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

import kaizen.logging

from kaizen.db.tables import Tables
from kaizen.db.objects import Info, Installed, File, Directory, SessionPhase, \
        UpdateVersion, InstallDirectories, SchemaVersion
from kaizen.external.sqlalchemy import String, create_engine
from kaizen.external.sqlalchemy.orm import mapper, sessionmaker

CURRENT_DB_SCHEMA = 0

class Db(object):

    def __new__(type, *args):
        if not '_instance' in type.__dict__:
            type._instance = object.__new__(type)
        return type._instance

    def __init__(self, config):
        if not "_already_init" in dir(self):
            cls = self.__class__
            self.log = kaizen.logging.getLogger("%s.%s" % (cls.__module__,
                                                        cls.__name__))
            rootdir = config.get("rootdir")
            debug_db = config.get("debugdb")
            db_path = os.path.join(rootdir, "kaizen.db")
            if not os.path.exists(rootdir):
                os.makedirs(rootdir)
            self.engine = create_engine("sqlite:///%s" % db_path,
                                        echo=debug_db)
            self.tables = Tables(self)
            self.tables.create()
            SqlAlchemySession = sessionmaker()
            self.session = SqlAlchemySession(bind=self.engine)
            mapper(Info, self.tables.info_table) 
            mapper(Installed, self.tables.installed_table)
            mapper(File, self.tables.files_table)
            mapper(Directory, self.tables.dirs_table)
            mapper(SessionPhase, self.tables.phases_table)
            mapper(SchemaVersion, self.tables.dbversion_table)
            mapper(UpdateVersion, self.tables.updates_table)
            mapper(InstallDirectories, self.tables.install_directories_table)
            self._init_schema()
            self._already_init = True

    def get_engine(self):
        return self.engine

    def _init_schema(self):
        self.schema = self.session.query(SchemaVersion).first()
        if not self.schema:
            self.schema = SchemaVersion(CURRENT_DB_SCHEMA)
            self.session.add(self.schema)
            self.session.commit()
        self.log.debug("Current database schema version is %r" % \
                       self.schema.version)
