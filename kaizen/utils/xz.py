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

import tarfile

from cStringIO import StringIO as IO

import lzma


class XZFile(object):

    def __init__(self, filename):
        self.filename = filename

    def extractall(self, dest_dir):
        xz = lzma.LZMADecompressor()
        infile = open(self.filename, "r")
        data = xz.decompress(infile.read())
        infile.close()

        outfile = IO(data)
        tar = tarfile.open(fileobj=outfile, mode="r")
        tar.extractall(dest_dir)
        outfile.close()
