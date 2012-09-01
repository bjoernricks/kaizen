# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# kaizen - Continously improve, build and manage free software
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

import sys
import os
import os.path

from kaizen.logging.log import getLogger
from kaizen.session.error import SessionError
from kaizen.session.session import Session
from kaizen.system.command import Configure, CMake, Make, Command, Copy, Delete

class SessionCmd(object):

    depends = []

    def __init__(self, session):
        self.log = getLogger(self)
        self.session = session


class MakeCmd(SessionCmd):

    def build(self):
        j = self.session.config.get("buildjobs")

        if self.session.parallel and j > 1:
            build_args = ["-j" + str(j)] + self.session.build_args
        else:
            build_args = self.session.build_args

        make = Make(self.session.build_path, self.session.debug)
        if self.session.build_cc:
            make.set_cc(self.session.build_cc)
        if self.session.build_cpp:
            make.set_cpp(self.session.build_cpp)
        if self.session.build_cflags:
            make.set_cflags(self.session.build_cflags)
        if self.session.build_cppflags:
            make.set_cppflags(self.session.build_cppflags)
        if self.session.build_ldflags:
            make.set_ldflags(self.session.build_ldflags)
        if self.session.build_libs:
            make.set_libs(self.session.build_libs)
        if self.session.build_cxx:
            make.set_cxx(self.session.build_cxx)
        if self.session.build_cxxflags:
            make.set_cxxflags(self.session.build_cxxflags)
        if self.session.build_cpath:
            make.set_cpath(self.session.build_cpath)
        if self.session.build_library_path:
            make.set_library_path(self.session.build_library_path)
        make.run(build_args)

    def destroot(self):
        Make(self.session.build_path,
             self.session.debug).install(self.session.dest_dir)

    def clean(self):
        Make(self.session.build_path, self.session.debug).clean()

    def distclean(self):
        Make(self.session.build_path, self.session.debug).distclean()


class MakeSession(Session):

    build_cmd = MakeCmd
    clean_cmd = MakeCmd
    distclean_cmd = MakeCmd
    destroot_cmd = MakeCmd


class ConfigureCmd(SessionCmd):

    def configure(self):
        args = self.session.configure_args
        args.append("--prefix=" + self.session.prefix)
        args.append("--srcdir=" + self.session.configure_path)
        configure = Configure(args, self.session.configure_path,
                              self.session.build_path, self.session.debug)
        if self.session.configure_cc:
            configure.set_cc(self.session.configure_cc)
        if self.session.configure_cpp:
            configure.set_cpp(self.session.configure_cpp)
        if self.session.configure_cflags:
            configure.set_cflags(self.session.configure_cflags)
        if self.session.configure_cppflags:
            configure.set_cppflags(self.session.configure_cppflags)
        if self.session.configure_ldflags:
            configure.set_ldflags(self.session.configure_ldflags)
        if self.session.configure_libs:
            configure.set_libs(self.session.configure_libs)
        if self.session.configure_cxx:
            configure.set_cxx(self.session.configure_cxx)
        if self.session.configure_cxxflags:
            configure.set_cxxflags(self.session.configure_cxxflags)
        if self.session.configure_cpath:
            configure.set_cpath(self.session.configure_cpath)
        if self.session.configure_library_path:
            configure.set_library_path(self.session.configure_library_path)
        configure.run()

    def distclean(self):
        if self.session.src_path != self.session.build_path:
            Delete(self.session.build_dir).run()
        else:
            Make(self.session.build_path, self.session.debug).distclean()


class ConfigureSession(MakeSession):

    configure_cmd = ConfigureCmd
    distclean_cmd = ConfigureCmd


class CMakeCmd(SessionCmd):

    depends = ["cmake"]

    def configure(self):
        args = self.session.configure_args
        args.append("-DCMAKE_INSTALL_PREFIX=" + self.session.prefix)
        args.append("-DCMAKE_COLOR_MAKEFILE=TRUE")

        if self.session.verbose:
            args.append("-DCMAKE_VERBOSE_MAKEFILE=TRUE")

        CMake(args, self.session.configure_path, self.session.build_path,
              self.session.debug).run()

    def distclean(self):
        if self.session.src_path != self.session.build_path:
            Delete(self.session.build_dir).run()
        else:
            raise SessionError(self.session.name, "CMake is used to build the "
                               "session but src_path and build_path are set to "
                               "the same directory %s. Please use out of source"
                               " builds with CMake." % self.session.src_path)


