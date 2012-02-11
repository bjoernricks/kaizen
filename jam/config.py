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

import jam

from jam.utils import real_path, get_number_of_cpus
from jam.error import JamRuntimeError

JAM_CONFIG_FILES  = ["/etc/jamrc", real_path("~/.jam/jamrc")]

class Config(object):
    """
    Config class for several jam settings

    Variables are:
    * version - String: jam version
    * quiet - Bool: only return parsable output and don't display addition user
                    related output
    * debug - Bool: debug is enabled/disabled (default is False)
    * verbose - Bool: commands should print it's output (default is False)
    * debugdb - Bool: database queries are printed (default is False)
    * prefix - String: absolute path to the prefix (default is /usr/local)
    * rootdir - String: path to the rootdir (default is %(prefix)s/jam)
    * downloadroot - String: path to the directory to put in downloaded source
                             (default is %(rootdir)s/cache
    * destroot - String: path to the directory to put in installed files
                         (default is %(rootdir)s/destroot)
    * buildroot - String: path to the build directory (default is
                          %(rootdir)s/cache)
    * sessions - List: paths to the sessions (default is [%(rootdir)s/sessions])
    * packagepath - String: absolute path to the jam python package (calculated
                            at runtime)
    * system - String: path to an additional config file containing system
                       releated settings
    * appdir - String: path to the Mac OS X application bundle dir
    * buildjobs - Integer: number of jobs that should be used to build the
                           source e.g. started via make -j.
                           0 or empty for auto detection.
    """

    def __init__(self, files=[], options={}):
        self.options = options
        self.config = {}
        defaults = {}

        # set default values
        defaults["debug"] = False
        defaults["quiet"] = False
        defaults["verbose"] = False
        defaults["prefix"] = "/usr/local"
        defaults["buildjobs"] = 0
        defaults.update(options)

        self.configparser = SafeConfigParser(defaults)
        self.configparser.read(files) 

        if not self.configparser.has_section("jam"):
            self.configparser.add_section("jam")
        prefix = real_path(self._get("prefix"))

        self.config["version"] = jam.__version__
        self.config["prefix"] = prefix
        self.config["verbose"] = self._getbool("verbose", False)
        self.config["quiet"] = self._getbool("quiet", False)
        self.config["debug"] = self._getbool("debug", False)
        self.config["rootdir"] = self._get("rootdir")
        self.config["sessions"] = self._getlist("sessions")
        self.config["destroot"] = self._get("destroot")
        self.config["downloadroot"] = self._get("downloadroot")
        self.config["buildroot"] = self._get("buildroot")
        self.config["debugdb"] = self._getbool("debugdb")
        self.config["system"] = self._get("system")
        self.config["buildjobs"] = self._getint("buildjobs")

        jam_package_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        os.path.pardir))
        self.config["packagepath"] = jam_package_path

        jam_dir = self.config.get("rootdir", None)
        if not jam_dir:
            jam_dir = os.path.join(prefix, "jam")
            self.config["rootdir"] = jam_dir
        if not self.config.get("system", None):
            self.config["system"] = os.path.join(jam_dir, "system")
        if not self.config.get("downloadroot", None):
            self.config["downloadroot"] = os.path.join(jam_dir, "cache")
        if not self.config.get("sessions"):
            self.config["sessions"] = [os.path.join(jam_dir, "session")]
        if not self.config.get("destroot", None):
            self.config["destroot"] = os.path.join(jam_dir, "destroot")
        if not self.config.get("buildroot", None):
            self.config["buildroot"] = os.path.join(jam_dir, "cache")
        if not self.config.get("appsdir", None):
            self.config["appsdir"] = os.path.join(prefix, "Applications")
        if not self.config.get("buildjobs") > 0:
            self.config["buildjobs"] = get_number_of_cpus() + 1

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

    def _getint(self, value, default=0):
        if value in self.options and self.options[value]:
            return self.options[value]
        try:
            return self.configparser.getint("jam", value)
        except:
            return default

    def _getlist(self, value, default=[]):
        list_value = self._get(value, default)
        if not list_value:
            return default
        # TODO use regex to split string
        return list_value.split(",")

    def get(self, value):
        if value not in self.config:
            raise JamRuntimeError("Value for '%s' not found in config." % value)
        return self.config[value]

