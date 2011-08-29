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

import jam.log
from jam.session import Session
from jam.session.wrapper import SessionLoader, SessionValidator

class MySession(Session):
    pass


logger = jam.log.getLogger("jam").set_level(jam.log.Logger.NONE)

class TestConfig(object):

    def __init__(self):
        self.config = {}
        self.config["jam_sessions"] = os.path.join(test_dir, "session")

    def get(self, value):
        return self.config.get(value, None)

class SessionLoaderTest(unittest.TestCase):

    def test_load(self):
        config = TestConfig()
        loader = SessionLoader(config)

        module = loader.module("testsession")
        self.assertTrue(module)
        self.assertEquals("testsession", module.__name__)

        classes = loader.classes("testsession")
        self.assertEquals(2, len(classes))

        sessions = loader.sessions("testsession")
        self.assertEquals(1, len(sessions))

        session = loader.load("testsession")
        self.assertTrue(session)
        instance = session(config, "session",
                           "session", "session")
        self.assertTrue(instance)
        self.assertTrue(instance.build())
        self.assertEquals(1, instance.my_method())

        session = loader.load("notestsession")
        self.assertFalse(session)

    def test_load_derived(self):
        config = TestConfig()
        loader = SessionLoader(config)

        module = loader.module("derivedsession")
        self.assertTrue(module)
        self.assertEquals("derivedsession", module.__name__)

        classes = loader.classes("derivedsession")
        self.assertEquals(1, len(classes))

        sessions = loader.sessions("derivedsession")
        self.assertEquals(1, len(sessions))

        session = loader.load("derivedsession")
        self.assertTrue(session)
        self.assertEquals("1.0.abc", session.version)
        instance = session(config, "session",
                           "session", "session")
        self.assertTrue(instance)

    def test_load_sub(self):

        config = TestConfig()
        loader = SessionLoader(config)

        module = loader.module("subtest.subsession")
        self.assertTrue(module)
        self.assertEquals("subtest.subsession", module.__name__)

        classes = loader.classes("subtest.subsession")
        self.assertEquals(1, len(classes))

        sessions = loader.sessions("subtest.subsession")
        self.assertEquals(1, len(sessions))

        session = loader.load("subtest.subsession")
        self.assertTrue(session)
        self.assertEquals("x.y.z", session.version)
        instance = session(config, "session",
                           "session", "session")
        self.assertTrue(instance)

        module = loader.module("subtest.derivedsession")
        self.assertTrue(module)
        self.assertEquals("subtest.derivedsession", module.__name__)

        classes = loader.classes("subtest.derivedsession")
        self.assertEquals(1, len(classes))

        sessions = loader.sessions("subtest.derivedsession")
        self.assertEquals(1, len(sessions))

        session = loader.load("subtest.derivedsession")
        self.assertTrue(session)
        self.assertEquals("olla", session.version)
        instance = session(config, "session",
                           "session", "session")
        self.assertTrue(instance)

class SessionValidatorTest(unittest.TestCase):

    def setUp(self):
        self.config = TestConfig()
        self.loader = SessionLoader(self.config)
        self.validator = SessionValidator()

    def test_validate(self):
        session = self.loader.load("testsession")
        self.assertTrue(session)
        self.assertTrue(self.validator.validate(session))

        session = self.loader.load("invalidsession")
        self.assertTrue(session)
        self.assertFalse(self.validator.validate(session))

        session = self.loader.load("sessionwithoutname")
        self.assertTrue(session)
        self.assertFalse(self.validator.validate(session))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(SessionLoaderTest("test_load"))
    suite.addTest(SessionLoaderTest("test_load_derived"))
    suite.addTest(SessionLoaderTest("test_load_sub"))
    suite.addTest(SessionValidatorTest("test_validate"))

    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())

