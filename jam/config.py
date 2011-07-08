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

import os.path

from ConfigParser import SafeConfigParser

from jam.utils import realpath

JAM_VERSION = "0.1"
JAM_CONFIG_FILES  = ["/etc/jamrc", realpath("~/.jam/jamrc")]

class Config(object):

    def __init__(self, files=[], options={}):
        self.options = options
        self.config = {}
        defaults = {}

        # set default values
        defaults["debug"] = False
        defaults["verbose"] = False
        defaults["prefix"] = "/opt/local"
        defaults.update(options)

        self.configparser = SafeConfigParser(defaults)
        self.configparser.read(files) 

        if not self.configparser.has_section("jam"):
            self.configparser.add_section("jam")
        prefix = self._get("prefix")

        self.config["version"] = JAM_VERSION
        self.config["prefix"] = prefix
        self.config["verbose"] = self._getbool("verbose", False)
        self.config["debug"] = self._getbool("debug", False)
        self.config["rootdir"] = self._get("rootdir")
        self.config["sessions"] = self._get("sessions")
        self.config["destroot"] = self._get("destroot")
        self.config["downloadroot"] = self._get("downloadroot")
        self.config["buildroot"] = self._get("buildroot")

        jam_dir = self.config.get("rootdir", None)
        if not jam_dir:
            jam_dir = os.path.join(prefix, "jam")
            self.config["rootdir"] = jam_dir
        if not self.config.get("downloadroot", None):
            self.config["downloadroot"] =  os.path.join(jam_dir, "cache")
        if not self.config.get("sessions", None):
            self.config["sessions"] =  os.path.join(jam_dir, "session")
        if not self.config.get("destroot", None):
            self.config["destroot"] = os.path.join(jam_dir, "destroot")
        if not self.config.get("buildroot", None):
            self.config["buildroot"] = os.path.join(jam_dir, "cache")

    def _get(self, value, default=None):
        if value in self.options and self.options[value]:
            return self.options[value]
        try:
            return self.configparser.get("jam", value)
        except:
            return default

    def _getbool(self, value, default=None):
        if value in self.options and self.options[value]:
            return self.options[value]
        try:
            return self.configparser.getboolean("jam", value)
        except:
            return default

    def get(self, value):
        # TODO: raise error if value not found
        return self.config[value]

