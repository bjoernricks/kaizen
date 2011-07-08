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

import jam.run
import jam.log

from jam.utils import realpath

class BuildSystem(object):

    def __init__(self, args, src_dir, build_dir, verbose=False):
        self.args = args
        self.src_dir = src_dir
        self.build_dir = build_dir
        self.cwd_dir = realpath(build_dir)
        self.verbose = verbose
        self.log = jam.log.getLogger("jam.buildsystem")

    def run(self):
        pass

class Configure(BuildSystem):
    
    def run(self):
        cmd = [os.path.join(self.src_dir, "configure")]
        cmd.extend(self.args)
        self.log.debug("Configure run '%s' in '%s'" % (cmd, self.cwd_dir))
        jam.run.call(cmd, not self.verbose, cwd=self.cwd_dir)

class CMake(BuildSystem):

    def run(self):
        cmd = ["cmake"]
        cmd.extend(args)
        cmd.append(realpath(self.src_dir))
        self.log.debug("CMake run '%s' in '%s'" % (cmd, self.cwd_dir))
        jam.run.call(cmd, not self.verbose, cwd=self.cwd_dir)

class Make(object):

    def __init__(self, dir, verbose=False):
        self.dir = dir
        self.cwd_dir = realpath(dir)
        self.verbose = verbose
        self.log = jam.log.getLogger("jam.make")

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
        self.cwd_dir = realpath(cwd)
        self.verbose = verbose
        self.log = jam.log.getLogger("jam.command")

    def run(self):
        cmd = [self.cmd]
        for arg in self.args:
            new_arg = arg.split()
            cmd.extend(new_arg)
        self.log.debug("Running command '%s' in '%s'" % (cmd, self.cwd_dir))
        jam.run.call(cmd, not self.verbose, cwd=self.cwd_dir)


class Copy(object):

    def __init__(self, src, dest):
        self.log = jam.log.getLogger("jam.copy")
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

