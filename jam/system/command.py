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
import logging
import shutil
import re

import jam.run
import jam.logging

from jam.utils import real_path

class BuildSystem(object):

    def __init__(self, args, src_dir, build_dir, verbose=False):
        self.args = args
        self.src_dir = src_dir
        self.build_dir = build_dir
        self.cwd_dir = real_path(build_dir)
        self.verbose = verbose
        self.env = dict()
        self.log = jam.logging.getLogger("jam.buildsystem")

    def set_cc(self, cc):
        self.env["CC"] = cc

    def set_cpp(self, cpp):
        self.env["CPP"] = cpp

    def set_cflags(self, cflags=[]):
        self.env["CFLAGS"] = " ".join(cflags)

    def set_cppflags(self, cppflags=[]):
        self.env["CPPFLAGS"] = " ".join(cppflags)

    def set_ldflags(self, ldflags=[]):
        self.env["LDFLAGS"] = " ".join(ldflags)

    def set_libs(self, libs=[]):
        self.env["LIBS"] = " ".join(libs)

    def set_cxx(self, cxx):
        self.env["CXX"] = cxx

    def set_cxxflags(self, cxxflags=[]):
        self.env["CXXFLAGS"] = " ".join(cxxflags)

    def run(self):
        pass


class Configure(BuildSystem):

    def run(self):
        cmd = [os.path.join(self.src_dir, "configure")]
        cmd.extend(self.args)
        self.log.debug("Configure run '%s' in '%s' with env '%s'" % (cmd,
                        self.cwd_dir, self.env))
        jam.run.call(cmd, not self.verbose, extra_env=self.env,
                     cwd=self.cwd_dir)


class CMake(BuildSystem):

    def run(self):
        cmd = ["cmake"]
        cmd.extend(self.args)
        cmd.append(real_path(self.src_dir))
        self.log.debug("CMake run '%s' in '%s' with env '%s'" % (cmd,
                       self.cwd_dir, self.env))
        jam.run.call(cmd, not self.verbose, extra_env=self.env,
                     cwd=self.cwd_dir)


class Make(object):

    def __init__(self, dir, verbose=False):
        self.dir = dir
        self.cwd_dir = real_path(dir)
        self.verbose = verbose
        self.log = jam.logging.getLogger("jam.make")

    def run(self, args=[]):
        cmd = ["make"]
        cmd.extend(args)
        self.log.debug("Make run '%s' in '%s'" % (cmd, self.cwd_dir))
        jam.run.call(cmd, not self.verbose, cwd=self.cwd_dir)

    def install(self, dest_dir=None):
        args = []
        if dest_dir:
            args.append("DESTDIR=" + dest_dir)
        args.append("install")
        self.run(args)

    def clean(self):
        self.run(["clean"])

    def distclean(self):
        self.run(["distclean"])


class Command(object):

    def __init__(self, cmd, args, cwd, verbose):
        self.cmd = cmd
        self.args = args
        self.cwd_dir = real_path(cwd)
        self.verbose = verbose
        self.log = jam.logging.getLogger("jam.command")
        self.env = dict()

    def set_env(self, key, value):
        self.env[key] = value

    def run(self):
        cmd = [self.cmd]
        for arg in self.args:
            new_arg = arg.split()
            cmd.extend(new_arg)
        self.log.debug("Running command '%s' in '%s' with env %s" % (cmd,
            self.cwd_dir, self.env))
        jam.run.call(cmd, not self.verbose, cwd=self.cwd_dir, extra_env=self.env)

    def set_args(self, args):
        self.args = args


class Patch(Command):

    def __init__(self, patchfile, cwd, verbose, reverse=False, num=1):
        args = []
        if reverse:
            args.append("-R")
        args.extend(["-p" + str(num), "-i", patchfile])
        super(Patch, self).__init__("patch", args, cwd, verbose)


class Copy(object):

    def __init__(self, src, dest):
        self.log = jam.logging.getLogger(__name__ + ".copy")
        self.src = src
        self.dest = dest

    def run(self):
        if os.path.isdir(self.src):
            if os.path.exists(self.dest):
                if os.listdir(self.dest):
                    self.log.debug("Skipping copy. Destination '%s'"
                                   " already exists" % self.dest)
                    return
                else:
                    os.rmdir(self.dest)
            self.log.debug("Copy directory '%s' to '%s'" % (self.src,
                                                            self.dest))
            shutil.copytree(self.src, self.dest)
        else:
            if os.path.isdir(self.dest):
                dest_dir = self.dest
            else:
                dest_dir = os.path.dirname(self.dest)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            self.log.debug("Copy file '%s' to '%s'" % (self.src, self.dest))
            shutil.copy(self.src, self.dest)


class Move(object):

    def __init__(self, src, dest):
        self.log = jam.logging.getLogger(__name__ + ".move")
        self.src = src
        self.dest = dest

    def run(self):
        self.log.debug("Moving '%s' to '%s'" % (self.src, self.dest))
        shutil.move(self.src, self.dest)


class Replace(object):

    def __init__(self, pattern, replace, source, dest=None):
        self.log = jam.logging.getLogger(__name__ + ".replace")
        self.pattern = pattern
        self.replace = replace
        self.source = source
        self.dest = dest
        if not self.dest:
            self.dest = source

    def run(self):
        if not os.path.isfile(self.source):
            #TODO raise exception
            self.log.error("Can't replace '%s' in file '%s'. File does not " \
                           "exist." % (self.pattern, self.source))
            return
        self.log.debug("Replacing '%s' with '%s' in file '%s'." % (self.pattern,
                                                                   self.replace,
                                                                   self.source))
        f = open(self.source, "r")
        content = f.read()
        f.close()
        replaced = re.sub(self.pattern, self.replace, content)
        f = open(self.dest, "w")
        f.write(replaced)
        f.close()


class Delete(object):

    def __init__(self, dir):
        self.dir = dir
        self.log = jam.logging.getLogger(__name__ + ".delete")

    def run(self):
        # TODO: delete only content of dir
        #       delete also content of symlinks shutil.rmtree doesn't work for
        #       symlinks
        #       add parameter fail_if_not_exists and raise an exception
        if os.path.isdir(self.dir):
            self.log.debug("deleting directory '%s' recursively" % self.dir)
            shutil.rmtree(self.dir)
        elif os.path.isfile(self.dir):
            self.log.debug("deleting file '%s'" % self.dir)
            os.remove(self.dir)
        else:
            self.log.error("Could not delete '%s'. It's not a file or directory"
                    % self.dir)
