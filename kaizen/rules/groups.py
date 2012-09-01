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

from kaizen.system.command import Command

class Group(object):

    depends = []
    configure_args = []
    build_args = []

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

    def __init__(self, rules, config):
        self.config = config
        self.rules = rules

        rules.configure_cflags.extend(self.configure_cflags)
        rules.configure_ldflags.extend(self.configure_ldflags)
        rules.configure_cppflags.extend(self.configure_cppflags)
        rules.configure_cxxflags.extend(self.configure_cxxflags)
        rules.configure_libs.extend(self.configure_libs)
        rules.configure_cpath.extend(self.configure_cpath)
        rules.configure_library_path.extend(self.configure_library_path)
        if not rules.configure_cc:
            rules.configure_cc = self.configure_cc
        if not rules.configure_cpp:
            rules.configure_cpp = self.configure_cpp
        if not rules.configure_cxx:
            rules.configure_cxx = self.configure_cxx

        rules.build_cflags.extend(self.build_cflags)
        rules.build_ldflags.extend(self.build_ldflags)
        rules.build_cppflags.extend(self.build_cppflags)
        rules.build_cxxflags.extend(self.build_cxxflags)
        rules.build_libs.extend(self.build_libs)
        rules.build_cpath.extend(self.build_cpath)
        rules.build_library_path.extend(self.build_library_path)
        if not rules.build_cc:
            rules.build_cc = self.build_cc
        if not rules.build_cpp:
            rules.build_cpp = self.build_cpp
        if not rules.build_cxx:
            rules.build_cxx = self.build_cxx

        rules.depends.extend(self.depends)
        rules.configure_args.extend(self.configure_args)
        rules.build_args.extend(self.build_args)

    def pre_configure(self):
        pass

    def post_configure(self):
        pass

    def pre_build(self):
        pass

    def post_build(self):
        pass

    def pre_destroot(self):
        pass

    def post_destroot(self):
        pass

    def pre_clean(self):
        pass

    def post_clean(self):
        pass

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


class UpdateMimeDatabase(Group):

    depends = ["shared-mime-info"]

    def __init__(self, rules, config):
        super(UpdateMimeDatabase, self).__init__(rules, config)
        args = []
        debug = self.config.get("debug")
        if debug:
            args.append("-V")
        args.append(rules.prefix + "/share/mime")
        self.updatemime = Command(rules.prefix + "/bin/update-mime-database",
                                  args, os.getcwd(), debug)

    def post_activate(self):
        self.updatemime.run()

    def post_deactivate(self):
        self.updatemime.run()


class KDE(UpdateMimeDatabase):

    def __init__(self, rules, config):
        super(KDE, self).__init__(rules, config)
        if rules.name != "kdelibs":
            rules.depends.append("kdelibs")
        debug = self.config.get("debug")
        self.kbuildsycoca = Command(rules.prefix + "/bin/kbuildsycoca4", [],
                                    os.getcwd(), debug)

    def post_activate(self):
        super(KDE, self).post_activate()
        self.kbuildsycoca.run()

    def post_deactivate(self):
        super(KDE, self).post_deactivate()
        if self.rules.name != "kdelibs":
            self.kbuildsycoca.run()
