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

import sys
import os
import os.path

from kaizen.logging.log import getLogger
from kaizen.rules.error import RulesError
from kaizen.rules.rules import Rules
from kaizen.system.command import Configure, CMake, Make, Command, Copy, Delete

class RulesCmd(object):

    depends = []

    def __init__(self, rules):
        self.log = getLogger(self)
        self.rules = rules


class MakeCmd(RulesCmd):

    def build(self):
        j = self.rules.config.get("buildjobs")

        if self.rules.parallel and j > 1:
            build_args = ["-j" + str(j)] + self.rules.build_args
        else:
            build_args = self.rules.build_args

        make = Make(self.rules.build_path, self.rules.debug)
        if self.rules.build_env:
            make.update_env(self.rules.build_env)
        if self.rules.build_cc:
            make.set_cc(self.rules.build_cc)
        if self.rules.build_cpp:
            make.set_cpp(self.rules.build_cpp)
        if self.rules.build_cxx:
            make.set_cxx(self.rules.build_cxx)
        if self.rules.build_cflags:
            make.set_cflags(self.rules.build_cflags)
        if self.rules.build_cppflags:
            make.set_cppflags(self.rules.build_cppflags)
        if self.rules.build_ldflags:
            make.set_ldflags(self.rules.build_ldflags)
        if self.rules.build_libs:
            make.set_libs(self.rules.build_libs)
        if self.rules.build_cxx:
            make.set_cxx(self.rules.build_cxx)
        if self.rules.build_cxxflags:
            make.set_cxxflags(self.rules.build_cxxflags)
        if self.rules.build_cpath:
            make.set_cpath(self.rules.build_cpath)
        if self.rules.build_library_path:
            make.set_library_path(self.rules.build_library_path)
        make.run(build_args)

    def destroot(self):
        make = Make(self.rules.build_path, self.rules.debug)
        if self.rules.destroot_env:
            make.update_env(self.rules.destroot_env)

        make.install(self.rules.dest_dir)

    def clean(self):
        Make(self.rules.build_path, self.rules.debug).clean()

    def distclean(self):
        Make(self.rules.build_path, self.rules.debug).distclean()


class MakeRules(Rules):

    build_cmd = MakeCmd
    clean_cmd = MakeCmd
    distclean_cmd = MakeCmd
    destroot_cmd = MakeCmd


class ConfigureCmd(RulesCmd):

    def configure(self):
        args = self.rules.configure_args
        args.append("--prefix=" + self.rules.prefix)

        # add --srcdir parameter if configure is not run in the source directory
        if self.rules.configure_path != self.rules.src_path:
            args.append("--srcdir=" + self.rules.configure_path)

        configure = Configure(args, self.rules.configure_path,
                              self.rules.build_path, self.rules.debug)

        if self.rules.configure_env:
            configure.update_env(self.rules.configure_env)
        if self.rules.configure_cc:
            configure.set_cc(self.rules.configure_cc)
        if self.rules.configure_cpp:
            configure.set_cpp(self.rules.configure_cpp)
        if self.rules.configure_cxx:
            configure.set_cxx(self.rules.configure_cxx)
        if self.rules.configure_cflags:
            configure.set_cflags(self.rules.configure_cflags)
        if self.rules.configure_cppflags:
            configure.set_cppflags(self.rules.configure_cppflags)
        if self.rules.configure_ldflags:
            configure.set_ldflags(self.rules.configure_ldflags)
        if self.rules.configure_libs:
            configure.set_libs(self.rules.configure_libs)
        if self.rules.configure_cxx:
            configure.set_cxx(self.rules.configure_cxx)
        if self.rules.configure_cxxflags:
            configure.set_cxxflags(self.rules.configure_cxxflags)
        if self.rules.configure_cpath:
            configure.set_cpath(self.rules.configure_cpath)
        if self.rules.configure_library_path:
            configure.set_library_path(self.rules.configure_library_path)
        configure.run()

    def distclean(self):
        if self.rules.src_path != self.rules.build_path:
            Delete(self.rules.build_dir).run()
        else:
            Make(self.rules.build_path, self.rules.debug).distclean()


class ConfigureRules(MakeRules):

    configure_cmd = ConfigureCmd
    distclean_cmd = ConfigureCmd


