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
import hashlib # requires python 2.5

class Hash(object):

    def __init__(self, filename):
        self.filename = filename
        self.md5 = None
        self.sha1 = None

    def md5(self):
        if not self.md5:
            self.md5 = self._calculate_hash(hashlib.md5)
        return self.md5
    def sha1(self):
        if not self.sha1:
            self.sha1 = self._calculate_hash(hashlibs.sha1)
        return self.sha1

    def _calculate_hash(self, hashalgorithm):
        """ calculates a hashof a file """
        if not os.path.isfile(filename):
            raise RuntimeError("Could not calculate hash. File not found: %s"
                                % self.filename)
        f = file(self.filename, 'rb')
        m = hashalgorithm()
        while True:
            d = f.read(8096)
            if not d:
               break
            m.update(d)
        f.close()
        return m.hexdigest()

def realpath(path):
    return os.path.abspath(os.path.expanduser(path))
