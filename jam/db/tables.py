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

from jam.external.sqlalchemy import MetaData, Table, Column, String, ForeignKey

from jam.db import PhaseType

class Tables(object):

    def __init__(self, db):
        self.metadata = MetaData()
        self.metadata.bind = db.get_engine()

        self.sessions_table = Table('sessions', self.metadata,
                         Column('session', String, primary_key = True),
                         Column('desription', String),
                         Column('license', String),
                         Column('maintainer', String),
                         Column('category', String),
                         Column('homepage', String),
                         Column('scm', String))

        self.installed_table = Table('installed', self.metadata,
                          Column('session', String,
                                 ForeignKey(self.sessions_table.c.session),
                                 primary_key = True),
                          Column('version', String, nullable = False))

        files = Table('files', self.metadata,
                      Column('filename', String, primary_key = True),
                      Column('session', String,
                             ForeignKey(self.sessions_table.c.session),
                             nullable = False))

        self.status_table = Table('status', self.metadata,
                       Column('session', String,
                              ForeignKey(self.sessions_table.c.session),
                              primary_key = True),
                       Column('version', String, nullable = False),
                       Column('phase', PhaseType, nullable = False))

    def create(self):
        self.metadata.create_all()


