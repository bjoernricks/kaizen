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

from jam.db.update.update import Update as RootUpdate
from jam.db.objects import SessionPhase, InstallDirectories
from jam.session.handler import SessionHandler
from jam.utils.helpers import real_path


class Update(RootUpdate):

    version = 0


class UpdateForInstallDirs(Update):

    name = "installdirs"

    def run(self):
        self.log.info("Running update %r %r" % (self.version, self.name))
        db = self.db.session

        query = db.query(SessionPhase.session, SessionPhase.version).distinct( \
                SessionPhase.session, SessionPhase.version)
        for sessionphase in query:
            session_name = sessionphase[0]
            session_version = sessionphase[1]
            handler = SessionHandler(self.config, session_name, session_version)
            session = handler.session
            install_directories = InstallDirectories(session_name,
                                                     session_version)
            install_directories.build = real_path(session.build_path)
            install_directories.source = real_path(session.src_path)
            install_directories.destroot = real_path(session.destroot_path)
            self.log.debug("Update install_directories %r" % install_directories)
            db.merge(install_directories)

        db.commit()
        return True

updates = [UpdateForInstallDirs]
