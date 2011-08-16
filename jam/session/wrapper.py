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

import jam.log

from jam.external.sqlalchemy import and_

from jam.utils import Loader, realpath, list_dir, list_subdir, extract_file
from jam.download import Downloader
from jam.phase.phase import Phases
from jam.db.db import Db
from jam.db.objects import Status
from jam.session.session import Session
from jam.session.error import SessionError
from jam.system.command import Patch

class SessionWrapper(object):

    def __init__(self, name, config, force=False):
        self.config = config
        self.session_name = name
        self.force = force
        self.session = None
        self.phases = Phases()
        self.log = jam.log.getLogger("jam.sessionwrapper")
        self.init_session()
        self.db = Db(config)
        self.init_status()
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
        version = session.version + "-" + session.revision
        self.version = version
        name = self.session_name
        build_cache = self.config.get("buildroot")
        download_cache = self.config.get("downloadroot")
        destroot = self.config.get("destroot")
        self.download_cache_dir = os.path.join(download_cache, name)
        self.cache_dir = os.path.join(build_cache, name, version)
        self.destroot_dir = os.path.join(destroot, name)
        self.data_dir = os.path.join(self.download_cache_dir, "data")
        self.patch_dir = os.path.join(self.download_cache_dir, "patches")
        self.src_dir = os.path.join(self.cache_dir, "source")
        self.build_dir = os.path.join(self.cache_dir, "build")
        self.dest_dir = os.path.join(self.destroot_dir, version)
        self.session = session(self.config, self.src_dir,
                                   self.build_dir, self.dest_dir)
        validator = SessionValidator()
        if not validator.validate(self.session):
            raise SessionError(self.session_name,
                               "Loaded invalid session from '%s'. Errors: %s" %
                               (self.config.get("sessions"),
                               "\n".join(validator.errors)))

    def init_status(self):
        self.status = self.db.session.query(Status).filter(
                                            and_(Status.session ==
                                                 self.session_name,
                                            Status.version == self.version)
                                            ).first()
        if not self.status:
            self.status = Status(self.session_name, self.version)
            self.set_phase(self.phases.get("None"))

    def set_phase(self, phase):
        self.status.set_phase(phase)
        self.db.session.add(self.status)
        self.db.session.commit()

    def get_current_phase(self):
        return self.status.phase

    def depends(self):
        self.log.debug("%s:phase:depends" % self.session_name)
        from jam.session.depend import DependencyAnalyser
        return DependencyAnalyser(self.config, self).analyse()

    def patch(self):
        self.log.debug("%s:phase:patch" % self.session_name)
        for patch in self.session.patches:
            patch_name = os.path.basename(patch)
            Patch(os.path.join(self.patch_dir, patch_name), self.session.src_path,
                               self.config.get("verbose")).run()

    def unpatch(self):
        self.log.debug("%s:phase:unpatch" % self.session_name)
        for patch in self.session.patches:
            patch_name = os.path.basename(patch)
            Patch(os.path.join(self.patch_dir, patch_name), self.src_path,
                               self.config.get("verbose"), True).run()

    def extract(self):
        self.log.debug("%s:phase:extract" % self.session_name)
        if not os.path.exists(self.src_dir):
            self.log.debug("Creating source dir '%s'" % self.src_dir)
            os.makedirs(self.src_dir)
        filename = os.path.basename(self.session.url)
        archive_file = os.path.join(self.data_dir, filename)
        if os.path.isfile(archive_file):
            self.log.info("Extract '%s' to '%s'" % (archive_file, self.src_dir))
            extract_file(archive_file, self.src_dir)
        else:
            self.log.info("Nothing to extract.")

    def download(self):
        self.log.debug("%s:phase:download" % self.session_name)
        if not os.path.exists(self.data_dir):
            self.log.debug("Creating data dir '%s'" % self.data_dir)
            os.makedirs(self.data_dir)
        if self.session.url:
            self.log.info("Copying source file from '%s'." % self.session.url)
            dl = Downloader(self.session.url) 
            download_file = dl.copy(self.data_dir, self.force)
            dl.verify(self.session.hash)
        if self.session.patches:
            if not os.path.exists(self.patch_dir):
                self.log.debug("Creating patch dir '%s'" % self.patch_dir)
                os.makedirs(self.patch_dir)
            for patch in self.session.patches:
                dl = Downloader(patch)
                dl.copy(self.patch_dir, self.force)

    def deactivate(self):
        self.log.debug("%s:phase:deactivate" % self.session_name)
        (dirs, files) = list_subdir(self.dest_dir, True)
        for file in files:
            file_path = os.path.join("/", file)
            if os.path.exists(file_path):
                self.log.debug("Deactivating '%s'" % file_path)
                os.remove(file_path)
        dirs.sort(reverse=True)
        for subdir in dirs:
            dir = os.path.join("/", subdir)
            if os.path.exists(dir) and not os.listdir(dir) and not \
                dir == self.config.get("prefix"):
                os.rmdir(dir)
                self.log.debug("Deleting directory '%s'" % dir)

    def activate(self):
        self.log.debug("%s:phase:activate" % self.session_name)
        (dirs, files) = list_subdir(self.dest_dir)
        current_dir = os.path.join(self.destroot_dir, "current")
        if os.path.exists(current_dir):
            os.remove(current_dir)
        os.symlink(self.dest_dir, current_dir)
        for subdir in dirs:
            dir = os.path.join("/", subdir)
            if not os.path.exists(dir):
                os.makedirs(dir)
                self.log.debug("Creating directory '%s'" % dir)
        for file in files:
            file_path = os.path.join("/", file)
            destdir_file_path = os.path.join(current_dir, file)
            self.log.debug("Activating '%s' from '%s'" % (file_path,
                           destdir_file_path))
            if os.path.exists(file_path):
                os.remove(file_path)
            os.symlink(destdir_file_path, file_path)

    def configure(self):
        self.log.debug("%s:phase:configure" % self.session_name)
        build_path = self.session.build_path
        if not os.path.exists(build_path):
            self.log.debug("Creating build dir '%s'" % build_path)
            os.makedirs(build_path)
        self.session.configure()

    def build(self):
        self.log.debug("%s:phase:build" % self.session_name)
        self.session.build()

    def destroot(self):
        self.log.debug("%s:phase:destroot" % self.session_name)
        if not os.path.exists(self.dest_dir):
            self.log.debug("Creating destroot dir '%s'" % self.dest_dir)
            os.makedirs(self.dest_dir)
        self.session.destroot()

    def clean(self):
        self.log.debug("%s:phase:clean" % self.session_name)
        self.session.clean()

    def distclean(self):
        self.log.debug("%s:phase:distclean" % self.session_name)
        self.session.distclean()


class SessionLoader(Loader):

    def __init__(self, config):
        self.config = config
        self.log = jam.log.getLogger("jam.sessionloader")
        path = realpath(self.config.get("sessions"))
        self.add_path(path)

    def sessions(self, modulename):
        module = self.module(modulename)
        if not module:
            return None 
        return self.classes(module, Session)

    def load(self, sessionname):
        sessionstring = sessionname + "." + sessionname
        sessions = self.sessions(sessionstring)
        if not sessions:
            self.log.warn("Could not load any session with name '%s'" %
                          sessionname)
            return None
        session = sessions[0]
        self.log.debug("Loaded session class '%s'" % session.__name__)
        return session


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
