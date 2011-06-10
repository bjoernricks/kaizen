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

import os.path
import shutil

import jam.log

from tempfile import mkdtemp

from jam.utils import Template, Hash
from jam.download import Downloader

class SessionCreateError(Exception):
    pass

class SessionCreator(object):

    def __init__(self, config, url, keep=False):
        self.url = url
        self.keep = keep
        self.session_dir = config.get("sessions")
        self.dir = config.get("rootdir")
        self.template = None
        self.name = None
        self.version = None
        self.log = jam.log.getLogger("jam.sessioncreator")

    def set_template(self, template):
        self.template = template

    def set_name(self, name):
        self.name = name

    def set_version(self, version):
        self.version = version

    def create(self):
        temp_dir = mkdtemp(prefix="tmp-session-", dir=self.dir)
        self.log.debug("Created temporary directory '%s'" % temp_dir)
        downloader = Downloader(self.url)
        source = downloader.copy(temp_dir)
        hashcalc = Hash(source)
        md5 = hashcalc.md5()
        self.log.debug("md5 hash is '%s'" % md5)
        sha1 = hashcalc.sha1()
        self.log.debug("sha1 hash is '%s'" % sha1)

        name = self.name
        if not self.name or not self.version:
            filename = os.path.basename(source)
            if not "-" in filename:
                self._clean(tmp_dir)
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

        if self.template:
            template = Template(self.template + ".template")

        self._clean(temp_dir)

    def _clean(self, tmp_dir):
        if not self.keep:
            self.log.debug("Deleteing temporary directory '%s'" % tmp_dir)
            shutil.rmtree(tmp_dir)
