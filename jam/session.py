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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import os
import sys
import inspect
import tarfile
import zipfile
import os.path

import jam.log

from jam.utils import realpath, list_dir, list_subdir
from jam.command import Configure, CMake, Make
from jam.download import Downloader
from jam.depend import DependencyAnalyser

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
        self.log = jam.log.getLogger("jam.sessionmanager")
        self.session_wrapper = SessionWrapper(name, config, force)
        self.init()

    def init(self):
        self.log.normal("%s:phase:init" % self.session_name)

    def download(self):
        self.log.normal("%s:phase:download" % self.session_name)
        self.session_wrapper.download()

    def extract(self):
        self.log.normal("%s:phase:extract" % self.session_name)
        self.session_wrapper.extract()

    def archive(self):
        self.log.normal("%s:phase:archive" % self.session_name)

    def configure(self):
        self.log.normal("%s:phase:configure" % self.session_name)
        self.session_wrapper.configure()

    def build(self):
        self.log.normal("%s:phase:build" % self.session_name)
        self.session_wrapper.build()

    def destroot(self):
        self.log.normal("%s:phase:destroot" % self.session_name)
        self.session_wrapper.destroot()

    def install(self):
        self.log.normal("%s:running install" % self.session_name)
        self.download()
        self.extract()
        self.patch()
        self.configure()
        self.build()
        self.destroot()
        self.activate()

    def uninstall(self):
        self.log.normal("%s:phase:uninstall" % self.session_name)

    def activate(self):
        self.log.normal("%s:phase:activate" % self.session_name)
        (dirs, files) = list_subdir(self.session_wrapper.dest_dir)
        for subdir in dirs:
            dir = os.path.join("/", subdir)
            if not os.path.exists(dir):
                os.makedirs(dir)
                self.log.debug("Creating directory '%s'" % dir)
        for file in files:
            file_path = os.path.join("/", file)
            destdir_file_path = os.path.join(self.session_wrapper.dest_dir, file)
            if not os.path.exists(file_path):
                self.log.debug("Activating '%s' from '%s'" % (file_path,
                                destdir_file_path))
                os.symlink(destdir_file_path, file_path)

    def deactivate(self):
        self.log.normal("%s:phase:deactivate" % self.session_name)
        (dirs, files) = list_subdir(self.session_wrapper.dest_dir, True)
        for file in files:
            file_path = os.path.join("/", file)
            if os.path.exists(file_path):
                self.log.debug("Deactivating '%s'" % file_path)
                os.remove(file_path)
        dirs.sort(reverse=True)
        for subdir in dirs:
            dir = os.path.join("/", subdir)
            if os.path.exists(dir) and not os.listdir(dir):
                os.rmdir(dir)
                self.log.debug("Deleting directory '%s'" % dir)

    def patch(self):
        self.log.normal("%s:phase:patch" % self.session_name)

    def unpatch(self):
        self.log.normal("%s:phase:unpatch" % self.session_name)

    def clean(self):
        self.log.normal("%s:phase:clean" % self.session_name)
        self.session_wrapper.clean()

    def distclean(self):
        self.log.normal("%s:phase:distclean" % self.session_name)
        self.log.normal(self.session_wrapper.distclean())

    def depends(self):
        self.log.normal("%s:phase:depends" % self.session_name)
        self.session_wrapper.depends()


