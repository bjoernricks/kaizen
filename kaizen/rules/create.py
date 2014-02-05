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

import os
import os.path
import shutil

import kaizen.logging

from tempfile import mkdtemp

from kaizen.utils import Template, Hash, list_contents, extract_file, real_path
from kaizen.system.download import UrlDownloader
from kaizen.rules.error import RulesCreateError


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


class NameDetector(FileDetector):

    def __init__(self, prefix, filename, templatename):
        super(NameDetector, self).__init__(filename, templatename)
        self.prefix = prefix

    def get_name(self):
        return self.prefix + "-" + self.name


detectors = [FileDetector("CMakeLists.txt", "cmake"),
             NameDetector("python", "setup.py", "python"),
             FileDetector("configure", "autotools"),
             NameDetector("perl", "Makefile.PL", "perl")]


class RulesCreator(object):

    def __init__(self, config, url, keep=False):
        self.url = url
        self.keep = keep
        self.rules_dir = config.get("rules")
        self.dir = config.get("rootdir")
        self.template = None
        self.name = None
        self.version = None
        self.tmp_dir = None
        self.log = kaizen.logging.getLogger(self)

    def set_template(self, template):
        self.template = template

    def set_name(self, name):
        self.name = name

    def set_version(self, version):
        self.version = version

    def create(self, stdout=False):
        if not os.path.isdir(self.dir):
            os.makedirs(self.dir)
        self.tmp_dir = mkdtemp(prefix="tmp-rules-", dir=self.dir)
        self.log.debug("Created temporary directory '%s'" % self.tmp_dir)
        downloader = UrlDownloader(None, self.url)
        source = downloader.copy(self.tmp_dir)
        hashcalc = Hash(source)
        md5 = hashcalc.md5()
        self.log.debug("md5 hash is '%s'" % md5)
        sha1 = hashcalc.sha1()
        self.log.debug("sha1 hash is '%s'" % sha1)

        filename = os.path.basename(source)
        if not "-" in filename and (not self.name or not self.version):
            self.clean()
            raise RulesCreateError("Could not detect name and "\
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

        self.log.debug("Detected rules name is '%s'" % detected_name)
        self.log.debug("Detected rules version is '%s'" % detected_version)
        self.log.info("Rules name is '%s'" % name)
        self.log.info("Rules version is '%s'" % version)

        vars = dict()
        vars["name"] = name
        vars["version"] = version
        vars["md5"] = md5
        vars["sha1"] = sha1
        vars["url"] = self.url
        vars["rootdir"] = self.dir
        vars["rules"] = self.rules_dir
        vars["rulesname"] = name.replace("-","").capitalize()
        vars["detectedname"] = detected_name
        vars["detectedversion"] = detected_version

        # self.name and self.version may contain templates
        if self.name:
            name = self.name % vars
        if self.version:
            version = self.version % vars

        if stdout:
            print template.replace(vars)
        else:
            new_rules_dir = os.path.join(real_path(self.rules_dir[0]), name)
            if not os.path.exists(new_rules_dir):
                os.makedirs(new_rules_dir)
            try:
                rulesfile = os.path.join(new_rules_dir, "rules.py")
                f = open(rulesfile, "w")
                self.log.info("Creating new rules file '%s'" % rulesfile)
                f.write(template.replace(vars))
            finally:
                f.close()

        self.clean()

    def clean(self):
        if self.tmp_dir and not self.keep:
            self.log.debug("Deleteing temporary directory '%s'" % self.tmp_dir)
            shutil.rmtree(self.tmp_dir)

