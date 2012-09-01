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

import datetime

import kaizen.logging

import kaizen.db.update.update_0 as update_0

from kaizen.db.db import Db
from kaizen.db.objects import UpdateVersion
from kaizen.db.update.error import UpdateError


updates = {
           0 : update_0.updates,
          }

class Upgrade(object):

    def __init__(self, config):
        self.config = config
        self.db = Db(config)
        cls = self.__class__
        self.log = kaizen.logging.getLogger(self)

    def run(self):
        version = self.db.schema.version
        cur_updates = updates.get(version)
        if not cur_updates:
            self.log.debug("No updates for database scheme version"
                           " %r available" % version)
            return

        for update in cur_updates:
            if self.db.session.query(
                    UpdateVersion).filter(UpdateVersion.update ==
                            update.name).first():
                    self.log.debug("Update %r already applied." % update.name)
                    continue
            update = update(self.config, self.db)
            try:
                self.log.debug("Running update %r" % update.name)
                success = update.run()
                if success:
                    update.finish()
            except UpdateError, e:
                self.log.error("Error while running update %r. %s" % update.name,
                               e)
