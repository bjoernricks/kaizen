# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# kaizen - Continuously improve, build and manage free software
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

import kaizen.logging

from datetime import datetime

from kaizen.db.db import Db
from kaizen.db.objects import UpdateVersion
from kaizen.error import KaizenError


class Update(object):

    name = None
    version = None

    def __init__(self, config, db):
        self.config = config
        self.db = db
        self.log = kaizen.logging.getLogger(self)

    def run(self):
        """ Runs the actual update process
            If this method returns true the finish method is called by Upgrade.
        """
        return False

    def get_name(self):
        return self.name

    def finish(self):
        updatever = UpdateVersion(self.name, self.version, datetime.now())
        self.db.session.add(updatever)
        self.db.session.commit()


class UpdateError(KaizenError):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "Error during update: %s" % (self.value)
