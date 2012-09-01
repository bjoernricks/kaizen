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

import os.path

from kaizen.error import KaizenRuntimeError

try:
    from hashlib import md5 # requires python 2.5
    from hashlib import sha1 # requires python 2.5
except ImportError:
    from md5 import new as md5
    from sha import new as sha1

class Hash(object):

    def __init__(self, filename):
        self.filename = filename
        self.md5_value = None
        self.sha1_value = None

    def md5(self):
        if not self.md5_value:
            self.md5_value = self._calculate_hash(md5)
        return self.md5_value

    def sha1(self):
        if not self.sha1_value:
            self.sha1_value = self._calculate_hash(sha1)
        return self.sha1_value

    def _calculate_hash(self, hashalgorithm):
        """ calculates a hash of a file """
        if not os.path.isfile(self.filename):
            raise KaizenRuntimeError("Could not calculate hash. File not found: %s"
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
