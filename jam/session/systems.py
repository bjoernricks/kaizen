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
from jam.system import Configure, CMake, Make, Command, Copy

class MakeSession(Session):

    def build(self):
        Make(self.build_path, self.config.get("debug")).run()

    def destroot(self):
        Make(self.build_path, self.config.get("debug")).install(self.dest_dir)

    def clean(self):
        Make(self.build_path, self.config.get("debug")).clean()

    def distclean(self):
        Make(self.build_path, self.config.get("debug")).distclean()

    def configure(self):
        pass


class ConfigureSession(MakeSession):

    def configure(self):
        args = self.args
        args.append("--prefix=" + self.config.get("prefix"))
        args.append("--srcdir=" + self.src_path)
        Configure(args, self.src_path, self.build_path,
                  self.config.get("debug")).run()


class CMakeSession(MakeSession):

    depends = ["cmake"]

    def configure(self):
        args = self.args
        args.append("-DCMAKE_INSTALL_PREFIX=" + self.config.get("prefix"))
        args.append("-DCMAKE_COLOR_MAKEFILE=TRUE")
        if self.config.get("verbose"):
            args.append("-DCMAKE_VERBOSE_MAKEFILE=TRUE")
        CMake(args, self.src_path, self.build_path,
              self.config.get("debug")).run()

    def distclean(self):
        # todo delete content of build_path
        pass


class PythonSession(Session):

    def configure(self):
        Copy(self.src_path, self.build_path).run()

    def build(self):
        Command("python", ["setup.py", "build"], self.build_path,
                self.config.get("debug")).run()

    def destroot(self):
        Command("python", ["setup.py", "install", 
                "--prefix="+ self.config.get("prefix"),
                "--root=" + self.dest_dir],
                self.build_path,
                self.config.get("debug")).run()

    def clean(self):
        Command("python", ["setup.py", "clean"], self.build_path,
                self.config.get("debug")).run()

    def distclean(self):
        pass


