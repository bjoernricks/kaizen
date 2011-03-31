# vim:fileencoding=utf-8:et::sw=4:ts=4:tw=80:

# jam - An advanced package manager for Free Software
#
# Copyright (C) 2011  Björn Ricks <bjoern.ricks@googlemail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
import sys
import inspect
import logging
import tarfile
import zipfile
import os.path

from jam.utils import realpath
from jam.buildsystem import Configure, CMake, Make
from jam.download import Downloader

class SessionError(Exception):

    def __init__(self, session_name, value):
        self.session_name = session_name
        self.value = value

    def __str__(self):
        return "Error in session '%s': %s" % (self.session_name, self.value)

class SessionConfig(object):

    def __init__(self, config={}):
        self.config = {}

        # set default values
        self.config["debug"] = False
        self.config["verbose"] = False
        self.config["jam_prefix"] = "/opt/local"

        self.config.update(config)
        prefix = self.get("jam_prefix")
        jam_dir = os.path.join(prefix, "jam")

        if not self.config.get("jam_download_cache", None):
            self.config["jam_download_cache"] =  os.path.join(jam_dir, "cache")
        if not self.config.get("jam_sessions", None):
            self.config["jam_sessions"] =  os.path.join(jam_dir, "session")
        if not self.config.get("jam_destroot", None):
            self.config["jam_destroot"] = os.path.join(jam_dir, "destroot")
        if not self.config.get("jam_build_cache", None):
            self.config["jam_build_cache"] = os.path.join(jam_dir, "cache")

    def get(self, value):
        # TODO: raise error if value not found
        return self.config[value]


class SessionManager(object):

    url = []
    patches = []

    def __init__(self, config, name, force=False):
        self.config = config
        self.force = force
        self.session_name = name
        self.session_loader = SessionLoader(config)
        self.session = self.session_loader.load(name + "." + name)
        # TODO: check session
        if not self.session:
            raise SessionError(self.session_name,
                               "Could not load session from '%s'" %
                               self.config.get("jam_sessions"))
        validator = SessionValidator()
        if not validator.validate(self.session):
            raise SessionError(self.session_name,
                               "Loaded invalid session from '%s'. Errors: %s" %
                               (self.config.get("jam_sessions"),
                               "\n".join(validator.errors)))
        self.session_instance = None
        self.download_file = None 
        self.log = logging.getLogger("jam.sessionmanager")

    def create_destroot_dir(self):
        name = self.session_name
        destroot_dir = os.path.join(self.config.get("jam_destroot"), name)
        if not os.path.exists(destroot_dir):
            os.makedirs(destroot_dir)
        self.log.debug("creating destroot dir in %s", destroot_dir)
        self.dest_dir = os.path.join(destroot_dir, self.session.version + "-"
                                 + self.session.revision)
        if not os.path.exists(self.dest_dir):
            self.log.debug("creating destroot dir %s", self.dest_dir)
            os.mkdir(self.dest_dir)

    def create_download_cache_dirs(self):
        name = self.session_name
        cache_dir = os.path.join(self.config.get("jam_download_cache"), name)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        self.log.debug("creating download cache dirs in %s", cache_dir)
        self.data_dir = os.path.join(cache_dir, "data")
        if not os.path.exists(self.data_dir):
            self.log.debug("creating download cache datadir in %s", self.data_dir)
            os.mkdir(self.data_dir)
        self.patch_dir = os.path.join(cache_dir, "patches")
        if not os.path.exists(self.patch_dir):
            self.log.debug("creating download cache patchdir in %s", self.patch_dir)
            os.mkdir(self.patch_dir)

    def create_build_cache_dirs(self):
        name = self.session_name
        cache_dir = os.path.join(self.config.get("jam_build_cache"), name,
                                 self.session.version + "-" + self.session.revision)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        self.log.debug("creating build cache dirs in %s", cache_dir)
        self.src_dir = os.path.join(cache_dir, "source")
        if not os.path.exists(self.src_dir):
            self.log.debug("creating build cache sourcedir %s", self.src_dir)
            os.mkdir(self.src_dir)
        self.build_dir = os.path.join(cache_dir, "build")
        if not os.path.exists(self.build_dir):
            self.log.debug("creating build cache buildir %s", self.build_dir)
            os.mkdir(self.build_dir)

    def get_session_instance(self):
        if not self.session_instance:
            self.session_instance = self.session(self.config, self.src_dir,
                                                 self.build_dir, self.dest_dir)
        return self.session_instance
    
    def extract_file(self, file_name, dest_dir):
        if not os.path.isfile(file_name):
            self.log.error("Unable to extract file. '%s' is does not exit or \
                            is not a file." % file_name)
            return
        if tarfile.is_tarfile(file_name):
            self.log.debug("Extracting tar file '%s' to '%s'" %
                          (file_name, dest_dir))
            file = tarfile.open(file_name)
            file.extractall(dest_dir)
        elif zipfile.is_zipfile(file_name):
            self.log.debug("Extracting zip file '%s' to '%s'" %
                          (file_name, dest_dir))
            file = zipfile.ZipFile(file_name)
            file.extractall(dest_fir)

    def download(self):
        self.log.info("%s: download", self.session_name)
        self.create_download_cache_dirs()

        if self.session.url:
            self.log.info("Copying source file from '%s'." % self.session.url)
            dl = Downloader(self.session.url) 
            self.download_file = dl.copy(self.data_dir, self.force)
            dl.verify(self.session.hash)
        for patch in self.patches:
            dl = Downloader(patch)
            dl.copy(self.patch_dir)

    def extract(self):
        self.download()
        self.log.info("%s: extract", self.session_name)
        # TODO: create directories in their phases
        self.create_build_cache_dirs()
        self.create_destroot_dir()
        if self.download_file:
            self.extract_file(self.download_file, self.src_dir)
        else:
            self.log.info("Nothing to extract.")

    def archive(self):
        self.log.info("%s: archive", self.session_name)

    def configure(self):
        self.patch()
        self.log.info("%s: configure", self.session_name)
        self.get_session_instance().configure()

    def build(self):
        self.configure()
        self.log.info("%s: build", self.session_name)
        self.get_session_instance().build()

    def destroot(self):
        self.build()
        self.log.info("%s: destroot", self.session_name)
        #self.create_destroot_dir()
        self.get_session_instance().destroot()

    def install(self):
        self.log.info("%s: install", self.session_name)

    def uninstall(self):
        self.log.info("%s: uninstall", self.session_name)

    def activate(self):
        self.log.info("%s: activate", self.session_name)

    def deactivate(self):
        self.log.info("%s: deactivate", self.session_name)

    def patch(self):
        self.extract()
        self.log.info("%s: patch", self.session_name)

    def unpatch(self):
        self.log.info("%s: unpatch", self.session_name)