class CMakeSession(MakeSession):

    configure_cmd = CMakeCmd
    distclean_cmd = CMakeCmd


class Python(object):

    depends = ["python"]

    def __init__(self, session):
        self.session = session

    def configure(self):
        Copy(self.session.src_path + "/*", self.session.build_path).run()

    def build(self):
        args = ["setup.py", "build"]
        args.extend(self.session.build_args)
        Command("python", args, self.session.build_path,
                self.session.debug).run()

    def destroot(self):
        Command("python", ["setup.py", "install", 
                "--prefix="+ self.session.prefix,
                "--root=" + self.session.dest_dir,
                # root implies single-version-externally-managed
                # "--single-version-externally-managed"
                ],
                self.session.build_path,
                self.session.debug).run()

    def clean(self):
        Command("python", ["setup.py", "clean"], self.session.build_path,
                self.session.debug).run()

    def distclean(self):
        pass


class PythonSession(Session):

    build_cmd = Python
    configure_cmd = Python
    destroot_cmd = Python
    clean_cmd = Python
    distclean_cmd = Python


class PythonDevelopSession(PythonSession):

    extract_cmd = None
    download_cmd = None

    def init(self):
        self.python_version = ".".join(
                        [str(value) for value in sys.version_info[:2]])
        self.python_package_path = os.path.join("lib",
                                                "python" + self.python_version,
                                                "site-packages")
        self.python_path = os.path.join(self.dest_path,
                                        self.python_package_path)

    def configure(self):
        pass

    def build(self):
        pass

    def destroot(self):
        cmd = Command("python", ["setup.py", "develop",
                      "--prefix=" + self.dest_path,
                      "--no-deps"],
                      self.build_path,
                      self.debug)
        if not os.path.exists(self.python_path):
            os.makedirs(self.python_path)
        cmd.set_env("PYTHONPATH", self.python_path)
        cmd.run()

    def post_destroot(self):
        Delete(os.path.join(self.python_path, "site.py")).run()
        Delete(os.path.join(self.python_path, "site.pyc")).run()
        Delete(os.path.join(self.python_path, "easy-install.pth")).run()

    def post_activate(self):
        self.read_kaizen_pth()
        self.add_kaizen_pth_entry()
        self.write_kaizen_pth()

    def post_deactivate(self):
        self.read_kaizen_pth()
        self.delete_kaizen_pth()
        self.write_kaizen_pth()

    def read_kaizen_pth(self):
        self.entries = []
        pth_file = os.path.join(self.prefix, self.python_package_path,
                                "kaizen-sessions.pth")
        if not os.path.isfile(pth_file):
            return
        f = open(pth_file, "r")
        try:
            for line in f:
                if line:
                    if "\n" in line:
                        # remove newline
                        self.entries.append(line[:-1])
                    else:
                        self.entries.append(line)
        finally:
            f.close()

        self.log.debug("Current kaizen-sessions.pth entries are %r" % self.entries)

    def add_kaizen_pth_entry(self):
        if self.build_path not in self.entries:
            self.log.debug("adding kaizen-session.pth entry '%s'" % \
                           self.build_path)
            self.entries.append(self.build_path)

    def delete_kaizen_pth(self):
        if self.build_path in self.entries:
            self.log.debug("removing kaizen-session.pth entry '%s'" % \
                           self.build_path)
            self.entries.remove(self.build_path)

    def write_kaizen_pth(self):
        f = open(os.path.join(self.prefix, self.python_package_path,
                              "kaizen-sessions.pth"), "w")
        try:
            num = len(self.entries)
            for i, entry in enumerate(self.entries):
                f.write(entry)
                if i+1 < num:
                    f.write("\n")
        finally:
            f.close()


class GitSession(Session):

    depends = ["python-dulwich"]

    @classmethod
    def get_version(cls):
        from dulwich.repo import Repo
        repo = Repo(cls.src_path)
        return cls.version + "git" + repo.head()
