# vim:fileencoding=utf-8:et::sw=4:ts=4:tw=80:

# jam - An advanced package manager for Free Software
#
# Copyright (C) 2011  Björn Ricks <bjoern.ricks@googlemail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os.path
import logging

import jam.run

from jam.utils import realpath

class BuildSystem(object):

    def __init__(self, args, src_dir, build_dir, verbose=False):
        self.args = args
        self.src_dir = src_dir
        self.build_dir = build_dir
        self.cwd_dir = realpath(build_dir)
        self.verbose = verbose
        self.log = logging.getLogger("jam.buildsystem")

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
        self.log = logging.getLogger("jam.make")

    def run(self, args=[]):
        cmd = ["make"]
        cmd.extend(args)
        self.log.debug("Make run '%s' in '%s'" % (cmd, self.cwd_dir))
        jam.run.call(cmd, not self.verbose, cwd=self.cwd_dir)

    def install(self, dest_dir=None):
        cmd = []
        if dest_dir:
            cmd.append("DESTDIR=" + dest_dir)
        cmd.append("install")
        self.run(args)
