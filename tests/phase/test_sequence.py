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

from jam.phase.phase import Phase, phases_list
from jam.phase.sequence import Sequence, SequenceError, UnSequence

import jam.log

jam.log.getRootLogger().set_level(jam.log.Logger.NONE)

class SessionDummy():

    def __init__(self):
        self.methods = dict()
        self.session_name = "Dummy"
        self.result_phases = []
        self.current_phase = None
        self.phases = []

    def set(self, method_name):
        self.methods[method_name] = True

    def get(self, phase_name):
        return self.methods.get(phase_name)

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

    def delete_destroot(self):
        self.set("delete_destroot")

    def delete_build(self):
        self.set("delete_build")

    def delete_source(self):
        self.set("delete_source")

    def delete_download(self):
        self.set("delete_download")

    def set_current_phase(self, phase):
        self.result_phases.append(phase)
        self.current_phase = phase

    def get_current_phase(self):
        return self.current_phase

    def set_local_current_phase(self, phase):
        self.current_phase = phase

    def get_phases(self):
        return self.phases

    def set_phase(self, phase):
        if phase not in self.phases:
            self.phases.append(phase)

    def unset_phase(self, phase):
        if phase in self.phases:
            self.phases.remove(phase)

    def set_test_phases(self, phases):
        self.phases = phases


