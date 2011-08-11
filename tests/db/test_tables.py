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

from jam.db.db import Db, Tables
from jam.phase.phase import Phases
from jam.external.sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, StatementError

class TestDb(Db):

    def __init__(self):
        self.db_path = os.path.join(test_dir, "jam.db")
        self.engine = create_engine("sqlite:///%s" % self.db_path)


class TableTest(unittest.TestCase):

    def setUp(self):
        self.db = TestDb()
        self.tables = Tables(self.db)

    def tearDown(self):
        os.remove(self.db.db_path)

    def test_create(self):
        self.tables.create()
        # second time tables already exists and create shouldn't raise an error
        self.tables.create()

    def test_info_table(self):
        self.tables.create()
        val = self.tables.info_table.insert({"session" : "myapp",
                                       "description" : "my new session",
                                       "license" : "GPLv2",
                                       "maintainer" : "john@doe.com",
                                       "category" : "devel",
                                       "homepage" : "http://some.url",
                                       "scm" : "git://some.url/abc.git",
                                       "scm_web" : "http://gitweb.some.url/",
                                       })
        val.execute()
        try:
            val.execute()
            self.fail("inserting the same info should result in an "
                      "IntegrityError")
        except IntegrityError, e:
            pass

    def test_installed_table(self):
        self.tables.create()
        table = self.tables.installed_table

        ins = dict({"session": "myapp",
                   "version" : "123"})
        res = table.insert(ins)
        res.execute()

        res = table.select(table.c.session == "myapp")
        val = res.execute().fetchone()
        self.assertEquals(val["session"], "myapp")
        self.assertEquals(val["version"], "123")

        ins = dict({"session": "myapp",
                    "version": "321"})
        res = table.insert(ins)
        try:
            res.execute()
            self.fail("inserting the same value should result in an "
                      "IntegretyError")
        except IntegrityError, e:
            pass

        res = table.update(table.c.session == "myapp", ins)
        res.execute()

        res = table.select(table.c.session == "myapp")
        val = res.execute().fetchone()
        self.assertEquals(val["session"], "myapp")
        self.assertEquals(val["version"], "321")

    def test_files_table(self):
        self.tables.create()
        table = self.tables.files_table

        ins = dict(filename="/usr/share/myapp/myfile",
                   session="myapp")

        res = table.insert(ins)
        res.execute()

        res = table.select(table.c.session == "myapp")
        val = res.execute().fetchone()
        self.assertEquals(val["session"], "myapp")
        self.assertEquals(val["filename"], "/usr/share/myapp/myfile")

        res = table.insert(ins)
        try:
            res.execute()
            self.fail("inserting the same value should result in an "
                      "IntegretyError")
        except IntegrityError, e:
            pass

        ins = dict(filename="/usr/share/myapp/myfile",
                   session="app2")
        res = table.insert(ins)
        try:
            res.execute()
            self.fail("inserting the same primary key should result in an "
                      "IntegretyError")
        except IntegrityError, e:
            pass

    def test_status_table(self):
        self.tables.create()
        table = self.tables.status_table

        ins = dict(session="myapp",
                   version="123",
                   phase="Built")
        res = table.insert(ins)
        res.execute()

        ins = dict(session="myapp",
                   version="1234",
                   phase="Built")
        res = table.insert(ins)
        res.execute()

        ins = dict(session="myapp2",
                   version="123",
                   phase="abc")
        res = table.insert(ins)
        try:
            res.execute()
            self.fail("abc is an invalid phase")
        except StatementError:
            pass

        table.delete(table.c.session=="myapp").execute()

        ins = dict(session="myapp",
                   version="123",
                   phase="None")
        res = table.insert(ins)
        res.execute()
        table.delete(table.c.session=="myapp").execute()

        ins = dict(session="myapp",
                   version="123",
                   phase="Downloaded")
        res = table.insert(ins)
        res.execute()
        table.delete(table.c.session=="myapp").execute()

        ins = dict(session="myapp",
                   version="123",
                   phase="Extracted")
        res = table.insert(ins)
        res.execute()
        table.delete(table.c.session=="myapp").execute()

        ins = dict(session="myapp",
                   version="123",
                   phase="Configured")
        res = table.insert(ins)
        res.execute()
        table.delete(table.c.session=="myapp").execute()

        ins = dict(session="myapp",
                   version="123",
                   phase="Destrooted")
        res = table.insert(ins)
        res.execute()
        table.delete(table.c.session=="myapp").execute()

        ins = dict(session="myapp",
                   version="123",
                   phase="Activated")
        res = table.insert(ins)
        res.execute()
        table.delete(table.c.session=="myapp").execute()

        ins = dict(session="myapp",
                   version="123",
                   phase="Deactivated")
        res = table.insert(ins)
        res.execute()
        table.delete(table.c.session=="myapp").execute()

        ins = dict(session="myapp",
                   version="123",
                   phase="Patched")
        res = table.insert(ins)
        res.execute()

        query = table.select(table.c.session=="myapp")
        status = self.db.engine.execute(query).fetchone()
        self.assertEquals("myapp", status[0])
        self.assertEquals("123", status[1])
        self.assertEquals(Phases().get("Patched"), status[2])

        table.delete(table.c.session=="myapp").execute()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TableTest))
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
