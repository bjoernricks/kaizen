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

import os
import os.path
import sys
import unittest

test_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(test_dir, os.pardir, os.pardir))

from kaizen.system.command import Replace

class ReplaceTest(unittest.TestCase):

    def test_replace(self):
        in_txt = os.path.join(test_dir, "data", "in.txt")
        out_txt = os.path.join(test_dir, "data", "out.txt")
        tmp_txt = os.path.join(test_dir, "data", "tmp.txt")
        f = open(out_txt, "r")
        expected_result = f.read()
        Replace("text.", "replaced text!", in_txt, tmp_txt).run()
        f = open(tmp_txt, "r")
        actual_result = f.read()
        self.assertEqual(expected_result, actual_result)
        os.remove(tmp_txt)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ReplaceTest))
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
