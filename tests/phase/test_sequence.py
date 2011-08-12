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
from jam.phase.sequence import Sequence, SequenceEntry, SequenceError


class SessionDummy():

    def __init__(self):
        self.phase = dict()
        self.name = "Dummy"

    def set(self, phase_name):
        self.phase[phase_name] = True

    def get(self, phase_name):
        return self.phase.get(phase_name)

    def download(self):
        self.set("download")

    def extract(self):
        self.set("extract")

    def patch(self):
        self.set("patch")

    def configure(self):
        self.set("configure")

    def build(self):
        self.set("build")

    def destroot(self):
        self.set("destroot")

    def activate(self):
        self.set("activate")

    def deactivate(self):
        self.set("deactivate")

    def install(self):
        self.set("install")

    def unpatch(self):
        self.set("unpatch")


class SequenceTest(unittest.TestCase):

    def setUp(self):
        self.phases = Phases()

    def test_add(self):
        required_phase = self.phases.get("None")
        result_phase = self.phases.get("Activated")
        sequence = Sequence("test_seq1", required_phase, result_phase)
        sequence.add(self.phases.get("Extracted"), "extract")
        sequence.add(self.phases.get("Built"), "build", True)

        self.assertEquals(2, len(sequence.sequence))
        seq1 = sequence.sequence[0]
        self.assertEquals(self.phases.get("Extracted"), seq1.phase)
        self.assertEquals("extract", seq1.method_name)
        self.assertFalse(seq1.always)

        seq2 = sequence.sequence[1]
        self.assertEquals(self.phases.get("Built"), seq2.phase)
        self.assertEquals("build", seq2.method_name)
        self.assertTrue(seq2.always)

    def test_required_phase(self):
        session_dummy = SessionDummy()
        required_phase = self.phases.get("Patched")
        result_phase = self.phases.get("Activated")
        sequence = Sequence("test_seq2", required_phase, result_phase)
        sequence.add(self.phases.get("Extracted"), "extract")
        sequence.add(self.phases.get("Built"), "build", True)
        current_phase = self.phases.get("Patched")
        sequence.call(session_dummy, current_phase)

        current_phase = self.phases.get("None")
        try:
            sequence.call(session_dummy, current_phase)
            self.fail("Current session phase is smaller then requred phase")
        except SequenceError:
            pass

    def test_call(self):
        session_dummy = SessionDummy()
        required_phase = self.phases.get("Patched")
        result_phase = self.phases.get("Activated")
        sequence = Sequence("test_seq2", required_phase, result_phase)
        sequence.add(self.phases.get("Extracted"), "extract")
        sequence.add(self.phases.get("Built"), "build", True)
        current_phase = self.phases.get("Patched")
        sequence.call(session_dummy, current_phase)

        self.assertFalse(session_dummy.get("extract"))
        self.assertTrue(session_dummy.get("build"))

        session_dummy = SessionDummy()
        required_phase = self.phases.get("None")
        result_phase = self.phases.get("Activated")
        sequence = Sequence("test_seq3", required_phase, result_phase)
        sequence.add(self.phases.get("Extracted"), "extract")
        sequence.add(self.phases.get("Built"), "build", True)
        current_phase = self.phases.get("None")
        sequence.call(session_dummy, current_phase)

        self.assertTrue(session_dummy.get("extract"))
        self.assertTrue(session_dummy.get("build"))

        session_dummy = SessionDummy()
        required_phase = self.phases.get("Patched")
        result_phase = self.phases.get("Activated")
        sequence = Sequence("test_seq4", required_phase, result_phase)
        sequence.add(self.phases.get("Extracted"), "extract")
        sequence.add(self.phases.get("Built"), "build", True)
        current_phase = self.phases.get("Built")
        sequence.call(session_dummy, current_phase)

        self.assertFalse(session_dummy.get("extract"))
        self.assertTrue(session_dummy.get("build"))

        session_dummy = SessionDummy()
        required_phase = self.phases.get("Patched")
        result_phase = self.phases.get("Activated")
        sequence = Sequence("test_seq5", required_phase, result_phase)
        sequence.add(self.phases.get("Extracted"), "extract")
        sequence.add(self.phases.get("Built"), "build", True)
        current_phase = self.phases.get("Activated")
        sequence.call(session_dummy, current_phase)

        self.assertFalse(session_dummy.get("extract"))
        self.assertTrue(session_dummy.get("build"))

        session_dummy = SessionDummy()
        required_phase = self.phases.get("None")
        result_phase = self.phases.get("Activated")
        sequence = Sequence("test_seq6", required_phase, result_phase)
        sequence.add(self.phases.get("Extracted"), "extract")
        sequence.add(self.phases.get("Built"), "build")
        current_phase = self.phases.get("None")
        sequence.call(session_dummy, current_phase)

        self.assertTrue(session_dummy.get("extract"))
        self.assertTrue(session_dummy.get("build"))

        session_dummy = SessionDummy()
        required_phase = self.phases.get("None")
        result_phase = self.phases.get("Activated")
        sequence = Sequence("test_seq7", required_phase, result_phase)
        sequence.add(self.phases.get("Extracted"), "extract")
        sequence.add(self.phases.get("Built"), "build")
        current_phase = self.phases.get("Extracted")
        sequence.call(session_dummy, current_phase)

        self.assertFalse(session_dummy.get("extract"))
        self.assertTrue(session_dummy.get("build"))

        session_dummy = SessionDummy()
        required_phase = self.phases.get("None")
        result_phase = self.phases.get("Activated")
        sequence = Sequence("test_seq8", required_phase, result_phase)
        sequence.add(self.phases.get("Extracted"), "extract")
        sequence.add(self.phases.get("Built"), "build")
        current_phase = self.phases.get("Built")
        sequence.call(session_dummy, current_phase)

        self.assertFalse(session_dummy.get("extract"))
        self.assertFalse(session_dummy.get("build"))

        session_dummy = SessionDummy()
        required_phase = self.phases.get("None")
        result_phase = self.phases.get("Activated")
        sequence = Sequence("test_seq9", required_phase, result_phase)
        sequence.add(self.phases.get("Extracted"), "extract")
        sequence.add(self.phases.get("Built"), "build")
        current_phase = self.phases.get("Activated")
        sequence.call(session_dummy, current_phase)

        self.assertFalse(session_dummy.get("extract"))
        self.assertFalse(session_dummy.get("build"))

    def test_parent_sequence(self):
        session_dummy = SessionDummy()
        required_phase = self.phases.get("None")
        result_phase = self.phases.get("Activated")
        sequence1 = Sequence("test_par_seq1", required_phase, result_phase)
        sequence1.add(self.phases.get("Extracted"), "extract")

        result_phase = self.phases.get("Built")
        sequence2 = Sequence("test_par_seq2", required_phase, result_phase,
                             sequence1)
        sequence2.add(self.phases.get("Built"), "build")
        current_phase = self.phases.get("None")
        sequence2.call(session_dummy, current_phase)

        self.assertTrue(session_dummy.get("extract"))
        self.assertTrue(session_dummy.get("build"))

        session_dummy = SessionDummy()
        required_phase = self.phases.get("None")
        result_phase = self.phases.get("Activated")
        sequence1 = Sequence("test_par_seq3", required_phase, result_phase)
        sequence1.add(self.phases.get("Extracted"), "extract")

        result_phase = self.phases.get("Built")
        sequence2 = Sequence("test_par_seq4", required_phase, result_phase,
                             sequence1)
        sequence2.add(self.phases.get("Built"), "build")
        current_phase = self.phases.get("Extracted")
        sequence2.call(session_dummy, current_phase)

        self.assertFalse(session_dummy.get("extract"))
        self.assertTrue(session_dummy.get("build"))

        session_dummy = SessionDummy()
        required_phase = self.phases.get("None")
        result_phase = self.phases.get("Activated")
        sequence1 = Sequence("test_par_seq5", required_phase, result_phase)
        sequence1.add(self.phases.get("Extracted"), "extract")

        result_phase = self.phases.get("Built")
        sequence2 = Sequence("test_par_seq6", required_phase, result_phase,
                             sequence1)
        sequence2.add(self.phases.get("Built"), "build")
        current_phase = self.phases.get("Built")
        sequence2.call(session_dummy, current_phase)

        self.assertFalse(session_dummy.get("extract"))
        self.assertFalse(session_dummy.get("build"))

        session_dummy = SessionDummy()
        required_phase = self.phases.get("None")
        result_phase = self.phases.get("Activated")
        sequence1 = Sequence("test_par_seq7", required_phase, result_phase)
        sequence1.add(self.phases.get("Extracted"), "extract", True)

        result_phase = self.phases.get("Built")
        sequence2 = Sequence("test_par_seq8", required_phase, result_phase,
                             sequence1)
        sequence2.add(self.phases.get("Built"), "build")
        current_phase = self.phases.get("Built")
        sequence2.call(session_dummy, current_phase)

        self.assertTrue(session_dummy.get("extract"))
        self.assertFalse(session_dummy.get("build"))

        session_dummy = SessionDummy()
        required_phase = self.phases.get("None")
        result_phase = self.phases.get("Activated")
        sequence1 = Sequence("test_par_seq9", required_phase, result_phase)
        sequence1.add(self.phases.get("Extracted"), "extract", True)

        result_phase = self.phases.get("Built")
        sequence2 = Sequence("test_par_seq10", required_phase, result_phase,
                             sequence1)
        sequence2.add(self.phases.get("Built"), "build", True)
        current_phase = self.phases.get("Built")
        sequence2.call(session_dummy, current_phase)

        self.assertTrue(session_dummy.get("extract"))
        self.assertTrue(session_dummy.get("build"))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(SequenceTest))
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