class CMakeCmd(RulesCmd):

    depends = ["cmake"]

    def configure(self):
        args = self.rules.configure_args
        args.append("-DCMAKE_INSTALL_PREFIX=" + self.rules.prefix)
        args.append("-DCMAKE_COLOR_MAKEFILE=TRUE")

        if self.rules.verbose:
            args.append("-DCMAKE_VERBOSE_MAKEFILE=TRUE")

        CMake(args, self.rules.configure_path, self.rules.build_path,
              self.rules.debug).run()

    def distclean(self):
        if self.rules.src_path != self.rules.build_path:
            Delete(self.rules.build_dir).run()
        else:
            raise RulesError(self.rules.name, "CMake is used to build the "
                               "rules but src_path and build_path are set to "
                               "the same directory %s. Please use out of source"
                               " builds with CMake." % self.rules.src_path)


class CMakeRules(MakeRules):

    configure_cmd = CMakeCmd
    distclean_cmd = CMakeCmd


class PerlCmd(RulesCmd):

    depends = ["perl"]

    def configure(self):
        Copy(self.rules.src_path + "/*", self.rules.build_path).run()
        args = ["Makefile.PL"]
        if self.rules.configure_args:
            args.extend(self.rules.configure_args)
        args.append("PREFIX=" + self.rules.prefix)

        Command("perl", args, self.rules.build_path, self.rules.debug).run()

    def distclean(self):
        if self.rules.src_path != self.rules.build_path:
            Delete(self.rules.build_dir).run()
        else:
            Make(self.rules.build_path, self.rules.debug).distclean()


class PerlRules(MakeRules):

    configure_cmd = PerlCmd
    distclean_cmd = PerlCmd


class Python(object):

    depends = ["python"]

    def __init__(self, rules):
        self.rules = rules

    def configure(self):
        Copy(self.rules.src_path + "/*", self.rules.build_path).run()

    def build(self):
        args = ["setup.py", "build"]
        args.extend(self.rules.build_args)
        Command("python", args, self.rules.build_path,
                self.rules.debug).run()

    def destroot(self):
        Command("python", ["setup.py", "install",
                "--prefix="+ self.rules.prefix,
                "--root=" + self.rules.dest_dir,
                # root implies single-version-externally-managed
                # "--single-version-externally-managed"
                ],
                self.rules.build_path,
                self.rules.debug).run()

    def clean(self):
        Command("python", ["setup.py", "clean"], self.rules.build_path,
                self.rules.debug).run()

    def distclean(self):
        pass


class PythonRules(Rules):

    build_cmd = Python
    configure_cmd = Python
    destroot_cmd = Python
    clean_cmd = Python
    distclean_cmd = Python


class PythonDevelopRules(PythonRules):

    extract_cmd = None
    download_cmd = None
    _kaizen_pth = None

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

    def pre_activate(self):
        self.read_kaizen_pth()
        self.add_kaizen_pth_entry()
        self.write_kaizen_pth()

    def post_deactivate(self):
        self.read_kaizen_pth()
        self.delete_kaizen_pth()
        self.write_kaizen_pth()

    def get_kaizen_pth_path(self):
        if self._kaizen_pth is None:
            import site
            k_site = None
            for c_site in site.PREFIXES:
                if os.access(c_site, os.W_OK):
                    k_site = c_site
                    break
            if not k_site:
                if hasattr(site, "getusersitepackages"):
                    k_site = site.getusersitepackages()
                else:
                    k_site = site.USER_SITE
            self._kaizen_pth = os.path.join(k_site, "kaizen-rules.pth")
        return self._kaizen_pth


    def read_kaizen_pth(self):
        self.entries = []
        pth_file = self.get_kaizen_pth_path()
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

        self.log.debug("Current kaizen-rules.pth entries are %r" % self.entries)

    def add_kaizen_pth_entry(self):
        if self.python_path not in self.entries:
            self.log.debug("adding kaizen-rules.pth entry '%s'" % \
                           self.python_path)
            self.entries.append(self.python_path)

    def delete_kaizen_pth(self):
        if self.python_path in self.entries:
            self.log.debug("removing kaizen-rules.pth entry '%s'" % \
                           self.python_path)
            self.entries.remove(self.python_path)

    def write_kaizen_pth(self):
        self.log.debug("writing kaizen-rules.pth to '%s'" % \
                        self.get_kaizen_pth_path())
        with open(self.get_kaizen_pth_path(), "w") as f:
            num = len(self.entries)
            for i, entry in enumerate(self.entries):
                f.write(entry)
                if i+1 < num:
                    f.write("\n")


class GitRules(Rules):

    depends = ["python-dulwich"]

    @classmethod
    def get_version(cls):
        from dulwich.repo import Repo
        repo = Repo(cls.src_path)
        return cls.version + "git" + repo.head()
