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

import os
import tarfile
import zipfile
import os.path
import shutil

import jam.logging

from jam.external.sqlalchemy import and_

from jam.utils import real_path, list_dir, list_subdir, extract_file
from jam.download import UrlDownloader
from jam.phase.phase import phases_list
from jam.db.db import Db
from jam.db.objects import File, Directory, SessionPhase, InstallDirectories
from jam.session.session import Session
from jam.session.loader import SessionLoader
from jam.session.error import SessionError
from jam.system.command import Patch

class SessionWrapper(object):

    def __init__(self, name, config, force=False):
        self.config = config
        self.session_name = name
        self.force = force
        self.session = None
        self.log = jam.logging.getLogger(self)
        self.init_session()
        self.db = Db(config)
        self.load_phases()
        self.load_install_directories()
        self.session.init()

    def load_session(self):
        session_loader = SessionLoader(self.config)
        session = session_loader.load(self.session_name)
        if not session:
            raise SessionError(self.session_name,
                               "Could not load session from '%s'" %
                               self.config.get("sessions"))
        return session

    def init_session(self):
        session = self.load_session()
        # calculate version for directries
        version = session.version + "-" + session.revision
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
        self.session = session(self.config, self.src_dir, self.build_dir,
                               self.dest_dir)
        validator = SessionValidator()
        if not validator.validate(self.session):
            raise SessionError(self.session_name,
                               "Loaded invalid session from '%s'. Errors: %s" %
                               (self.config.get("sessions"),
                               "\n".join(validator.errors)))

    def load_phases(self):
        phases = self.db.session.query(SessionPhase).filter(
                                            and_(SessionPhase.session ==
                                                 self.session_name,
                                            SessionPhase.version ==
                                            self.session.get_dist_version())
                                            ).all()
        self.phases = [phase.phase for phase in phases]

    def get_phases(self):
        return self.phases

    def set_phase(self, phase):
        sessionphase = SessionPhase(self.session_name,
                                    self.session.get_dist_version(), phase)
        sessionphase = self.db.session.merge(sessionphase)
        self.db.session.commit()
        self.load_phases()

    def unset_phase(self, phase):
        if phase in self.phases:
            self.db.session.query(SessionPhase).filter(
                    and_(SessionPhase.session == self.session_name,
                    SessionPhase.version == self.session.get_dist_version(),
                    SessionPhase.phase == phase)).delete()
            self.db.session.commit()
            self.load_phases()

    def load_install_directories(self):
        session = self.session
        install_directories = InstallDirectories(self.session_name,
                                                 session.get_dist_version())
        install_directories = self.db.session.merge(install_directories)
        install_directories.build = real_path(session.build_path)
        install_directories.source = real_path(session.src_path)
        install_directories.destroot = real_path(session.destroot_path)
        self.db.session.add(install_directories)
        self.db.session.commit()
        self.install_directories = install_directories

    def build_depends(self):
        from jam.session.depend import DependencyAnalyser
        return DependencyAnalyser(self.config, self).analyse()

    def runtime_depends(self):
        from jam.session.depend import RuntimeDependencyAnalyser
        return RuntimeDependencyAnalyser(self.config, self).analyse()

    def depends(self):
        return (self.build_depends(), self.runtime_depends())

    def patch(self):
        self.log.info("%s:phase:patch" % self.session_name)
        self.groups_call("pre_patch")
        self.session.pre_patch()
        patchsys = self.session.patchsystem(self.session.src_path,
                self.session.patch_path, self.session.patches,
                self.config.get("verbose"))
        patchsys.apply()
        self.groups_call("post_patch")
        self.session.post_patch()

    def unpatch(self):
        self.log.info("%s:phase:unpatch" % self.session_name)
        patchsys = self.session.patchsystem(self.session.src_path,
                self.session.patch_path, self.session.patches,
                self.config.get("verbose"))
        patchsys.unapply()

    def extract(self):
        self.log.info("%s:phase:extract" % self.session_name)
        if not os.path.exists(self.src_dir):
            self.log.debug("Creating source dir '%s'" % self.src_dir)
            os.makedirs(self.src_dir)
        filename = self.get_download_file(self.session.url)
        archive_file = os.path.join(self.data_dir, filename)
        if os.path.isfile(archive_file):
            self.log.info("Extract '%s' to '%s'" % (archive_file, self.src_dir))
            extract_file(archive_file, self.src_dir)
        else:
            # TODO raise error
            self.log.error("Nothing to extract. Could not find file '%s'" %
                           archive_file)

    def get_download_file(self, file):
        if isinstance(file, list):
            return file[1]
        else:
            return os.path.basename(file)

    def get_download(self, file, dir):
        if isinstance(file, list):
            file_source = file[0]
            file_dest = os.path.join(dir, file[1])
        else:
            file_source = file
            file_dest = dir
        return file_source, file_dest

    def download(self):
        self.log.info("%s:phase:download" % self.session_name)
        if not os.path.exists(self.data_dir):
            self.log.debug("Creating data dir '%s'" % self.data_dir)
            os.makedirs(self.data_dir)
        if self.session.url and self.session.download:
            self.log.info("Copying source file from '%s'." % self.session.url)
            (archive_source, archive_dest) = self.get_download(self.session.url,
                                                self.data_dir)
            dl = self.session.download(archive_source,
                                       self.session.session_path)
            download_file = dl.copy(archive_dest, self.force)
            dl.verify(self.session.hash)
            self.install_directories.download = real_path(download_file)
            self.db.session.add(self.install_directories)
            self.db.commit()

    def deactivate(self):
        self.log.info("%s:phase:deactivate" % self.session_name)
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

        self.groups_call("pre_deactivate")
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
        self.groups_call("post_deactivate")

    def check_files_installed(self, files):
        query = self.db.session.query(File).filter(and_(File.filename.in_(
                                      [x for (x, y) in files]),
                                       File.session != self.session_name))
        if query.count():
            self.log.error("The following files are already installed by a " \
                           "different session:")
            for file in query:
                self.log.error("Session: '%s', Filename: '%s'" % (file.session,
                                                                 file.filename))
                # FIXME: raise error
                return

    def activate(self):
        self.log.info("%s:phase:activate" % self.session_name)
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

        self.groups_call("pre_activate")
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
                self.check_files_installed(check_files)
                activate_files.extend(check_files)
                check_files = []

        if check_files:
            self.check_files_installed(check_files)
            activate_files.extend(check_files)

        # check if session is already installed
        query = self.db.session.query(SessionPhase).filter(and_(
                                      SessionPhase.session == self.session_name,
                                      SessionPhase.phase ==
                                      phases_list.get("Activated")
                                     ))
        # deactivate same session if already installed
        if query.count():
            self.deactivate()

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
        self.groups_call("post_activate")

    def configure(self):
        self.log.info("%s:phase:configure" % self.session_name)
        build_path = self.session.build_path
        if not os.path.exists(build_path):
            self.log.debug("Creating build dir '%s'" % build_path)
            os.makedirs(build_path)
        self.groups_call("pre_configure")
        self.session.pre_configure()
        self.session.configure()
        self.session.post_configure()
        self.groups_call("post_configure")

    def build(self):
        self.log.info("%s:phase:build" % self.session_name)
        self.groups_call("pre_build")
        self.session.pre_build()
        self.session.build()
        self.session.post_build()
        self.groups_call("post_build")

    def destroot(self):
        self.log.info("%s:phase:destroot" % self.session_name)
        if not os.path.exists(self.dest_dir):
            self.log.debug("Creating destroot dir '%s'" % self.dest_dir)
            os.makedirs(self.dest_dir)
        self.groups_call("pre_destroot")
        self.session.pre_destroot()
        self.session.destroot()
        self.session.post_destroot()
        self.groups_call("post_destroot")

    def clean(self):
        self.log.info("%s:phase:clean" % self.session_name)
        self.groups_call("pre_clean")
        self.session.pre_clean()
        self.session.clean()
        self.session.post_clean()
        self.groups_call("post_clean")

    def distclean(self):
        self.log.info("%s:phase:distclean" % self.session_name)
        self.session.distclean()

    def delete_destroot(self):
        self.log.info("%s:phase:delete-destroot" % self.session_name)
        dest_dir = self.install_directories.destroot
        if os.path.exists(dest_dir):
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
        self.log.info("%s:phase:delete-build" % self.session_name)
        build_dir = self.install_directories.build
        if os.path.exists(build_dir):
            self.log.debug("Deleting build directory '%s'" % build_dir)
            shutil.rmtree(build_dir)

    def delete_source(self):
        self.log.info("%s:phase:delete-source" % self.session_name)
        src_dir = self.install_directories.source
        if os.path.exists(src_dir):
            self.log.debug("Deleting source directory '%s'" % src_dir)
            shutil.rmtree(src_dir)

    def delete_download(self):
        self.log.info("%s:phase:delete-download" % self.session_name)
        download = self.install_directories.download
        if os.path.exists(download):
            self.log.debug("Deleting download file '%s'" % download)
            os.remove(download)

    def get_installed_files(self):
        query = self.db.session.query(File).filter(File.session ==
                                                    self.session_name)
        return query.all()

    def get_version(self):
        return self.session.get_dist_version()

    def groups_call(self, methodname):
        for group in self.session._groups:
            method = getattr(group, methodname)
            method()


class SessionValidator(object):

    errors = []

    def validate(self, session):
        valid = True
        try:
            if not session.version:
                valid = False
                self.errors.append("Session '%s' version not set." %
                                   session.__name__)
        except AttributeError, error:
            self.errors.append("Session '%s' has no attribute version." %
                               session.__name__)
        try:
            if not session.name:
                valid = False
                self.errors.append("Session '%s' name not set." %
                                   session.__name__)
        except AttributeError, error:
            self.errors.append("Session '%s' has not attribute name." %
                               session.__name__)

        return valid
