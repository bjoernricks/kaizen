# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# jam - An advanced package manager for Free Software
#
# Copyright (C) 2011  Björn Ricks <bjoern.ricks@googlemail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 
# 02110-1301 USA

import os.path
import shutil

import jam.logging

from jam.external.sqlalchemy import and_
from jam.db.db import Db
from jam.db.objects import File, Directory, SessionPhase, InstallDirectories
from jam.phase.phase import phases_list
from jam.session.loader import SessionLoader
from jam.session.error import SessionError
from jam.session.validator import SessionValidator
from jam.utils import real_path, list_dir, list_subdir
from jam.utils.signals import Signal


class SessionHandler(object):

    def __init__(self, config, session_name, dist_version=None, force=False):
        self.log = jam.logging.getLogger(self)
        self.config = config
        self.session_name = session_name
        self.force = force
        self.db = Db(config)
        self._session_class = None
        self._session = None

        self.install_directories = None

        if not dist_version:
            # if version is not provided use version from current session
            self.session_dist_version = self.session_class.get_dist_version()
        else:
            self.session_dist_version = dist_version
        self._init_directories()
        self._init_signals()
        self._load_install_directories()
        self._load_phases()

    @property
    def session_class(self):
        if not self._session_class:
            self._session_class = self._load_session()
        return self._session_class

    @property
    def session(self):
        if not self._session:
            self._session = self._init_session()
        return self._session

    def _load_session(self):
        self.log.debug("Loading session class")
        session_loader = SessionLoader(self.config)
        session = session_loader.load(self.session_name)
        if not session:
            raise SessionError(self.session_name,
                               "Could not load session from '%s'" %
                               self.config.get("sessions"))
        return session

    def _init_session(self):
        self.log.debug("Init session %r" % self.session_name)
        session = self.session_class
        validator = SessionValidator()
        if not validator.validate(session):
            raise SessionError(self.session_name,
                               "Loaded invalid session from '%s'. Errors: %s" %
                               (self.config.get("sessions"),
                               "\n".join(validator.errors)))
        return session(self.config, self.src_dir, self.build_dir, self.dest_dir)

    def _load_install_directories(self):
        if self.install_directories:
            return
        query = self.db.session.query(InstallDirectories).filter(and_( \
                InstallDirectories.session == self.session_name,
                InstallDirectories.version == self.session_dist_version))
        install_directories = query.first()
        if not install_directories:
            install_directories = InstallDirectories(self.session_name,
                                                     self.session_dist_version)
            self.db.session.add(install_directories)
            self.db.session.commit()
        self.install_directories = install_directories

    def _update_install_directories(self):
        self.db.session.add(self.install_directories)
        self.db.session.commit()

    def _init_directories(self):
        version = self.session_dist_version
        name = self.session_name
        build_cache = self.config.get("buildroot")
        download_cache = self.config.get("downloadroot")
        destroot = self.config.get("destroot")
        self.download_cache_dir = os.path.join(download_cache, name)
        self.cache_dir = os.path.join(build_cache, name, version)
        self.destroot_dir = os.path.join(destroot, name)
        self.data_dir = os.path.join(self.download_cache_dir, "data")
        self.src_dir = os.path.join(self.cache_dir, "source")
        self.build_dir = os.path.join(self.cache_dir, "build")
        self.dest_dir = os.path.join(self.destroot_dir, version)

    def _init_signals(self):
        self.already_activated = Signal()

    def _groups_call(self, methodname):
        for group in self.session._groups:
            method = getattr(group, methodname)
            method()

    def _get_download(self, file, dir):
        if isinstance(file, list):
            file_source = file[0]
            file_dest = os.path.join(dir, file[1])
        else:
            file_source = file
            file_dest = dir
        return file_source, file_dest

    def _check_installed_files(self, files):
        query = self.db.session.query(File).filter(and_(File.filename.in_(
                                      [x for (x, y) in files]),
                                       File.session != self.session_name))
        if query.count():
            self.log.error("The following files are already installed by a " \
                           "different session:")
            for file in query:
                self.log.error("Session: '%s', Filename: '%s'" % (file.session,
                                                                 file.filename))
                return

    def _load_phases(self):
        phases = self.db.session.query(SessionPhase).filter(
                                            and_(SessionPhase.session ==
                                                 self.session_name,
                                            SessionPhase.version ==
                                            self.session_dist_version)
                                            ).all()
        self.phases = [phase.phase for phase in phases]

    def get_phases(self):
        return self.phases

    def set_phase(self, phase):
        sessionphase = SessionPhase(self.session_name,
                                    self.session_dist_version, phase)
        sessionphase = self.db.session.merge(sessionphase)
        self.db.session.commit()
        self._load_phases()

    def unset_phase(self, phase):
        if phase in self.phases:
            self.db.session.query(SessionPhase).filter(
                    and_(SessionPhase.session == self.session_name,
                    SessionPhase.version == self.session_dist_version,
                    SessionPhase.phase == phase)).delete()
            self.db.session.commit()
            self._load_phases()

    def get_installed_files(self):
        query = self.db.session.query(File).filter(File.session ==
                                                   self.session_name)
        return query.all()

    def build_depends(self):
        from jam.session.depend import DependencyAnalyser
        return DependencyAnalyser(self.config, self).analyse()

    def runtime_depends(self):
        from jam.session.depend import RuntimeDependencyAnalyser
        return RuntimeDependencyAnalyser(self.config, self).analyse()

    def depends(self):
        return (self.build_depends(), self.runtime_depends())

    def patch(self):
        self.log.info("Patching session %r" % self.session_name)
        self._groups_call("pre_patch")
        self.session.pre_patch()
        patchsys = self.session.patchsystem(self.session.src_path,
                self.session.patch_path, self.session.patches,
                self.config.get("verbose"))
        patchsys.apply()
        self._groups_call("post_patch")
        self.session.post_patch()

    def unpatch(self):
        self.log.info("Unpatching session %r" % self.session_name)
        patchsys = self.session.patchsystem(self.session.src_path,
                self.session.patch_path, self.session.patches,
                self.config.get("verbose"))
        patchsys.unapply()

    def delete_destroot(self):
        self.log.info("Deleting destroot of session %r" % self.session_name)
        dest_dir = self.install_directories.destroot
        if dest_dir and os.path.exists(dest_dir):
            self.log.debug("Deleting destroot directory '%s'" % dest_dir)
            shutil.rmtree(dest_dir)

        current_dir = os.path.join(self.destroot_dir, "current")
        if not os.path.exists(current_dir) and os.path.islink(current_dir):
            os.remove(current_dir)
        #if os.path.exists(self.destroot_dir) and not \
        #        os.listdir(self.destroot_dir) \
        #        and not self.destroot_dir == self.config.get("prefix"):
        #    os.remove(self.destroot_dir)

    def delete_build(self):
        self.log.info("Deleting build of session %r" % self.session_name)
        build_dir = self.install_directories.build
        if build_dir and os.path.exists(build_dir):
            self.log.debug("Deleting build directory '%s'" % build_dir)
            shutil.rmtree(build_dir)

    def delete_source(self):
        self.log.info("Deleting source of session %r" % self.session_name)
        src_dir = self.install_directories.source
        if src_dir and os.path.exists(src_dir):
            self.log.debug("Deleting source directory '%s'" % src_dir)
            shutil.rmtree(src_dir)

    def delete_download(self):
        self.log.info("Delete download of session %r" % self.session_name)
        download = self.install_directories.download
        if download and os.path.exists(download):
            self.log.debug("Deleting download file '%s'" % download)
            os.remove(download)
        if os.path.exists(self.data_dir) and not os.listdir(self.data_dir):
            self.log.debug("Deleting download directory '%s'" % self.data_dir)
            os.rmdir(self.data_dir)

    def download(self):
        self.log.info("Download of session %r" % self.session_name)
        if not os.path.exists(self.data_dir):
            self.log.debug("Creating download directory %r" % self.data_dir)
            os.makedirs(self.data_dir)
        if self.session.url and self.session.download:
            self.log.info("Copying source file from '%s'." % self.session.url)
            (archive_source, archive_dest) = self._get_download(self.session.url,
                                                                self.data_dir)
            dl = self.session.download(archive_source, self.session.session_path)
            download_file = dl.copy(archive_dest, self.force)
            dl.verify(self.session.hash)
            self.install_directories.download = real_path(download_file)
            self.db.session.add(self.install_directories)
            self.db.session.commit()

    def activate(self):
        self.log.info("Activation of session %r" % self.session_name)

        # deactivate same session if already installed
        #TODO maybe this case should be handled by the manager
        if self.is_activated():
            self.log.info("Deactivating already installed version of "
                          "session %r" % self.session_name)
            self.deactivate()

        current_dir = os.path.join(self.destroot_dir, "current")

        # lexists -> returns True also for broken links
        if os.path.lexists(current_dir):
            os.remove(current_dir)
        os.symlink(self.dest_dir, current_dir)

        (dirs, files) = list_subdir(self.dest_dir)
        # create necessary directories and run pre_activate
        # in pre_activate a session may create directories, files, etc.
        for subdir in dirs:
            dir = os.path.join("/", subdir)
            if not os.path.exists(dir):
                os.makedirs(dir)
                self.log.debug("Creating directory '%s'" % dir)

        self._groups_call("pre_activate")
        self.session.pre_activate()

        (dirs, files) = list_subdir(self.dest_dir)
        activate_files = []
        check_files = []
        i = 0
        for file in files:
            file_path = os.path.join("/", file)
            destdir_file_path = os.path.join(current_dir, file)
            check_files.append((file_path, destdir_file_path))
            # sqlite has a limit for max variables in a sql query
            # therefore split this up in several queries
            i += 1
            if i > 100:
                i = 0
                self._check_installed_files(check_files)
                activate_files.extend(check_files)
                check_files = []

        if check_files:
            self._check_installed_files(check_files)
            activate_files.extend(check_files)

        # record created directories in db
        for subdir in dirs:
            dir = os.path.join("/", subdir)
            dbdir = Directory(self.session_name, dir)
            dbdir = self.db.session.merge(dbdir)
            self.db.session.add(dbdir)
        self.db.session.commit()

        # create symlinks and record installed files in db
        for (file_path, destdir_file_path) in activate_files:
            self.log.debug("Activating '%s' from '%s'" % (file_path,
                           destdir_file_path))
            if os.path.lexists(file_path):
                os.remove(file_path)
            os.symlink(destdir_file_path, file_path)
            dbfile = File(file_path, self.session_name)
            dbfile = self.db.session.merge(dbfile)
            self.db.session.add(dbfile)
        self.db.session.commit()
        self.session.post_activate()
        self._groups_call("post_activate")

    def deactivate(self):
        self.log.info("Deactivation of session %r" % self.session_name)
        installed = self.db.session.query(SessionPhase).filter(
                                     and_(
                                     SessionPhase.session == self.session_name,
                                     SessionPhase.phase ==
                                     phases_list.get("Activated"))
                                     ).first()
        if not installed:
            self.log.warn("'%s' is not recognized as active but should be" \
                          " deactivated. Either deactivation was forced or"\
                          " the database may be currupted" % self.session_name)

        self._groups_call("pre_deactivate")
        self.session.pre_deactivate()

        # delete activated files
        for file in self.get_installed_files():
            file_path = file.filename
            if os.path.lexists(file_path):
                self.log.debug("Deactivating '%s'" % file_path)
                os.remove(file_path)
            else:
                self.log.warn("File '%s' couldn't be deactivated because it "\
                              "doesn't exist anymore" % file_path)
            self.db.session.delete(file)
        self.db.session.commit()

        # delete empty directories
        query = self.db.session.query(Directory).filter(Directory.session ==
                                                        self.session_name)
        for directory in query.all():
            dir = directory.directory
            if os.path.exists(dir) and not os.listdir(dir) and not \
                dir == self.config.get("prefix"):
                os.rmdir(dir)
                self.log.debug("Deleting directory '%s'" % dir)
            self.db.session.delete(directory)
        self.db.session.commit()

        self.session.post_deactivate()
        self._groups_call("post_deactivate")

    def is_activated(self, exact=False):
        db = self.db.session
        if exact:
            query = db.query(SessionPhase).filter(and_(
                SessionPhase.session == self.session_name,
                SessionPhase.version == self.session_dist_version,
                SessionPhase.phase ==
                phases_list.get("Activated")
                ))
        else:
            query = db.query(SessionPhase).filter(and_(
                SessionPhase.session == self.session_name,
                SessionPhase.phase ==
                phases_list.get("Activated")
                ))
        return query.count() > 0

    def configure(self):
        self.log.info("Configuration of session %r" % self.session_name)
        build_path = self.session.build_path
        if not os.path.exists(build_path):
            self.log.debug("Creating build dir '%s'" % build_path)
            os.makedirs(build_path)
        self._groups_call("pre_configure")
        self.session.pre_configure()
        self.session.configure()
        self.session.post_configure()
        self._groups_call("post_configure")

    def build(self):
        self.log.info("Build session %r" % self.session_name)
        self._groups_call("pre_build")
        self.session.pre_build()
        self.session.build()
        self.session.post_build()
        self.install_directories.build = real_path(self.session.build_path)
        self._update_install_directories()
        self._groups_call("post_build")

    def destroot(self):
        self.log.info("Destrooting session %r" % self.session_name)
        if not os.path.exists(self.dest_dir):
            self.log.debug("Creating destroot dir '%s'" % self.dest_dir)
            os.makedirs(self.dest_dir)
        self.install_directories.destroot = self.dest_dir
        self._update_install_directories()
        self._groups_call("pre_destroot")
        self.session.pre_destroot()
        self.session.destroot()
        self.session.post_destroot()
        self._groups_call("post_destroot")

    def clean(self):
        self.log.info("Clean session %r" % self.session_name)
        self._groups_call("pre_clean")
        self.session.pre_clean()
        self.session.clean()
        self.session.post_clean()
        self._groups_call("post_clean")

    def distclean(self):
        self.log.info("Distclean session %r" % self.session_name)
        self.session.distclean()

    def extract(self):
        self.log.info("Extracting session %r" % self.session_name)
        extractor = self.session.extract(self.session.url)
        extractor.extract(self.data_dir, self.src_dir)
        self.install_directories.source = real_path(self.session.src_path)
        self._update_install_directories()

    def get_version(self):
        return self.session_dist_version
