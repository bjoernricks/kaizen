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

from jam.session.session import Session
from jam.system.command import Configure, CMake, Make, Command, Copy, Delete

class MakeSession(Session):

    def build(self):
        Make(self.build_path, self.debug).run(self.build_args)

    def destroot(self):
        Make(self.build_path, self.debug).install(self.dest_dir)

    def clean(self):
        Make(self.build_path, self.debug).clean()

    def distclean(self):
        Make(self.build_path, self.debug).distclean()

    def configure(self):
        pass


class ConfigureSession(MakeSession):

    def configure(self):
        args = self.configure_args
        args.append("--prefix=" + self.prefix)
        args.append("--srcdir=" + self.src_path)
        configure = Configure(args, self.src_path, self.build_path,
                             self.debug)
        if self.configure_cc:
            configure.set_cc(self.configure_cc)
        if self.configure_cpp:
            configure.set_cpp(self.configure_cpp)
        if self.configure_cflags:
            configure.set_cflags(self.configure_cflags)
        if self.configure_cppflags:
            configure.set_cppflags(self.configure_cppflags)
        if self.configure_ldflags:
            configure.set_ldflags(self.configure_ldflags)
        if self.configure_libs:
            configure.set_libs(self.configure_libs)
        if self.configure_cxx:
            configure.set_cxx(self.configure_cxx)
        if self.configure_cxxflags:
            configure.set_cxxflags(self.configure_cxxflags)
        configure.run()


class CMakeSession(MakeSession):

    depends = ["cmake"]

    def configure(self):
        args = self.configure_args
        args.append("-DCMAKE_INSTALL_PREFIX=" + self.prefix)
        args.append("-DCMAKE_COLOR_MAKEFILE=TRUE")
        if self.verbose:
            args.append("-DCMAKE_VERBOSE_MAKEFILE=TRUE")
        CMake(args, self.src_path, self.build_path,
              self.debug).run()

    def distclean(self):
        Delete(self.build_dir).run()


class PythonSession(Session):

    def configure(self):
        Copy(self.src_path, self.build_path).run()

    def build(self):
        #TODO drop configure and use --build-base=
        args = ["setup.py", "build"]
        args.extend(self.build_args)
        Command("python", args, self.build_path,
                self.debug).run()

    def destroot(self):
        Command("python", ["setup.py", "install", 
                "--prefix="+ self.prefix,
                "--root=" + self.dest_dir],
                self.build_path,
                self.debug).run()

    def clean(self):
        Command("python", ["setup.py", "clean"], self.build_path,
                self.debug).run()

    def distclean(self):
        pass