class SequenceTest(unittest.TestCase):

    def test_must_be_called(self):
        session = SessionDummy()
        sequence = Sequence("mysequence", phases_list.get("Built"),
                            phases_list.get("Activated"), ["mymethod"])
        # result phase in session phase => must not
        session.set_test_phases([phases_list.get("Activated")])
        self.assertFalse(sequence.must_be_called(session))

        # result phase in session phase but always => must
        sequence.always = True
        self.assertTrue(sequence.must_be_called(session))

        # not always but result phase not in session phase
        sequence.always = False
        session.set_test_phases([])
        self.assertTrue(sequence.must_be_called(session))

        # result phase in session phases => run
        session = SessionDummy()
        sequence = UnSequence("mysequence", phases_list.get("Built"),
                              phases_list.get("Activated"),
                              phases_list.get("Activated"), ["mydropmethod"])
        session.set_test_phases([phases_list.get("Activated")])

        self.assertTrue(sequence.must_be_called(session))

        # result phase not in session phases => not run
        session.set_test_phases([])
        self.assertFalse(sequence.must_be_called(session))

        # result phase not in session phases but always is set => run
        sequence.always = True
        self.assertTrue(sequence.must_be_called(session))

    def test_required_phase(self):
        session_dummy = SessionDummy()
        required_phase = phases_list.get("Patched")
        result_phase = phases_list.get("Activated")
        sequence = Sequence("test_seq2", required_phase, result_phase,
                            ["extract"])
        # Patched == Patched => run
        session_dummy.set_local_current_phase(phases_list.get("Patched"))
        sequence(session_dummy)

        # Activated > Patched => run
        session_dummy.set_local_current_phase(phases_list.get("Activated"))
        sequence(session_dummy)

        # None < Patched => Error
        session_dummy.set_local_current_phase(phases_list.get("None"))
        try:
            sequence(session_dummy)
            self.fail("Current session phase is smaller then requred phase")
        except SequenceError:
            pass

        session_dummy = SessionDummy()
        required_phase = phases_list.get("Patched")
        result_phase = phases_list.get("Activated")
        sequence = UnSequence("test_unseq2", required_phase, result_phase,
                              result_phase, ["uninstall"])
        # Patched == Patched => run
        session_dummy.set_local_current_phase(phases_list.get("Patched"))
        sequence(session_dummy)

        # Activated > Patched => run
        session_dummy.set_local_current_phase(phases_list.get("Activated"))
        sequence(session_dummy)

        # None < Patched => Error
        session_dummy.set_local_current_phase(phases_list.get("None"))
        try:
            sequence(session_dummy)
            self.fail("Current session phase is smaller then requred phase")
        except SequenceError:
            pass

    def test_call_methods(self):
        session_dummy = SessionDummy()
        required_phase = phases_list.get("Patched")
        result_phase = phases_list.get("Activated")
        sequence = Sequence("test_seq2", required_phase, result_phase, [])

        self.assertEquals(session_dummy.get_phases(), [])
        self.assertEquals(session_dummy.methods, dict()) 

        sequence.method_names = ["build"]
        sequence.call_methods(session_dummy)
        self.assertTrue(session_dummy.get("build"))

        session_dummy = SessionDummy()
        sequence.method_names = ["build", "activate"]
        sequence.call_methods(session_dummy)
        self.assertTrue(session_dummy.get("build"))
        self.assertTrue(session_dummy.get("activate"))

        session_dummy = SessionDummy()
        sequence.method_names = ["build", session_dummy.activate]
        sequence.call_methods(session_dummy)
        self.assertTrue(session_dummy.get("build"))
        self.assertTrue(session_dummy.get("activate"))

        session_dummy = SessionDummy()
        sequence.method_names = [session_dummy.build, session_dummy.activate]
        sequence.call_methods(session_dummy)
        self.assertTrue(session_dummy.get("build"))
        self.assertTrue(session_dummy.get("activate"))

    def test_call(self):
        session_dummy = SessionDummy()
        required_phase = phases_list.get("Patched")
        result_phase = phases_list.get("Built")
        sequence = Sequence("test_seq2", required_phase, result_phase,
                            ["build"])

        # current phase < result phase and result phase not in session 
        # phases => run
        self.assertEquals(session_dummy.get_phases(), [])
        session_dummy.set_local_current_phase(phases_list.get("Patched"))
        sequence.call(session_dummy)
        self.assertTrue(session_dummy.get("build"))

        # current phase == result phase but result phase not in session
        # phases => run
        session_dummy = SessionDummy()
        self.assertEquals(session_dummy.get_phases(), [])
        session_dummy.set_local_current_phase(phases_list.get("Built"))
        sequence.call(session_dummy)
        self.assertTrue(session_dummy.get("build"))

        # result phase in session phases => not run
        session_dummy = SessionDummy()
        self.assertEquals(session_dummy.get_phases(), [])
        session_dummy.set_test_phases([phases_list.get("Built")])
        self.assertEquals(len(session_dummy.get_phases()), 1)
        sequence.call(session_dummy)
        self.assertFalse(session_dummy.get("build"))
        self.assertEquals(len(session_dummy.get_phases()), 1)

        # result phase in session phases but force is set => run
        session_dummy = SessionDummy()
        self.assertEquals(session_dummy.get_phases(), [])
        session_dummy.set_test_phases([phases_list.get("Built")])
        self.assertEquals(len(session_dummy.get_phases()), 1)
        sequence.call(session_dummy, True)
        self.assertTrue(session_dummy.get("build"))
        self.assertEquals(len(session_dummy.get_phases()), 1)

        # test parent sequence calls
        sequence2 = Sequence("child_seq", required_phase,
                             phases_list.get("Configured"),
                             ["configure"], parent_seq=sequence)

        # Built and Configured not in session phases => run both
        session_dummy = SessionDummy()
        self.assertEquals(session_dummy.get_phases(), [])
        sequence2.call(session_dummy)
        self.assertTrue(session_dummy.get("build"))
        self.assertTrue(session_dummy.get("configure"))
        self.assertEquals(len(session_dummy.get_phases()), 2)

        # Configured in session phases => don't run
        session_dummy = SessionDummy()
        self.assertEquals(session_dummy.get_phases(), [])
        session_dummy.set_test_phases([phases_list.get("Configured")])
        self.assertEquals(len(session_dummy.get_phases()), 1)
        sequence2.call(session_dummy)
        self.assertFalse(session_dummy.get("build"))
        self.assertFalse(session_dummy.get("configure"))
        self.assertEquals(len(session_dummy.get_phases()), 1)

        # Built in session phases => run only configure
        session_dummy = SessionDummy()
        self.assertEquals(session_dummy.get_phases(), [])
        session_dummy.set_test_phases([phases_list.get("Built")])
        self.assertEquals(len(session_dummy.get_phases()), 1)
        sequence2.call(session_dummy)
        self.assertFalse(session_dummy.get("build"))
        self.assertTrue(session_dummy.get("configure"))
        self.assertEquals(len(session_dummy.get_phases()), 2)

        session_dummy = SessionDummy()
        required_phase = phases_list.get("Patched")
        result_phase = phases_list.get("Built")
        unsequence = UnSequence("test_seq2", required_phase, result_phase,
                                result_phase, ["deactivate"])

        # result phase in session phases => run
        session_dummy = SessionDummy()
        self.assertEquals(session_dummy.get_phases(), [])
        session_dummy.set_test_phases([phases_list.get("Built")])
        self.assertEquals(len(session_dummy.get_phases()), 1)
        unsequence.call(session_dummy)
        self.assertTrue(session_dummy.get("deactivate"))
        self.assertEquals(len(session_dummy.get_phases()), 0)

        # result phase not in session phases => not run
        session_dummy = SessionDummy()
        self.assertEquals(session_dummy.get_phases(), [])
        session_dummy.set_test_phases([phases_list.get("Configured")])
        unsequence.call(session_dummy)
        self.assertFalse(session_dummy.get("deactivate"))
        self.assertEquals(len(session_dummy.get_phases()), 1)

        # result phase not in session phases but force is set => run
        session_dummy = SessionDummy()
        self.assertEquals(session_dummy.get_phases(), [])
        unsequence.call(session_dummy, True)
        self.assertTrue(session_dummy.get("deactivate"))
        self.assertEquals(len(session_dummy.get_phases()), 0)

        session_dummy = SessionDummy()
        required_phase = phases_list.get("Patched")
        result_phase = phases_list.get("Built")
        unset_phase = phases_list.get("Built")
        unsequence = UnSequence("test_seq2", required_phase, result_phase,
                              unset_phase, ["delete_build"],
                              parent_seq=sequence)

        self.assertEquals(len(session_dummy.get_phases()), 0)
        unsequence.call(session_dummy)
        self.assertTrue(session_dummy.get("build"))
        self.assertTrue(session_dummy.get("delete_build"))
        self.assertEquals(len(session_dummy.get_phases()), 0)

        session_dummy = SessionDummy()
        session_dummy.set_test_phases([result_phase])
        unsequence.call(session_dummy)
        self.assertFalse(session_dummy.get("build"))
        self.assertTrue(session_dummy.get("delete_build"))
        self.assertEquals(len(session_dummy.get_phases()), 0)

        sequence2 = Sequence("child_seq", required_phase,
                             phases_list.get("Configured"),
                             ["configure"], parent_seq=unsequence)

        self.assertEquals(len(session_dummy.get_phases()), 0)
        sequence2.call(session_dummy)
        self.assertTrue(session_dummy.get("build"))
        self.assertTrue(session_dummy.get("delete_build"))
        self.assertTrue(session_dummy.get("configure"))
        self.assertEquals(len(session_dummy.get_phases()), 1)
        self.assertEquals(session_dummy.get_phases()[0],
                          phases_list.get("Configured"))

    def test__call__(self):
        session_dummy = SessionDummy()
        self.assertEquals(len(session_dummy.result_phases), 0)

        required_phase = phases_list.get("None")
        result_phase = phases_list.get("Configured")
        sequence = Sequence("configure", required_phase, result_phase,
                            ["configure"])
        session_dummy.set_local_current_phase(phases_list.get("None"))
        sequence(session_dummy)

        self.assertTrue(session_dummy.get("configure"))
        self.assertEquals(len(session_dummy.result_phases), 1)
        self.assertEquals(session_dummy.result_phases[0], result_phase)
        self.assertEquals(len(session_dummy.get_phases()), 1)
        self.assertEquals(session_dummy.get_current_phase(), result_phase)
        self.assertEquals(session_dummy.get_phases()[0], result_phase)

        # test two methods
        session_dummy = SessionDummy()
        sequence = Sequence("configure", required_phase, result_phase, ["build",
                            "configure"])
        session_dummy.set_local_current_phase(phases_list.get("Configured"))
        sequence(session_dummy)

        self.assertTrue(session_dummy.get("configure"))
        self.assertTrue(session_dummy.get("build"))
        self.assertEquals(len(session_dummy.result_phases), 1)
        self.assertEquals(session_dummy.result_phases[0], result_phase)
        self.assertEquals(session_dummy.get_current_phase(), result_phase)
        self.assertEquals(len(session_dummy.get_phases()), 1)
        self.assertEquals(session_dummy.get_phases()[0], result_phase)

        # test always = True (result_phase is in phases)
        session_dummy = SessionDummy()
        sequence = Sequence("test_seq5", required_phase, result_phase,
                            ["configure"], True)
        session_dummy.set_local_current_phase(phases_list.get("Configured"))
        session_dummy.set_test_phases([phases_list.get("Configured")])
        sequence(session_dummy)

        self.assertTrue(session_dummy.get("configure"))
        self.assertEquals(len(session_dummy.result_phases), 1)
        self.assertEquals(session_dummy.result_phases[0], result_phase)
        self.assertEquals(session_dummy.get_current_phase(), result_phase)
        self.assertEquals(len(session_dummy.get_phases()), 1)
        self.assertEquals(session_dummy.get_phases()[0], result_phase)

        # test force (result_phase is in phases but force is set)
        session_dummy = SessionDummy()
        sequence = Sequence("test_seq5", required_phase, result_phase,
                            ["configure"])
        session_dummy.set_local_current_phase(phases_list.get("Configured"))
        session_dummy.set_test_phases([phases_list.get("Configured")])
        sequence(session_dummy, True)

        self.assertTrue(session_dummy.get("configure"))
        self.assertEquals(len(session_dummy.result_phases), 1)
        self.assertEquals(session_dummy.result_phases[0], result_phase)
        self.assertEquals(session_dummy.get_current_phase(), result_phase)
        self.assertEquals(len(session_dummy.get_phases()), 1)
        self.assertEquals(session_dummy.get_phases()[0], result_phase)

    def test_parent_sequence(self):
        session_dummy = SessionDummy()
        required_phase = phases_list.get("None")
        result_phase1 = phases_list.get("Built")
        result_phase2 = phases_list.get("Configured")
        sequence1 = Sequence("build", required_phase, result_phase1,
                             ["build"])
        sequence2 = Sequence("configure", required_phase, result_phase2,
                            ["configure"], parent_seq=sequence1)

        session_dummy.set_local_current_phase(phases_list.get("None"))
        sequence2(session_dummy)

        self.assertTrue(session_dummy.get("build"))
        self.assertTrue(session_dummy.get("configure"))
        self.assertEquals(len(session_dummy.result_phases), 1)
        self.assertEquals(session_dummy.result_phases[0], result_phase2)
        self.assertEquals(len(session_dummy.get_phases()), 2)
        self.assertEquals(session_dummy.get_phases()[0], result_phase1)
        self.assertEquals(session_dummy.get_phases()[1], result_phase2)
        self.assertEquals(session_dummy.get_current_phase(), result_phase2)

        # phases contains built => run only configure 
        session_dummy = SessionDummy()
        session_dummy.set_test_phases([phases_list.get("Built")])
        session_dummy.set_local_current_phase(phases_list.get("None"))
        self.assertEquals(len(session_dummy.get_phases()), 1)
        self.assertEquals(session_dummy.get_phases()[0], result_phase1)

        sequence2(session_dummy)
        self.assertFalse(session_dummy.get("build"))
        self.assertTrue(session_dummy.get("configure"))
        self.assertEquals(len(session_dummy.result_phases), 1)
        self.assertEquals(session_dummy.result_phases[0], result_phase2)
        self.assertEquals(len(session_dummy.get_phases()), 2)
        self.assertEquals(session_dummy.get_phases()[0], result_phase1)
        self.assertEquals(session_dummy.get_phases()[1], result_phase2)
        self.assertEquals(session_dummy.get_current_phase(), result_phase2)

        # phases contains built and configure => not run
        session_dummy = SessionDummy()
        session_dummy.set_test_phases([phases_list.get("Built"),
                                       phases_list.get("Configured")])
        session_dummy.set_local_current_phase(phases_list.get("None"))
        self.assertEquals(len(session_dummy.result_phases), 0)
        self.assertEquals(len(session_dummy.get_phases()), 2)
        self.assertEquals(session_dummy.get_phases()[0], result_phase1)
        self.assertEquals(session_dummy.get_phases()[1], result_phase2)

        sequence2(session_dummy)
        self.assertFalse(session_dummy.get("build"))
        self.assertFalse(session_dummy.get("configure"))
        self.assertEquals(len(session_dummy.result_phases), 0)
        self.assertEquals(len(session_dummy.get_phases()), 2)
        self.assertEquals(session_dummy.get_current_phase(),
                          phases_list.get("None"))
        self.assertEquals(session_dummy.get_phases()[0], result_phase1)
        self.assertEquals(session_dummy.get_phases()[1], result_phase2)

        # phases contains built but force is set => run only configure
        session_dummy = SessionDummy()
        session_dummy.set_test_phases([phases_list.get("Built")])
        session_dummy.set_local_current_phase(phases_list.get("None"))
        self.assertEquals(len(session_dummy.get_phases()), 1)
        self.assertEquals(session_dummy.get_phases()[0], result_phase1)

        sequence2(session_dummy, True)
        self.assertFalse(session_dummy.get("build"))
        self.assertTrue(session_dummy.get("configure"))
        self.assertEquals(len(session_dummy.result_phases), 1)
        self.assertEquals(session_dummy.result_phases[0], result_phase2)
        self.assertEquals(len(session_dummy.get_phases()), 2)
        self.assertEquals(session_dummy.get_phases()[0], result_phase1)
        self.assertEquals(session_dummy.get_phases()[1], result_phase2)
        self.assertEquals(session_dummy.get_current_phase(), result_phase2)

        # phases contains built and configured but force is set
        # => run only configure
        session_dummy = SessionDummy()
        session_dummy.set_test_phases([phases_list.get("Built"), 
                                       phases_list.get("Configured")])
        session_dummy.set_local_current_phase(phases_list.get("None"))
        self.assertEquals(len(session_dummy.get_phases()), 2)
        self.assertEquals(session_dummy.get_phases()[0], result_phase1)
        self.assertEquals(session_dummy.get_phases()[1], result_phase2)

        sequence2(session_dummy, True)
        self.assertFalse(session_dummy.get("build"))
        self.assertTrue(session_dummy.get("configure"))
        self.assertEquals(len(session_dummy.result_phases), 1)
        self.assertEquals(session_dummy.result_phases[0], result_phase2)
        self.assertEquals(len(session_dummy.get_phases()), 2)
        self.assertEquals(session_dummy.get_phases()[0], result_phase1)
        self.assertEquals(session_dummy.get_phases()[1], result_phase2)
        self.assertEquals(session_dummy.get_current_phase(), result_phase2)

        # phase contains configured but force is set => run both
        session_dummy = SessionDummy()
        session_dummy.set_test_phases([phases_list.get("Configured")])
        session_dummy.set_local_current_phase(phases_list.get("None"))
        self.assertEquals(len(session_dummy.get_phases()), 1)
        self.assertEquals(session_dummy.get_phases()[0], result_phase2)

        sequence2(session_dummy, True)
        self.assertTrue(session_dummy.get("build"))
        self.assertTrue(session_dummy.get("configure"))
        self.assertEquals(len(session_dummy.result_phases), 1)
        self.assertEquals(session_dummy.result_phases[0], result_phase2)
        self.assertEquals(len(session_dummy.get_phases()), 2)
        self.assertEquals(session_dummy.get_phases()[0], result_phase2)
        self.assertEquals(session_dummy.get_phases()[1], result_phase1)
        self.assertEquals(session_dummy.get_current_phase(), result_phase2)

        # phases contains built and configured but always is set
        # => run only configure
        sequence3 = Sequence("test_par_seq2", required_phase, result_phase2,
                            ["configure"], True, sequence1)
        session_dummy = SessionDummy()
        session_dummy.set_test_phases([phases_list.get("Built"), 
                                       phases_list.get("Configured")])
        session_dummy.set_local_current_phase(phases_list.get("None"))
        self.assertEquals(len(session_dummy.get_phases()), 2)
        self.assertEquals(session_dummy.get_phases()[0], result_phase1)
        self.assertEquals(session_dummy.get_phases()[1], result_phase2)

        sequence3(session_dummy, True)
        self.assertFalse(session_dummy.get("build"))
        self.assertTrue(session_dummy.get("configure"))
        self.assertEquals(len(session_dummy.result_phases), 1)
        self.assertEquals(session_dummy.result_phases[0], result_phase2)
        self.assertEquals(len(session_dummy.get_phases()), 2)
        self.assertEquals(session_dummy.get_phases()[0], result_phase1)
        self.assertEquals(session_dummy.get_phases()[1], result_phase2)
        self.assertEquals(session_dummy.get_current_phase(), result_phase2)

        # phase contains configured but always is set => run both
        session_dummy = SessionDummy()
        session_dummy.set_test_phases([phases_list.get("Configured")])
        session_dummy.set_local_current_phase(phases_list.get("None"))
        self.assertEquals(len(session_dummy.get_phases()), 1)
        self.assertEquals(session_dummy.get_phases()[0], result_phase2)

        sequence3(session_dummy, True)
        self.assertTrue(session_dummy.get("build"))
        self.assertTrue(session_dummy.get("configure"))
        self.assertEquals(len(session_dummy.result_phases), 1)
        self.assertEquals(session_dummy.result_phases[0], result_phase2)
        self.assertEquals(len(session_dummy.get_phases()), 2)
        self.assertEquals(session_dummy.get_phases()[0], result_phase2)
        self.assertEquals(session_dummy.get_phases()[1], result_phase1)
        self.assertEquals(session_dummy.get_current_phase(), result_phase2)

        result_phase = phases_list.get("Configured")
        unset_phase = phases_list.get("Built")
        unsequence = UnSequence("delete_build", required_phase, result_phase,
                                unset_phase, ["delete_build"], False, sequence2)

        session_dummy = SessionDummy()
        session_dummy.set_local_current_phase(phases_list.get("None"))
        self.assertEquals(len(session_dummy.get_phases()), 0)
        unsequence(session_dummy)
        self.assertTrue(session_dummy.get("build"))
        self.assertTrue(session_dummy.get("configure"))
        self.assertTrue(session_dummy.get("delete_build"))
        self.assertEquals(len(session_dummy.result_phases), 1)
        self.assertEquals(session_dummy.result_phases[0], result_phase)
        self.assertEquals(len(session_dummy.get_phases()), 1)
        self.assertEquals(session_dummy.get_phases()[0], result_phase)
        self.assertEquals(session_dummy.get_current_phase(), result_phase)

        session_dummy = SessionDummy()
        session_dummy.set_local_current_phase(result_phase)
        session_dummy.set_test_phases([result_phase])

        # configured but build already deleted => not run
        unsequence(session_dummy)
        self.assertFalse(session_dummy.get("build"))
        self.assertFalse(session_dummy.get("configure"))
        self.assertFalse(session_dummy.get("delete_build"))
        self.assertEquals(len(session_dummy.result_phases), 0)
        self.assertEquals(len(session_dummy.get_phases()), 1)
        self.assertEquals(session_dummy.get_phases()[0], result_phase)
        self.assertEquals(session_dummy.get_current_phase(), result_phase)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(SequenceTest))
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
