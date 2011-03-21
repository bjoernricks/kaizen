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

import os
import os.path
import sys
import unittest
import logging


test_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(test_dir, os.pardir))

from jam.session import SessionLoader

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logging.getLogger("jam").addHandler(NullHandler())

class TestConfig(object):

    def __init__(self):
        self.jam_sessions = os.path.join(test_dir, "session")

class SessionLoaderTest(unittest.TestCase):

    def test_load(self):
        loader = SessionLoader(TestConfig())

        module = loader.module("testsession")
        self.assertTrue(module)
        self.assertEquals("testsession", module.__name__)

        classes = loader.classes("testsession")
        self.assertEquals(2, len(classes))

        sessions = loader.sessions("testsession")
        self.assertEquals(1, len(sessions))

        session = loader.load("testsession")
        self.assertTrue(session)
        self.assertTrue(session.build())
        self.assertEquals(1, session.my_method())

        session = loader.load("notestsession")
        self.assertFalse(session)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(SessionLoaderTest("test_load"))

    return suite

if __name__ == "__main__":
    print os.curdir
    runner = unittest.TextTestRunner()
    runner.run(suite())

