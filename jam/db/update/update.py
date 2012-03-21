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

import datetime

from jam.db.db import Db
from jam.error import JamError


class Update(object):

    name = None
    version = None

    def __init__(self, config, db):
        self.config = config
        self.db = db

    def run(self):
        pass

    def get_name(self):
        return self.name

    def finish(self):
        updatever = UpdateVersion(self.name, self.version, datetime.now())
        self.db.session.add(updatever)
        self.db.session.commit()


class UpdateError(JamError):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "Error during update: %s" % (self.value)
