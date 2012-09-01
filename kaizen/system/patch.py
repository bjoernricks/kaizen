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

import os.path

import kaizen.logging

from kaizen.system.command import Patch, Command


class PatchSystem(object):

    depends = []

    def __init__(self, work_dir, patch_dir, patches=None, verbose=False):
        """ work_dir  - path to the directory where the patches should
                        be apllied 
            patch_dir - path to the directory where the patches can be found
            patches   - list of patches
        """
        self.work_dir = work_dir
        self.patches = patches
        self.patch_dir = patch_dir
        self.verbose = verbose
        cls = self.__class__
        self.log = kaizen.logging.getLogger("%s.%s" % (cls.__module__,
                                                    cls.__name__))

    def push(self):
        """ Apply next patch """
        pass

    def pop(self):
        """ Revert last patch """
        pass

    def apply(self):
        """ Apply all patches """
        pass

    def unapply(self):
        """ Revert all patches"""
        pass


class Simple(PatchSystem):

    def __init__(self, work_dir, patch_dir, patches, verbose=False):
        super(Simple, self).__init__(work_dir, patch_dir, patches, verbose)
        if self.patches:
            self.next_patch = 0
            self.num_patches = len(self.patches)
        else:
            self.num_patches = 0

    def push(self):
        if not self.patches:
            return
        if self.next_patch >= self.num_patches:
            # all patches are applied
            self.log.debug("All patches are applied")
            return
        patch_name = self.patches[self.next_patch]
        patch = os.path.join(self.patch_dir, patch_name)
        self.log.info("Applying patch '%s' from '%s'" % (patch_name, patch))
        Patch(patch, self.work_dir, self.verbose).run()
        self.next_patch += 1

    def pop(self):
        if not self.patches:
            return
        current_patch = self.num_patches - self.next_patch - 1
        if current_patch < 0:
            # all patches are reverted
            self.log.debug("All patches are unappied")
            return
        patch_name = self.patches[current_patch]
        patch = os.path.join(self.patch_dir, patch_name)
        self.log.info("Unapplying patch '%s' from '%s'" % (patch_name, patch))
        Patch(patch, self.work_dir,
                self.verbose, reverse=True).run()
        self.next_patch += 1

    def apply(self):
        for i in range(self.num_patches):
            self.push()

    def unapply(self):
        for i in range(self.num_patches):
            self.pop()


class Quilt(PatchSystem):

    depends = ["quilt"]

    def __init__(self, work_dir, patch_dir, patches, verbose=False):
        super(Quilt, self).__init__(work_dir, patch_dir, patches, verbose)
        self.quilt = Command("quilt", [], self.work_dir, self.verbose)
        self.quilt.set_env("QUILT_PATCHES", self.patch_dir)

    def push(self):
        """ Apply next patch """
        self.quilt.set_args(["push"])
        self.quilt.run()

    def pop(self):
        """ Revert last patch """
        self.quilt.set_args(["pop"])
        self.quilt.run()

    def apply(self):
        """ Apply all patches """
        self.quilt.set_args(["push", "-a"])
        self.quilt.run()

    def unapply(self):
        """ Revert all patches"""
        self.quilt.set_args(["pop", "-a"])
        self.quilt.run()

    def refresh(self):
        """ Refresh current patch """
        self.quilt.set_args(["refresh"])
        self.quilt.run()

    def new(self, patch_name):
        """ Create a new patch """
        self.quilt.set_args(["new", patch_name])
        self.quilt.run()

    def delete(self):
        """ Delete the current patch """
        self.quilt.set_args(["delete"])
        self.quilt.run()

    def import_patches(self, patches):
        """ Import list of patches """
        args = ["import"]
        args.extend(patches)
        self.quilt.set_args(args)
        self.quilt.run()

    def edit(self, file_names):
        """ Edit file(s) to create patch """
        args = ["edit"]
        args.extend(file_names)
        self.quilt.set_args(args)
        self.quilt.run()
