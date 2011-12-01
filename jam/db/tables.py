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

from jam.phase.phase import Phases, Phase

from jam.external.sqlalchemy import MetaData, Table, Column, String, \
                                    ForeignKey, TypeDecorator


class PhaseType(TypeDecorator):

    impl = String
    phases = Phases()

    def process_bind_param(self, value, dialect):
        if isinstance(value, Phase):
            return value.name
        if not self.phases.get(value):
            raise TypeError("Invalid PhaseType '%s'" % value)
        return value

    def process_result_value(self, value, dialect):
        phase = self.phases.get(value)
        if not phase:
            raise TypeError("Invalid value '%s' for PhaseType" % value)
        return phase


class Tables(object):

    def __init__(self, db):
        self.metadata = MetaData()
        self.metadata.bind = db.engine

        self.info_table = Table('info', self.metadata,
                         Column('session', String, primary_key = True),
                         Column('desription', String),
                         Column('license', String),
                         Column('maintainer', String),
                         Column('category', String),
                         Column('homepage', String),
                         Column('scm', String),
                         Column('scm_web', String))

        # Installed table is now intended to record manually installed
        # session. It doesn't include session which are installed as
        # dependency
        self.installed_table = Table('installed', self.metadata,
                          Column('session', String,
                                 ForeignKey(self.info_table.c.session),
                                 primary_key = True),
                          Column('version', String, nullable = False))

        self.files_table = Table('files', self.metadata,
                      Column('filename', String, primary_key = True),
                      Column('session', String,
                             ForeignKey(self.info_table.c.session),
                             nullable = False))

        self.dirs_table = Table('directories', self.metadata,
                          Column('directory', String, primary_key=True),
                          Column('session', String,
                                 ForeignKey(self.info_table.c.session),
                                 primary_key=True))

        self.phases_table = Table("phases", self.metadata,
                       Column('session', String,
                              ForeignKey(self.info_table.c.session),
                              primary_key = True),
                       Column('version', String, primary_key = True),
                       Column('phase', PhaseType, primary_key=True))

    def create(self):
        self.metadata.create_all()