class Session(object):
    
    depends = []
    url = []
    patches = []
    version = ""
    revision = "0"
    hash = {}
    args = []
    name = ""
    src_path = None

    def __init__(self, config, src_dir, build_dir, dest_dir):
        self.config = config
        self.build_dir = build_dir
        if self.src_path is None:
            self.src_path = self.name + "-" + self.version
        self.src_dir = os.path.join(src_dir, self.src_path)
        self.dest_dir = dest_dir

    def configure(self):
        pass

    def build(self):
        pass

    def destroot(self):
        pass


class MakeSession(Session):

    def build(self):
        Make(self.build_dir, self.config.get("debug")).run()

    def destroot(self):
        Make(self.build_dir, self.config.get("debug")).install(self.dest_dir)


class ConfigureSession(MakeSession):

    def configure(self):
        self.args.append("--prefix=" + self.config.get("jam_prefix"))
        Configure(self.args, self.src_dir, self.build_dir,
                  self.config.get("debug")).run()


class CMakeSession(MakeSession):

    def configure(self):
        self.args.append("-DCMAKE_INSTALL_PREFIX=" + self.config.get("jam_prefix"))
        self.args.append("-DCMAKE_COLOR_MAKEFILE=TRUE")
        if self.config.get("verbose"):
            self.args.append("-DCMAKE_VERBOSE_MAKEFILE=TRUE")
        CMake(self.args, self.src_dir, self_builddir,
              self.config.get("debug")).run()


class SessionLoader(object):

    def __init__(self, config):
        self.config = config
        self.log = logging.getLogger("jam.sessionloader")
        self.add_path()

    def add_path(self):
        path = realpath(self.config.get("jam_sessions"))
        if not path in sys.path:
            sys.path.append(path)

    def module(self, name):
        try:
            return __import__(name, globals(), locals(), ['*'])
        except ImportError as error:
            self.log.warn("Could not import module '%s'. %s", name, error)
            return None

    def classes(self, modulename, parentclass=None):
        classes = []
        module = self.module(modulename)
        if not module:
            return classes
        self.log.debug("Imported module '%s'", module)
        for key, value in module.__dict__.items():
            if inspect.isclass(value):
                if parentclass:
                    if not issubclass(value, parentclass):
                        continue
                self.log.debug("Found class '%s'", value)
                classes.append(value)
        return classes

    def sessions(self, module):
        return self.classes(module, Session)

    def load(self, sessionname):
        sessions = self.sessions(sessionname)
        if not sessions:
            self.log.warning("Could not load any session with name '%s'",
                             sessionname)
            return None
        session = sessions[0]
        self.log.info("Loaded session '%s'", session.__name__)
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
        except AttributeError as error:
            self.errors.append("Session '%s' has no attribute version." %
                               session.__name__)
        try:
            if not session.name:
                valid = False
                self.errors.append("Session '%s' name not set." %
                                   session.__name__)
        except AttributeError as error:
            self.errors.append("Session '%s' has not attribute name." %
                               session.__name__)

        return valid
