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

from jam.utils import realpath

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
        self.session_dir = self.config.get("sessions")

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
        self.vars["session_path"] = realpath(os.path.join(self.session_dir,
                                             self.name))

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


