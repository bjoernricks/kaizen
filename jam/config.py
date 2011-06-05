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

from ConfigParser import SafeConfigParser

class Config(object):

    def __init__(self, files=[], config={}):
        self.config = {}
        defaults = {}

        # set default values
        defaults["debug"] = "0"
        defaults["verbose"] = "0" 
        defaults["prefix"] = "/opt/local"
        defaults.update(config)

        self.configparser = SafeConfigParser(defaults)
        self.configparser.read(files) 

        if not self.configparser.has_section("jam"):
            self.configparser.add_section("jam")
        prefix = self._get("prefix")

        self.config["prefix"] = prefix
        self.config["verbose"] = bool(self._get("verbose", False))
        self.config["debug"] = bool(self._get("debug", False))
        self.config["dir"] = self._get("dir")
        self.config["sessions"] = self._get("sessions")
        self.config["destroot"] = self._get("destroot")
        self.config["downloadroot"] = self._get("downloadroot")
        self.config["buildroot"] = self._get("buildroot")

        jam_dir = self.config.get("dir", None)
        if not jam_dir:
            jam_dir = os.path.join(prefix, "jam")
        if not self.config.get("downloadroot", None):
            self.config["downloadroot"] =  os.path.join(jam_dir, "cache")
        if not self.config.get("sessions", None):
            self.config["sessions"] =  os.path.join(jam_dir, "session")
        if not self.config.get("destroot", None):
            self.config["destroot"] = os.path.join(jam_dir, "destroot")
        if not self.config.get("buildroot", None):
            self.config["buildroot"] = os.path.join(jam_dir, "cache")

    def _get(self, value, default=None):
        try:
            return self.configparser.get("jam", value)
        except:
            return default

    def get(self, value):
        # TODO: raise error if value not found
        return self.config[value]

