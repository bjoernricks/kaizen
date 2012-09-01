# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# kaizen - Continuously improve, build and manage free software
#
# Copyright (C) 2011  Björn Ricks <bjoern.ricks@gmail.com>
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

import kaizen.logging

from kaizen.external.sqlalchemy import and_
from kaizen.db.db import Db
from kaizen.db.objects import File, Directory, RulesPhase, InstallDirectories
from kaizen.phase.phase import phases_list, DOWNLOADED, EXTRACTED, PATCHED, \
                            CONFIGURED, BUILT, DESTROOTED, ACTIVATED
from kaizen.phase.sequence import DOWNLOAD, EXTRACT, PATCH, CONFIGURE, BUILD, \
                               DESTROOT, ACTIVATE, DEACTIVATE, DELETE_SOURCE, \
                               DELETE_DOWNLOAD, DELETE_BUILD, DELETE_DESTROOT, \
                               UNPATCH, DISTCLEAN, SetSequence, UnSetSequence
from kaizen.rules.loader import RulesLoader
from kaizen.rules.error import RulesError
from kaizen.rules.validator import RulesValidator
from kaizen.utils import real_path, list_dir, list_subdir
from kaizen.utils.signals import Signal


class RulesHandler(object):

    def __init__(self, config, rules_name, dist_version=None, force=False):
        self.log = kaizen.logging.getLogger(self)
        self.config = config
        self.rules_name = rules_name
        self.force = force
        self.db = Db(config)
        self._rules_class = None
        self._rules = None

        self.install_directories = None

        if not dist_version:
            # if version is not provided use version from current rules
            self.rules_dist_version = self.rules_class.get_dist_version()
        else:
            self.rules_dist_version = dist_version
        self._init_directories()
        self._init_signals()
        self._init_sequences()
        self._load_install_directories()
        self._load_phases()

    @property
    def rules_class(self):
        if not self._rules_class:
            self._rules_class = self._load_rules()
        return self._rules_class

    @property
    def rules(self):
        if not self._rules:
            self._rules = self._init_rules()
        return self._rules

    def _load_rules(self):
        self.log.debug("Loading rules class")
        rules_loader = RulesLoader(self.config)
        rules = rules_loader.load(self.rules_name)
        if not rules:
            raise RulesError(self.rules_name,
                               "Could not load rules from '%s'" %
                               self.config.get("rules"))
        return rules

    def _init_rules(self):
        self.log.debug("Init rules %r" % self.rules_name)
        rules = self.rules_class
        validator = RulesValidator()
        if not validator.validate(rules):
            raise RulesError(self.rules_name,
                               "Loaded invalid rules from '%s'. Errors: %s" %
                               (self.config.get("rules"),
                               "\n".join(validator.errors)))
        return rules(self.config, self.src_dir, self.build_dir, self.dest_dir)

    def _load_install_directories(self):
        if self.install_directories:
            return
        query = self.db.session.query(InstallDirectories).filter(and_( \
                InstallDirectories.rules == self.rules_name,
                InstallDirectories.version == self.rules_dist_version))
        install_directories = query.first()
        if not install_directories:
            install_directories = InstallDirectories(self.rules_name,
                                                     self.rules_dist_version)
            self.db.session.add(install_directories)
            self.db.session.commit()
        self.install_directories = install_directories

    def _update_install_directories(self):
        self.db.session.add(self.install_directories)
        self.db.session.commit()

    def _init_directories(self):
        version = self.rules_dist_version
        name = self.rules_name
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

    def _init_sequences(self):
        self.sequences = dict()

        if self.rules_class.download_seq:
            seq = self.rules_class.download_seq
        else:
            seq = SetSequence(DOWNLOAD, None, DOWNLOADED)
        self.download_seq = seq
        self.sequences[seq.name] = seq

        if self.rules_class.extract_seq:
            seq = self.rules_class.extract_seq
        else:
            seq = SetSequence(EXTRACT, DOWNLOAD, EXTRACTED)
        self.extract_seq = seq
        self.sequences[seq.name] = seq

        if self.rules_class.patch_seq:
            seq = self.rules_class.patch_seq
        else:
            seq = SetSequence(PATCH, EXTRACT, PATCHED)
        self.patch_seq = seq
        self.sequences[seq.name] = seq

        if self.rules_class.configure_seq:
            seq = self.rules_class.configure_seq
        else:
            seq = SetSequence(CONFIGURE, PATCH, CONFIGURED)
        self.configure_seq = seq
        self.sequences[seq.name] = seq

        if self.rules_class.build_seq:
            seq = self.rules_class.build_seq
        else:
            seq = SetSequence(BUILD, CONFIGURE, BUILT)
        self.build_seq = seq
        self.sequences[seq.name] = seq

        if self.rules_class.destroot_seq:
            seq = self.rules_class.destroot_seq
        else:
            seq = SetSequence(DESTROOT, BUILD, DESTROOTED)
        self.destroot_seq = seq
        self.sequences[seq.name] = seq

        seq = SetSequence(ACTIVATE, DESTROOT, ACTIVATED)
        self.activate_seq = seq
        self.sequences[seq.name] = seq

        seq = UnSetSequence(DEACTIVATE, None, ACTIVATED)
        self.deactivate_seq = seq
        self.sequences[seq.name] = seq

        if self.rules_class.delete_destroot_seq:
            seq = self.rules_class.delete_destroot_seq
        else:
            seq = UnSetSequence(DELETE_DESTROOT, DEACTIVATE, DESTROOTED)
        self.delete_destroot_seq = seq
        self.sequences[seq.name] = seq

        if self.rules_class.delete_build_seq:
            seq = self.rules_class.delete_build_seq
        else:
            seq = UnSetSequence(DELETE_BUILD, DELETE_DESTROOT, BUILT)
        self.delete_build_seq = seq
        self.sequences[seq.name] = seq

        if self.rules_class.distclean_seq:
            seq = self.rules_class.distclean_seq
        else:
            seq = UnSetSequence(DISTCLEAN, DELETE_BUILD, CONFIGURED)
        self.distclean_seq = seq
        self.sequences[seq.name] = seq

        if self.rules_class.unpatch_seq:
            seq = self.rules_class.unpatch_seq
        else:
            seq = UnSetSequence(UNPATCH, DISTCLEAN, PATCHED)
        self.unpatch_seq = seq
        self.sequences[seq.name] = seq

        if self.rules_class.delete_source_seq:
            seq = self.rules_class.delete_source_seq
        else:
            seq = UnSetSequence(DELETE_SOURCE, UNPATCH, EXTRACTED)
        self.delete_source_seq = seq
        self.sequences[seq.name] = seq

        if self.rules_class.delete_download_seq:
            seq = self.rules_class.delete_download_seq
        else:
            seq = UnSetSequence(DELETE_DOWNLOAD, DELETE_SOURCE, DOWNLOADED)
        self.delete_download_seq = seq
        self.sequences[seq.name] = seq

        for name, seq in self.sequences.items():
            if seq.pre_sequence_name:
                pre_seq = self.sequences[seq.pre_sequence_name]
                seq.set_pre_sequence(pre_seq)
            if seq.post_sequence_name:
                post_seq = self.sequences[seq.post_sequence_name]
                seq.set_post_sequence(post_seq)

    def _groups_call(self, methodname):
        for group in self.rules._groups:
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
                                       File.rules != self.rules_name))
        if query.count():
            self.log.error("The following files are already installed by a " \
                           "different rules:")
            for file in query:
                self.log.error("Rules: '%s', Filename: '%s'" % (file.rules,
                                                                 file.filename))
                return

    def _load_phases(self):
        phases = self.db.session.query(RulesPhase).filter(
                                            and_(RulesPhase.rules ==
                                                 self.rules_name,
                                            RulesPhase.version ==
                                            self.rules_dist_version)
                                            ).all()
        self.phases = [phase.phase for phase in phases]

    def get_phases(self):
        return self.phases

    def set_phase(self, phase):
        rulesphase = RulesPhase(self.rules_name,
                                    self.rules_dist_version, phase)
        rulesphase = self.db.session.merge(rulesphase)
        self.db.session.commit()
        self._load_phases()

    def unset_phase(self, phase):
        if phase in self.phases:
            self.db.session.query(RulesPhase).filter(
                    and_(RulesPhase.rules == self.rules_name,
                    RulesPhase.version == self.rules_dist_version,
                    RulesPhase.phase == phase)).delete()
            self.db.session.commit()
            self._load_phases()

    def get_installed_files(self):
        query = self.db.session.query(File).filter(File.rules ==
                                                   self.rules_name)
        return query.all()

    def build_depends(self):
        from kaizen.rules.depend import DependencyAnalyser
        return DependencyAnalyser(self.config, self).analyse()

    def runtime_depends(self):
        from kaizen.rules.depend import RuntimeDependencyAnalyser
        return RuntimeDependencyAnalyser(self.config, self).analyse()

    def depends(self):
        return (self.build_depends(), self.runtime_depends())

    def patch(self):
        self.log.info("Patching rules %r" % self.rules_name)
        self._groups_call("pre_patch")
        self.rules.pre_patch()
        patchsys = self.rules.patch_cmd(self.rules.src_path,
                self.rules.patch_path, self.rules.patches,
                self.config.get("verbose"))
        patchsys.apply()
        self._groups_call("post_patch")
        self.rules.post_patch()

    def unpatch(self):
        self.log.info("Unpatching rules %r" % self.rules_name)
        patchsys = self.rules.patch_cmd(self.rules.src_path,
                self.rules.patch_path, self.rules.patches,
                self.config.get("verbose"))
        patchsys.unapply()

    def delete_destroot(self):
        self.log.info("Deleting destroot of rules %r" % self.rules_name)
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
        self.log.info("Deleting build of rules %r" % self.rules_name)
        build_dir = self.install_directories.build
        if build_dir and os.path.exists(build_dir):
            self.log.debug("Deleting build directory '%s'" % build_dir)
            shutil.rmtree(build_dir)

    def delete_source(self):
        self.log.info("Deleting source of rules %r" % self.rules_name)
        src_dir = self.install_directories.source
        if src_dir and os.path.exists(src_dir):
            self.log.debug("Deleting source directory '%s'" % src_dir)
            shutil.rmtree(src_dir)

    def delete_download(self):
        self.log.info("Delete download of rules %r" % self.rules_name)
        download = self.install_directories.download
        if download and os.path.exists(download):
            self.log.debug("Deleting download file '%s'" % download)
            os.remove(download)
        if os.path.exists(self.data_dir) and not os.listdir(self.data_dir):
            self.log.debug("Deleting download directory '%s'" % self.data_dir)
            os.rmdir(self.data_dir)

    def download(self):
        self.log.info("Download of rules %r" % self.rules_name)
        if not os.path.exists(self.data_dir):
            self.log.debug("Creating download directory %r" % self.data_dir)
            os.makedirs(self.data_dir)
        if self.rules.url and self.rules.download_cmd:
            self.log.info("Copying source file from '%s'." % self.rules.url)
            (archive_source, archive_dest) = self._get_download(self.rules.url,
                                                                self.data_dir)
            dl = self.rules.download_cmd(self.rules, archive_source)
            download_file = dl.copy(archive_dest, self.force)
            dl.verify(self.rules.hash)
            self.install_directories.download = real_path(download_file)
            self.db.session.add(self.install_directories)
            self.db.session.commit()

    def activate(self):
        self.log.info("Activation of rules %r" % self.rules_name)

        if self.is_activated():
            self.log.debug("Rules %r is already activated" % \
                           self.rules_name)
            return self.already_activated()

        current_dir = os.path.join(self.destroot_dir, "current")

        # lexists -> returns True also for broken links
        if os.path.lexists(current_dir):
            os.remove(current_dir)
        os.symlink(self.dest_dir, current_dir)

        (dirs, files) = list_subdir(self.dest_dir)
        # create necessary directories and run pre_activate
        # in pre_activate a rules may create directories, files, etc.
        for subdir in dirs:
            dir = os.path.join("/", subdir)
            if not os.path.exists(dir):
                os.makedirs(dir)
                self.log.debug("Creating directory '%s'" % dir)

        self.log.debug("Running pre-activate")
        self._groups_call("pre_activate")
        self.rules.pre_activate()

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
            dbdir = Directory(self.rules_name, dir)
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
            dbfile = File(file_path, self.rules_name)
            dbfile = self.db.session.merge(dbfile)
            self.db.session.add(dbfile)
        self.db.session.commit()
        self.log.debug("Running post-activate")
        self.rules.post_activate()
        self._groups_call("post_activate")

    def deactivate(self):
        self.log.info("Deactivation of rules %r" % self.rules_name)
        if not self.is_activated():
            self.log.warn("'%s' is not recognized as active but should be" \
                          " deactivated. Either deactivation was forced or"\
                          " the database may be currupted" % self.rules_name)

        self.log.debug("Running pre-deactivate")
        self._groups_call("pre_deactivate")
        self.rules.pre_deactivate()

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
        query = self.db.session.query(Directory).filter(Directory.rules ==
                                                        self.rules_name)
        for directory in query.all():
            dir = directory.directory
            if os.path.exists(dir) and not os.listdir(dir) and not \
                dir == self.config.get("prefix"):
                os.rmdir(dir)
                self.log.debug("Deleting directory '%s'" % dir)
            self.db.session.delete(directory)
        self.db.session.commit()

        self.log.debug("Running post-deactivate")
        self.rules.post_deactivate()
        self._groups_call("post_deactivate")

    def is_activated(self, exact=False):
        db = self.db.session
        if exact:
            query = db.query(RulesPhase).filter(and_(
                RulesPhase.rules == self.rules_name,
                RulesPhase.version == self.rules_dist_version,
                RulesPhase.phase ==
                phases_list.get("Activated")
                ))
        else:
            query = db.query(RulesPhase).filter(and_(
                RulesPhase.rules == self.rules_name,
                RulesPhase.phase ==
                phases_list.get("Activated")
                ))
        return query.count() > 0

    def configure(self):
        self.log.info("Configuration of rules %r" % self.rules_name)
        build_path = self.rules.build_path
        if not os.path.exists(build_path):
            self.log.debug("Creating build dir '%s'" % build_path)
            os.makedirs(build_path)
        self._groups_call("pre_configure")
        self.rules.pre_configure()
        self.rules.configure()
        self.rules.post_configure()
        self._groups_call("post_configure")

    def build(self):
        self.log.info("Build rules %r" % self.rules_name)
        self._groups_call("pre_build")
        self.rules.pre_build()
        self.rules.build()
        self.rules.post_build()
        self.install_directories.build = real_path(self.rules.build_path)
        self._update_install_directories()
        self._groups_call("post_build")

    def destroot(self):
        self.log.info("Destrooting rules %r" % self.rules_name)
        if not os.path.exists(self.dest_dir):
            self.log.debug("Creating destroot dir '%s'" % self.dest_dir)
            os.makedirs(self.dest_dir)
        self.install_directories.destroot = self.dest_dir
        self._update_install_directories()
        self._groups_call("pre_destroot")
        self.rules.pre_destroot()
        self.rules.destroot()
        self.rules.post_destroot()
        self._groups_call("post_destroot")

    def clean(self):
        self.log.info("Clean rules %r" % self.rules_name)
        self._groups_call("pre_clean")
        self.rules.pre_clean()
        self.rules.clean()
        self.rules.post_clean()
        self._groups_call("post_clean")

    def distclean(self):
        self.log.info("Distclean rules %r" % self.rules_name)
        self.rules.distclean()

    def extract(self):
        self.log.info("Extracting rules %r" % self.rules_name)
        if self.rules.extract_cmd:
            extractor = self.rules.extract_cmd(self.rules.url)
            extractor.extract(self.data_dir, self.src_dir)
        self.install_directories.source = real_path(self.rules.src_path)
        self._update_install_directories()

    def get_version(self):
        return self.rules_dist_version
