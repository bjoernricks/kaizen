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

import os.path

from jam.db.tables import Tables
from jam.db.objects import Info, Installed, File, Status, SessionPhase
from jam.external.sqlalchemy import String, create_engine
from jam.external.sqlalchemy.orm import mapper, sessionmaker

class Db(object):

    def __new__(type, *args):
        if not '_instance' in type.__dict__:
            type._instance = object.__new__(type)
        return type._instance

    def __init__(self, config):
        if not "_already_init" in dir(self):
            rootdir = config.get("rootdir")
            db_path = os.path.join(rootdir, "jam.db")
            self.engine = create_engine("sqlite:///%s" % db_path)
            self.tables = Tables(self)
            self.tables.create()
            SqlAlchemySession = sessionmaker()
            self.session = SqlAlchemySession(bind=self.engine)
            mapper(Info, self.tables.info_table) 
            mapper(Installed, self.tables.installed_table)
            mapper(File, self.tables.files_table)
            mapper(Status, self.tables.status_table)
            mapper(SessionPhase, self.tables.phases_table)
            self._already_init = True

    def get_engine(self):
        return self.engine


