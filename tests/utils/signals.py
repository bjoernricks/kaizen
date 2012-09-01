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

import os.path
import sys
import unittest

test_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(test_dir, os.pardir, os.pardir))

from kaizen.utils.signals import Signal

class A(object):

    def __init__(self):
        self.test = Signal()

class B(object):

    def __init__(self):
        self.called = False

    def on_call(self):
        self.called = True


class SignalTest(unittest.TestCase):

    def setUp(self):
        self.a = A()
        self.b = B()

    def test_connect(self):
        self.a.test.connect(self.b.on_call)
        self.assertTrue(len(self.a.test) == 1)

        self.a.test.connect(self.b.on_call)
        self.assertTrue(len(self.a.test) == 1)

        def test():
            pass
        self.a.test.connect(test)
        self.assertTrue(len(self.a.test) == 2)

    def test_disconnect(self):
        self.a.test.connect(self.b.on_call)
        self.assertTrue(len(self.a.test) == 1)

        self.a.test.disconnect(self.b.on_call)
        self.assertTrue(len(self.a.test) == 0)

        def test():
            pass
        self.a.test.connect(test)
        self.assertTrue(len(self.a.test) == 1)

        self.a.test.disconnect(test)
        self.assertTrue(len(self.a.test) == 0)


    def test_call(self):
        self.a.test.connect(self.b.on_call)
        self.a.test()
        self.assertTrue(self.b.called)

        self.value = False
        def test():
            self.value = True
        self.a.test.connect(test)
        self.a.test()
        self.assertTrue(self.value)

    def test_del(self):
        b = B()
        self.a.test.connect(b.on_call)
        self.assertTrue(len(self.a.test) == 1)
        del b
        self.assertTrue(len(self.a.test) == 0)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(SignalTest))
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
