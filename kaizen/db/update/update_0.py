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

from kaizen.db.update.update import Update as RootUpdate
from kaizen.db.objects import RulesPhase, InstallDirectories
from kaizen.rules.handler import RulesHandler
from kaizen.utils.helpers import real_path


class Update(RootUpdate):

    version = 0


class UpdateForInstallDirs(Update):

    name = "installdirs"

    def run(self):
        self.log.info("Running update %r %r" % (self.version, self.name))
        db = self.db.rules

        query = db.query(RulesPhase.rules, RulesPhase.version).distinct( \
                RulesPhase.rules, RulesPhase.version)
        for rulesphase in query:
            rules_name = rulesphase[0]
            rules_version = rulesphase[1]
            handler = RulesHandler(self.config, rules_name, rules_version)
            rules = handler.rules
            install_directories = InstallDirectories(rules_name,
                                                     rules_version)
            install_directories.build = real_path(rules.build_path)
            install_directories.source = real_path(rules.src_path)
            install_directories.destroot = real_path(rules.destroot_path)
            self.log.debug("Update install_directories %r" % install_directories)
            db.merge(install_directories)

        db.commit()
        return True

updates = [UpdateForInstallDirs]
