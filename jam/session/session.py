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

from jam.utils import Loader, realpath, list_dir, list_subdir, extract_file
from jam.download import Downloader
from jam.session.depend import DependencyAnalyser
from jam.db.objects import Status
from jam.db.db import Db
from jam.phase.phase import Phases

from jam.external.sqlalchemy import and_


class SessionError(Exception):

    def __init__(self, session_name, value):
        self.session_name = session_name
        self.value = value

    def __str__(self):
        return "Error in session '%s': %s" % (self.session_name, self.value)


class SessionManager(object):

    url = []
    patches = []

    def __init__(self, config, name, force=False):
        self.config = config
        self.force = force
        self.session_name = name
        self.log = jam.log.getLogger("jam.sessionmanager")
        self.session_wrapper = SessionWrapper(name, config, force)

    def download(self):
        self.session_wrapper.download()

    def extract(self):
        self.session_wrapper.extract()

    def archive(self):
        self.log.debug("%s:phase:archive" % self.session_name)

    def configure(self):
        self.session_wrapper.configure()

    def build(self):
        self.session_wrapper.build()

    def destroot(self):
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
        self.deactivate()

    def activate(self):
        self.session_wrapper.activate()

    def deactivate(self):
        self.session_wrapper.deactivate()

    def patch(self):
        self.log.debug("%s:phase:patch" % self.session_name)

    def unpatch(self):
        self.log.debug("%s:phase:unpatch" % self.session_name)

    def clean(self):
        self.session_wrapper.clean()

    def distclean(self):
        self.log.normal(self.session_wrapper.distclean())

    def depends(self):
        return self.session_wrapper.depends()

    def drop(self):
        self.log.debug("%s:phase:drop" % self.session_name)
        #TODO remove session destdir


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

    def depends(self):
        self.log.debug("%s:phase:depends" % self.session_name)
        return DependencyAnalyser(self.config, self.session).analyse()

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
                dl.copy(self.patch_dir)

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


class Session(object):

    depends = []
    url = ""
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
        self.prefix = self.config.get("prefix")

        self.__shadow = dict()

        if not self.name:
            module = self.__module__
            self.name = module.split(".")[0]

        self.vars = dict()
        self.vars["prefix"] = self.config.get("prefix")
        self.vars["rootdir"] = self.config.get("rootdir")
        self.vars["version"] = self.version
        self.vars["name"] = self.name
        self.vars["src_dir"] = self.src_dir
        self.vars["build_dir"] = self.build_dir

        if not self.src_path:
            self.src_path = os.path.join(src_dir, self.name 
                                         + "-" + self.version)

        self.vars["src_path"] = self.src_path

        if not self.build_path:
            self.build_path = build_dir

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

    def __getattribute__(self, name):
        value = object.__getattribute__(self, name)
        if not value:
            return value
        if name in ["src_path", "build_path", "args", "url",
                             "patches"]:
            if isinstance(value, list):
                newlist = self.__shadow.get(name)
                if not newlist:
                    newlist = value[:]
                    self.__shadow[name] = newlist
                for i, listvalue in enumerate(newlist):
                    replaced_value = self.var_replace(listvalue)
                    newlist[i] = replaced_value
                return newlist
            else:
                return self.var_replace(value)
        elif name == "depends":
            deps = value[:]
            for base in type(self).__bases__:
                superdeps = base.depends
                if superdeps:
                    deps.extend(superdeps)
            return list(set(deps))
        return value

    def init(self):
        pass

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
