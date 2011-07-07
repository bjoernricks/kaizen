# vim:fileencoding=utf-8:et::sw=4:ts=4:tw=80:

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

import jam.log

from tempfile import mkdtemp

from jam.utils import Template, Hash, list_contents, extract_file, realpath
from jam.download import Downloader

class SessionCreateError(Exception):
    pass


class TypeDetector(object):

    def detect(self, dir):
        return None


class FileDetector(TypeDetector):

    def __init__(self, filename, templatename):
        self.filename = filename
        self.templatename = templatename

    def detect(self, dir):
        (dirs, files) = list_contents(dir)
        if len(dirs) == 1:
            # only one subdir, look in subdir
            dir = os.path.join(dir, dirs[0])
            (dirs, files) = list_contents(dir)
        if self.filename in files:
            return Template(self.templatename + ".template")
        return None 


detectors = [FileDetector("CMakeList.txt", "cmake"),
             FileDetector("setup.py", "python"),
             FileDetector("configure", "autotools"),]


class SessionCreator(object):

    def __init__(self, config, url, keep=False):
        self.url = url
        self.keep = keep
        self.session_dir = config.get("sessions")
        self.dir = config.get("rootdir")
        self.template = None
        self.name = None
        self.version = None
        self.tmp_dir = None
        self.log = jam.log.getLogger("jam.sessioncreator")

    def set_template(self, template):
        self.template = template

    def set_name(self, name):
        self.name = name

    def set_version(self, version):
        self.version = version

    def create(self, stdout=False):
        self.tmp_dir = mkdtemp(prefix="tmp-session-", dir=self.dir)
        self.log.debug("Created temporary directory '%s'" % self.tmp_dir)
        downloader = Downloader(self.url)
        source = downloader.copy(self.tmp_dir)
        hashcalc = Hash(source)
        md5 = hashcalc.md5()
        self.log.debug("md5 hash is '%s'" % md5)
        sha1 = hashcalc.sha1()
        self.log.debug("sha1 hash is '%s'" % sha1)

        name = self.name
        if not self.name or not self.version:
            filename = os.path.basename(source)
            if not "-" in filename:
                self.clean()
                raise SessionCreateError("Could not determinte name and "\
                                         "version from file '%s'" % filename)
            suffixes = [".tar.gz", ".tar.bz2", ".tgz", "tbz2", ".zip"]
            for suffix in suffixes:
                if filename.endswith(suffix):
                    index = filename.rfind(suffix)
                    filename = filename[:index]
            split = filename.split("-")
            name = split[0]
            version = "".join(split[1:])

            if not self.version:
                self.log.info("Determined session version is '%s'" % version)
            if not self.name:
                self.log.info("Determined session name is '%s'" % name)

        if self.name:
            name = self.name
        if self.version:
            version = self.version
        if not self.template:
            extract_file(source, self.tmp_dir)
            for detector in detectors:
                template = detector.detect(self.tmp_dir)
                if template:
                    break
            if not template:
                self.log.info("Could not determine template for '%s'. "
                              "Using default." % name)
                template = Template("default.template")
        else:
            template = Template(self.templatename + ".template")

        vars = dict()
        vars["name"] = name
        vars["version"] = version
        vars["md5"] = md5
        vars["sha1"] = sha1
        vars["url"] = self.url
        vars["rootdir"] = self.dir
        vars["sessions"] = self.session_dir
        vars["sessionname"] = name.capitalize()
        
        if stdout:
            print template.replace(vars)
        else:
            new_session_dir = os.path.join(realpath(self.session_dir), name)
            if not os.path.exists(new_session_dir):
                os.makedirs(new_session_dir)
            try:
                sessionfile = os.path.join(new_session_dir, name + ".py")
                f = open(sessionfile, "w")
                self.log.info("Creating new session file '%s'" % sessionfile)
                f.write(template.replace(vars))
                f.close()
                f = open(os.path.join(new_session_dir, "__init__.py"), "w")
            finally:
                f.close()

        self.clean()

    def clean(self):
        if self.tmp_dir and not self.keep:
            self.log.debug("Deleteing temporary directory '%s'" % self.tmp_dir)
            shutil.rmtree(self.tmp_dir)

