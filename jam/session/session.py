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

import inspect
import os.path

from jam.utils import real_path
from jam.download import UrlDownloader

class Session(object):
    """
    Base Class for all Sessions

    All pre/post methods must not rely on any stuff that a corresponding
    pre/post method has created, set, etc. That means e.g. the post_deactivate
    method must not expect that the post_activate method has created a specific
    symlink. In that case the post_deactivate method must check for the
    existance of this sysmlink before removing it.
    """

    depends = []
    url = ""
    patches = []
    version = ""
    revision = "0"
    hash = {}
    configure_args = []
    build_args = []
    name = ""
    src_path = None
    build_path = None

    downloader = UrlDownloader

    def __init__(self, config, src_dir, build_dir, dest_dir):
        self.config = config
        self.build_dir = build_dir
        self.src_dir = src_dir
        self.dest_dir = dest_dir
        self.verbose = self.config.get("verbose")
        self.debug = self.config.get("debug")
        self.prefix = self.config.get("prefix")
        self.session_dirs = self.config.get("sessions")
        self.dist_version = self.version + "-" + self.revision
        self.destroot_dir = self.config.get("destroot")
        self.session_name = self.__module__.split(".")[0]
        self.destroot_path = os.path.join(self.destroot_dir, self.session_name,
                                          self.dist_version)
        self.session_path = real_path(os.path.dirname(
                                     inspect.getfile(self.__class__)))
        self.package_path = self.config.get("packagepath")

        self.__shadow = dict()

        if not self.name:
            self.name = self.session_name

        self.vars = dict()
        self.vars["prefix"] = self.config.get("prefix")
        self.vars["rootdir"] = self.config.get("rootdir")
        self.vars["version"] = self.version
        self.vars["revision"] = self.revision
        self.vars["name"] = self.name
        self.vars["src_dir"] = self.src_dir
        self.vars["build_dir"] = self.build_dir
        self.vars["session_path"] = self.session_path
        self.vars["dist_version"] = self.dist_version
        self.vars["package_path"] = self.package_path

        if not self.src_path:
            self.src_path = os.path.join(src_dir, self.name
                                         + "-" + self.version)
        self.vars["src_path"] = self.src_path

        if not self.build_path:
            self.build_path = build_dir

        self.vars["build_path"] = self.build_path

    def var_replace(self, var):
        if isinstance(var, list):
            for i, val in enumerate(var):
                var[i] = val % self.vars
            else:
                return var
        else:
            return var % self.vars

    def __getattribute__(self, name):
        try:
            value = object.__getattribute__(self, name)
        except AttributeError:
            self.__dict__[name] = None
            return None
        if not value:
            return value
        if name in ["src_path", "build_path", "configure_args", "url",
                    "build_args", "patches"]:
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

    def pre_configure(self):
        pass

    def post_configure(self):
        pass

    def build(self):
        pass

    def pre_build(self):
        pass

    def post_build(self):
        pass

    def destroot(self):
        pass

    def pre_destroot(self):
        pass

    def post_destroot(self):
        pass

    def clean(self):
        pass

    def pre_clean(self):
        pass

    def post_clean(self):
        pass

    def distclean(self):
        pass

    def pre_activate(self):
        pass

    def post_activate(self):
        pass

    def pre_deactivate(self):
        pass

    def post_deactivate(self):
        pass

