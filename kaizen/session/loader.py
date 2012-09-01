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

import jam.logging

from jam.utils import Loader, real_path
from jam.session.session import Session

class SessionLoader(Loader):

    def __init__(self, config):
        super(SessionLoader, self).__init__()
        self.config = config
        self.log = jam.logging.getLogger(self)
        paths = self.config.get("sessions")
        self.add_paths([real_path(path.strip()) for path in paths])

    def sessions(self, modulename):
        as_module = "jam.session._modules." + modulename
        module = self.module(modulename, as_module)
        if not module:
            return None 
        return self.classes(module, Session)

    def load(self, sessionname):
        sessionstring = sessionname + ".rules"
        sessions = self.sessions(sessionstring)
        if not sessions:
            self.log.warn("Could not load any session with name '%s'" %
                          sessionname)
            return None
        session = sessions[0]
        self.log.debug("Loaded session class '%s'" % session.__name__)
        return session
