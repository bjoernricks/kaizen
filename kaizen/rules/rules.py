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

import inspect
import os.path

import kaizen.logging

from kaizen.utils import real_path
from kaizen.system.download import UrlDownloader
from kaizen.system.patch import Simple
from kaizen.system.extract import ArchiveFile


class Rules(object):
    """
    Base Class for all Rules

    All pre/post methods must not rely on any stuff that a corresponding
    pre/post method has created, set, etc. That means e.g. the post_deactivate
    method must not expect that the post_activate method has created a specific
    symlink. In that case the post_deactivate method must check for the
    existance of this sysmlink before removing it.
    """

    depends = []
    runtime_depends = []
    url = ""
    patches = []
    version = ""
    revision = "0"
    hash = {}
    name = ""
    src_path = None
    build_path = None
    patch_path = None
    parallel = True

    configure_args = []
    configure_path = None
    configure_env = dict()
    configure_cflags = []
    configure_ldflags = []
    configure_cc = None
    configure_cpp = None
    configure_cppflags = []
    configure_cxx = None
    configure_cxxflags = []
    configure_libs = []
    configure_cpath = []
    configure_library_path = []

    build_args = []
    build_env = dict()
    build_cflags = []
    build_ldflags = []
    build_cc = None
    build_cpp = None
    build_cppflags = []
    build_cxx = None
    build_cxxflags = []
    build_libs = []
    build_cpath = []
    build_library_path = []

    download_cmd = UrlDownloader
    extract_cmd = ArchiveFile
    patch_cmd = Simple
    build_cmd = None
    configure_cmd = None
    destroot_cmd = None
    clean_cmd = None
    distclean_cmd = None

    download_seq = None
    extract_seq = None
    patch_seq = None
    build_seq = None
    configure_seq = None
    destroot_seq = None

    destroot_env = dict()

    delete_destroot_seq = None
    delete_build_seq = None
    distclean_seq = None
    unpatch_seq = None
    delete_source_seq = None
    delete_download_seq = None

    groups = []

    def __init__(self, config, src_dir, build_dir, dest_dir):
        self.config = config
        self.build_dir = build_dir
        self.src_dir = src_dir
        self.dest_dir = dest_dir
        self.verbose = self.config.get("verbose")
        self.debug = self.config.get("debug")
        self.prefix = self.config.get("prefix")
        self.rules_dirs = self.config.get("rules")
        self.destroot_dir = self.config.get("destroot")
        self.buildjobs = self.config.get("buildjobs")
        # rules name must be in sync with wrapper rules name for destroot
        # installation. Currently it's not best to have different sources
        # for rules name. Changing the module layout for rules installation
        # could fail if a rules uses self.destdir_path then.
        # TODO: All parameters should be set by Wrapper
        self.rules_name = self.__module__.split(".")[-2]
        self.destroot_path = os.path.join(self.destroot_dir, self.rules_name,
                                          self.get_dist_version())
        # TODO check if destroot_path and dest_dir are equal
        self.rules_path = real_path(os.path.dirname(
                                     inspect.getfile(self.__class__)))
        self.package_path = self.config.get("packagepath")
        self.apps_dir = self.config.get("appsdir")
        self.dest_path = self.destroot_path + self.prefix

        self.log = kaizen.logging.getLogger("kaizen.rules." + self.rules_name)

        self.__shadow = dict()

        if not self.name:
            self.name = self.rules_name

        self.vars = dict()
        self.vars["prefix"] = self.config.get("prefix")
        self.vars["rootdir"] = self.config.get("rootdir")
        self.vars["version"] = self.get_version()
        self.vars["revision"] = self.revision
        self.vars["name"] = self.name
        self.vars["src_dir"] = self.src_dir
        self.vars["build_dir"] = self.build_dir
        self.vars["rules_path"] = self.rules_path
        self.vars["dist_version"] = self.get_dist_version()
        self.vars["package_path"] = self.package_path
        self.vars["apps_dir"] = self.apps_dir
        self.vars["dest_path"] = self.dest_path

        if not self.src_path:
            self.src_path = os.path.join(src_dir, self.name
                                         + "-" + self.version)
        self.src_path = real_path(self.src_path)
        self.vars["src_path"] = self.src_path

        if not self.build_path:
            self.build_path = build_dir
        self.build_path = real_path(self.build_path)
        self.vars["build_path"] = self.build_path

        if not self.patch_path:
            self.patch_path = os.path.join(self.rules_path, "patches")
        self.patch_path = real_path(self.patch_path)
        self.vars["patch_path"] = self.patch_path

        # src_path may be differenct then the path to the sources where
        # e.g. configure should be run. A rules may copy the sources to
        # a different dir to be able to do clean builds.
        if not self.configure_path:
            self.configure_path = self.src_path
        self.vars["configure_path"] = self.configure_path

        groups = self.groups
        self._groups = []
        for group in groups:
            self._groups.append(group(self, config))


        self.init()

    def init(self):
        pass

    def var_replace(self, var):
        if isinstance(var, list):
            for i, val in enumerate(var):
                var[i] = self.var_replace(val)
            else:
                return var
        elif isinstance(var, basestring):
            return var % self.vars
        else:
            return var

    def __getattribute__(self, name):
        try:
            value = object.__getattribute__(self, name)
        except AttributeError:
            value = None
            found = False
            for group in self.groups:
                if hasattr(group, name):
                    value = getattr(group, name)
                    found = True
            if not found:
                raise
            self.__dict__[name] = value
            return value
        if name in ["src_path", "build_path", "configure_args", "url",
                    "build_args", "patches", "configure_path", "patch_path",
                    "configure_cflags", "configure_ldflags", "configure_cc",
                    "configure_cpp", "configure_cppflags", "configure_libs",
                    "configure_cxx", "configure_cxxflags", "configure_cpath",
                    "configure_library_path", "build_cflags", "build_ldflags",
                    "build_cc", "build_cpp", "build_cppflags", "build_libs",
                    "build_cxx", "build_cxxflags", "build_cpath",
                    "build_library_path",
                    ]:
            if not value:
                return value
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
            deps = []
            if self.build_cmd:
                deps.extend(self.build_cmd.depends)
            if self.extract_cmd:
                deps.extend(self.extract_cmd.depends)
            if self.patch_cmd:
                deps.extend(self.patch_cmd.depends)
            if self.configure_cmd:
                deps.extend(self.configure_cmd.depends)
            if self.destroot_cmd:
                deps.extend(self.destroot_cmd.depends)
            if self.clean_cmd:
                deps.extend(self.clean_cmd.depends)
            if self.distclean_cmd:
                deps.extend(self.distclean_cmd.depends)
            deps.extend(value[:])

            for base in type(self).__bases__:
                superdeps = base.depends
                if superdeps:
                    deps.extend(superdeps)
            return list(set(deps))
        return value

    def init(self):
        pass

    def configure(self):
        if self.configure_cmd:
            self.configure_cmd(self).configure()

    def pre_configure(self):
        pass

    def post_configure(self):
        pass

    def build(self):
        if self.build_cmd:
            self.build_cmd(self).build()

    def pre_build(self):
        pass

    def post_build(self):
        pass

    def destroot(self):
        if self.destroot_cmd:
            self.destroot_cmd(self).destroot()

    def pre_destroot(self):
        pass

    def post_destroot(self):
        pass

    def clean(self):
        if self.clean_cmd:
            self.clean_cmd(self).clean()

    def pre_clean(self):
        pass

    def post_clean(self):
        pass

    def distclean(self):
        if self.distclean_cmd:
            self.distclean_cmd(self).distclean()

    def pre_activate(self):
        pass

    def post_activate(self):
        pass

    def pre_deactivate(self):
        pass

    def post_deactivate(self):
        pass

    def pre_patch(self):
        pass

    def post_patch(self):
        pass

    @classmethod
    def get_version(cls):
        return cls.version

    @classmethod
    def get_dist_version(cls):
        return cls.get_version() + "-" + cls.revision
