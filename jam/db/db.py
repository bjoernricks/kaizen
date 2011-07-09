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

from jam.external.sqlalchemy import TypeDecorator, String


class Db(object):

    def __init__(self, config):
        rootdir = config.get("rootdir")
        db_path = os.path.join(rootdir, "jam.db")
        self.engine = create_engine("sqlite:///%s" % db_path)

    def get_engine(self):
        return self.engine


class PhaseType(TypeDecorator):

    impl = String
    phases = ["None", "Downloaded", "Extracted", "Configured", "Built",
              "Destrooted", "Activated", "Deactivated"]

    def process_bind_param(self, value, dialect):
        if value not in self.phases:
            raise TypeError("Invalid PhaseType '%s'" % value)
        return value

