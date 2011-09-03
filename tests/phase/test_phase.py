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

from jam.phase.phase import Phase, Phases

class PhasesTest(unittest.TestCase):

    def test_get(self):
        phases = Phases()
        phase = phases.get("None")
        self.assertEquals("None", phase.name)

        phase = phases.get("Downloaded")
        self.assertEquals("Downloaded", phase.name)

        phase = phases.get("Extracted")
        self.assertEquals("Extracted", phase.name)

        phase = phases.get("Patched")
        self.assertEquals("Patched", phase.name)

        phase = phases.get("Configured")
        self.assertEquals("Configured", phase.name)

        phase = phases.get("Built")
        self.assertEquals("Built", phase.name)

        phase = phases.get("Destrooted")
        self.assertEquals("Destrooted", phase.name)

        phase = phases.get("Activated")
        self.assertEquals("Activated", phase.name)

        try:
            phases.get("abc")
            self.fail("phase abc doesn't exists")
        except KeyError:
            pass

    def test_compare(self):
        phases = Phases()
        phasenone1 = phases.get("None")
        phasenone2 = phases.get("None")
        self.assertTrue(phasenone1 == phasenone2)

        phasedownloaded = phases.get("Downloaded")
        self.assertTrue(phasenone1 < phasedownloaded)
        self.assertTrue(phasedownloaded > phasenone1)

        phaseextracted = phases.get("Extracted")
        self.assertTrue(phaseextracted > phasedownloaded)

        phasepatched = phases.get("Patched")
        self.assertTrue(phasepatched > phaseextracted)

        phaseconfigured = phases.get("Configured")
        self.assertTrue(phaseconfigured > phasepatched)

        phasebuilt = phases.get("Built")
        self.assertTrue(phasebuilt > phaseconfigured)

        phasedestrooted = phases.get("Destrooted")
        self.assertTrue(phasedestrooted > phasebuilt)

        phaseactivated = phases.get("Activated")
        self.assertTrue(phaseactivated > phasedestrooted)


class PhaseTest(unittest.TestCase):

    def test_equal(self):
        phasenone1 = Phase("None", 0)
        phasenone2 = Phase("None", 0)
        self.assertEquals(phasenone1, phasenone2)

        phasedownloaded = Phase("Downloaded", 1)
        self.assertNotEquals(phasenone1, phasedownloaded)

    def test_compare(self):
        phasenone1 = Phase("None", 0)
        phasenone2 = Phase("None", 0)
        self.assertTrue(phasenone1 == phasenone2)

        phasedownloaded = Phase("Downloaded", 1)
        self.assertTrue(phasenone1 < phasedownloaded)
        self.assertTrue(phasedownloaded > phasenone1)

        phaseextracted = Phase("Extracted", 2)
        self.assertTrue(phaseextracted > phasedownloaded)
        self.assertTrue(phaseextracted > phasenone1)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(PhasesTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(PhaseTest))
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
