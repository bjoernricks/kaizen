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

from jam.session.manager import SessionManager


class Console(object):

    def list_session_files(self, config, sessionname):
        manager = SessionManager(config, sessionname)
        files = manager.get_installed_files()

    def list_session_phases(self, config, sessionname):
        manager = SessionManager(config, sessionname)
        phases = manager.get_session_phases()

    def list_session_dependencies(self, config, session):
        manager = SessionManager(config, sessionname)
        dependency_names = self.manager.depends().keys()
        if not dependency_names:
            return
        print "Session %s depends on:" % options.sessionname[0]
        for dependency_name in dependency_names:
            print "--> %s" % dependency_name

