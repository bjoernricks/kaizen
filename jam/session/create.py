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
import os.path
import shutil

import jam.log

from tempfile import mkdtemp

from jam.utils import Template, Hash, list_contents, extract_file, real_path
from jam.download import Downloader

class SessionCreateError(Exception):
    pass


class TypeDetector(object):

    def detect(self, dir):
        pass

    def get_template(self):
        pass

    def get_name(self):
        pass

class FileDetector(TypeDetector):

    def __init__(self, filename, templatename):
        self.name = None
        self.filename = filename
        self.templatename = templatename
        self.template = None

    def detect(self, name, dir):
        self.name = name
        (dirs, files) = list_contents(dir)
        if len(dirs) == 1:
            # only one subdir, look in subdir
            dir = os.path.join(dir, dirs[0])
            (dirs, files) = list_contents(dir)
        if self.filename in files:
            self.template = Template(self.templatename + ".template")
            return True
        return False

    def get_template(self):
        return self.template

    def get_name(self):
        return self.name


class PythonDetector(FileDetector):

    def detect(self, dir, name):
        retval = super(PythonDetector, self).detect(dir, name)
        self.name = "python-" + self.name
        return retval


detectors = [FileDetector("CMakeList.txt", "cmake"),
             PythonDetector("setup.py", "python"),
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
        if not os.path.isdir(self.dir):
            os.makedirs(self.dir)
        self.tmp_dir = mkdtemp(prefix="tmp-session-", dir=self.dir)
        self.log.debug("Created temporary directory '%s'" % self.tmp_dir)
        downloader = Downloader(self.url)
        source = downloader.copy(self.tmp_dir)
        hashcalc = Hash(source)
        md5 = hashcalc.md5()
        self.log.debug("md5 hash is '%s'" % md5)
        sha1 = hashcalc.sha1()
        self.log.debug("sha1 hash is '%s'" % sha1)

        filename = os.path.basename(source)
        if not "-" in filename and (not self.name or not self.version):
            self.clean()
            raise SessionCreateError("Could not detect name and "\
                    "version from file '%s'" % filename)

        if "-" in filename:
            suffixes = [".tar.gz", ".tar.bz2", ".tgz", "tbz2", ".zip"]
            for suffix in suffixes:
                if filename.endswith(suffix):
                    index = filename.rfind(suffix)
                    filename = filename[:index]
            split = filename.rsplit("-", 1)
            detected_name = split[0]
            name = detected_name.lower()
            version = split[1]
            detected_version = version
            self.log.info("Detected session version is '%s'" % version)
            self.log.info("Detected session name is '%s'" % name)
        else:
            name = self.name
            version = self.version
            detected_name = self.name
            detected_version = self.version

        if not self.template:
            extract_file(source, self.tmp_dir)
            template = None
            for detector in detectors:
                if detector.detect(name, self.tmp_dir):
                    template = detector.get_template()
                    name = detector.get_name()
                    break
            if not template:
                self.log.info("Could not detected template for '%s'. "
                              "Using default." % name)
                template = Template("default.template")
        else:
            template = Template(self.templatename + ".template")

        # name and version may be changed by template
        # overwrite them again
        if self.name:
            name = self.name
        if self.version:
            version = self.version

        vars = dict()
        vars["name"] = name
        vars["version"] = version
        vars["md5"] = md5
        vars["sha1"] = sha1
        vars["url"] = self.url
        vars["rootdir"] = self.dir
        vars["sessions"] = self.session_dir
        vars["sessionname"] = name.replace("-","").capitalize()
        vars["detectedname"] = detected_name
        vars["detectedversion"] = detected_version
        
        if stdout:
            print template.replace(vars)
        else:
            new_session_dir = os.path.join(real_path(self.session_dir[0]), name)
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

