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

import os
import os.path
import sys
import unittest

test_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(test_dir, os.pardir, os.pardir))

from jam.session.phase import get_phase_from_name, Phase

class PhaseTest(unittest.TestCase):

    def test_get_phase_from_name(self):
        phase = get_phase_from_name("None")
        self.assertEquals("None", phase.name)

        phase = get_phase_from_name("Downloaded")
        self.assertEquals("Downloaded", phase.name)

        phase = get_phase_from_name("Downloaded")
        self.assertEquals("Downloaded", phase.name)

        phase = get_phase_from_name("Downloaded")
        self.assertEquals("Downloaded", phase.name)

        phase = get_phase_from_name("Downloaded")
        self.assertEquals("Downloaded", phase.name)

        phase = get_phase_from_name("Downloaded")
        self.assertEquals("Downloaded", phase.name)

        phase = get_phase_from_name("Downloaded")
        self.assertEquals("Downloaded", phase.name)

        phase = get_phase_from_name("Downloaded")
        self.assertEquals("Downloaded", phase.name)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(PhaseTest))
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