class SessionWrapper(object):

    def __init__(self, name, config, force=False):
        self.config = config
        self.session_name = name
        self.session = None
        self.log = jam.log.getLogger("jam.sessionwrapper")
        self.phase = "init"
        self.init_session()

    def load_session(self):
        session_loader = SessionLoader(self.config)
        session = session_loader.load(self.session_name + "." +
                                      self.session_name)
        if not session:
            raise SessionError(self.session_name,
                               "Could not load session from '%s'" %
                               self.config.get("jam_sessions"))
        validator = SessionValidator()
        if not validator.validate(session):
            raise SessionError(self.session_name,
                               "Loaded invalid session from '%s'. Errors: %s" %
                               (self.config.get("jam_sessions"),
                               "\n".join(validator.errors)))
        return session

    def init_session(self):
        session = self.load_session()
        version = session.version + "-" + session.revision
        name = self.session_name
        build_cache = self.config.get("jam_build_cache")
        download_cache = self.config.get("jam_download_cache")
        destroot = self.config.get("jam_destroot")
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

    def replace_session_args(self):
        self.session.args = self.session.args_replace()

    def depends(self):
        return DependencyAnalyser(self.config, self.session).analyse()

    def extract(self):
        src_path = self.session.src_path
        if not os.path.exists(src_path):
            self.log.debug("creating source dir '%s'" % src_path)
            os.mkdirs(src_path)
        filename = os.path.basename(self.session.session.url)
        archive_file = os.path.join(self.data_dir, filename)
        if os.path.isfile(archive_file):
            self.extract_file(archive_file, src_path)
        else:
            self.log.info("Nothing to extract.")

    def download(self):
        if not os.path.exists(self.data_dir):
            self.log.debug("creating data dir '%s'" % self.data_dir)
            os.mkdirs(self.data_dir)
        if self.session.url:
            self.log.info("Copying source file from '%s'." % self.session.url)
            dl = Downloader(self.session.url) 
            download_file = dl.copy(self.data_dir, self.force)
            dl.verify(self.session.hash)
        if not os.path.exists(self.patch_dir):
            self.log.debug("creating patch dir '%s'" % self.data_dir)
            os.mkdirs(self.data_dir)
        for patch in self.session.patches:
            dl = Downloader(patch)
            dl.copy(self.patch_dir)

    def configure(self):
        self.replace_session_args()
        build_path = self.session.build_path
        if not os.path.exists(build_path):
            self.log.debug("creating build dir '%s'" % build_path)
            os.mkdirs(self.build_path)
        self.session.configure()

    def build(self):
        self.replace_session_args()
        self.session.build()

    def destroot(self):
        self.replace_session_args()
        if not os.path.exists(self.dest_dir):
            self.log.debug("creating destroot dir '%s'" % self.dest_dir)
            os.mkdirs(self.dest_dir)
        self.session.destroot()

    def clean(self):
        self.replace_session_args()
        self.session.clean()

    def distclean(self):
        self.replace_session_args()
        self.session.distclean()


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
    build_path = None

    def __init__(self, config, src_dir, build_dir, dest_dir):
        self.config = config
        self.build_dir = build_dir
        self.src_dir = src_dir
        self.dest_dir = dest_dir
        self.verbose = self.config.get("verbose")
        self.debug = self.config.get("debug")

        self.vars = dict()
        self.vars["prefix"] = self.config.get("jam_prefix")
        self.vars["version"] = self.version
        self.vars["name"] = self.name
        self.vars["src_dir"] = self.src_dir
        self.vars["build_dir"] = self.build_dir
        self.vars["src_path"] = ""
        self.vars["build_path"] = ""

        if not self.src_path:
            self.src_path = os.path.join(src_dir, self.name 
                                         + "-" + self.version)
        else:
            self.src_path = self.var_replace(self.src_path)

        self.vars["src_path"] = self.src_path

        if not self.build_path:
            self.build_path = build_dir
        else:
            self.build_path = self.var_replace(self.build_path)

        self.vars["build_path"] = self.build_path

    def var_replace(self, var):
        return var % self.vars

    def args_replace(self):
        org_args = self.args
        args = []
        for arg in org_args:
            newarg = self.var_replace(arg)
            args.append(newarg)
        return args

    def configure(self):
        pass

    def build(self):
        pass

    def destroot(self):
        pass

    def clean(self):
        pass

    def distclean(self):
        pass


class MakeSession(Session):

    def build(self):
        Make(self.build_path, self.config.get("debug")).run()

    def destroot(self):
        Make(self.build_path, self.config.get("debug")).install(self.dest_dir)

    def clean(self):
        Make(self.build_path, self.config.get("debug")).clean()

    def distclean(self):
        Make(self.build_path, self.config.get("debug")).distclean()


class ConfigureSession(MakeSession):

    def configure(self):
        self.args.append("--prefix=" + self.config.get("jam_prefix"))
        self.args.append("--srcdir=" + self.src_path)
        super(ConfigureSession, self).configure()
        Configure(self.args, self.src_path, self.build_path,
                  self.config.get("debug")).run()


class CMakeSession(MakeSession):

    depends = ["cmake"]

    def configure(self):
        self.args.append("-DCMAKE_INSTALL_PREFIX=" + self.config.get("jam_prefix"))
        self.args.append("-DCMAKE_COLOR_MAKEFILE=TRUE")
        if self.config.get("verbose"):
            self.args.append("-DCMAKE_VERBOSE_MAKEFILE=TRUE")
        super(CMakeSession, self).configure()
        CMake(self.args, self.src_path, self.build_path,
              self.config.get("debug")).run()

    def distclean(self):
        # todo delete content of build_path
        pass


class SessionLoader(object):

    def __init__(self, config):
        self.config = config
        self.log = jam.log.getLogger("jam.sessionloader")
        self.add_path()

    def add_path(self):
        path = realpath(self.config.get("jam_sessions"))
        if not path in sys.path:
            sys.path.append(path)

    def module(self, name):
        try:
            return __import__(name, globals(), locals(), ['*'])
        except ImportError as error:
            self.log.warn("Could not import module '%s'. %s" % (name, error))
            return None

    def classes(self, modulename, parentclass=None):
        classes = []
        module = self.module(modulename)
        if not module:
            return classes
        self.log.debug("Imported module '%s'" % module)
        for key, value in module.__dict__.items():
            if inspect.isclass(value):
                if parentclass:
                    if not issubclass(value, parentclass):
                        continue
                # only load classes from module
                if value.__module__ != modulename:
                    self.log.debug("Skipping class '%s'" % value)
                    continue
                self.log.debug("Found class '%s'" % value)
                classes.append(value)
        return classes

    def sessions(self, module):
        return self.classes(module, Session)

    def load(self, sessionname):
        sessions = self.sessions(sessionname)
        if not sessions:
            self.log.warn("Could not load any session with name '%s'" %
                          sessionname)
            return None
        session = sessions[0]
        self.log.info("Loaded session '%s'" % session.__name__)
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
