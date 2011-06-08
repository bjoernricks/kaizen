# vim:fileencoding=utf-8:et::sw=4:ts=4:tw=80:

# jam - An advanced package manager for Free Software
#
# Copyright (C) 2011  Björn Ricks <bjoern.ricks@googlemail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

from jam.config import Config, JAM_CONFIG_FILES
from jam.session import SessionManager


class Command(object):

    def __init__(self, name, func, aliases=[]):
        self.name = name
        self.func = func
        self.aliases = aliases

    def add_parser(self, parser):
        if self.aliases:
            subparser = parser.add_parser(self.name, aliases=self.aliases)
        else:
            subparser = parser.add_parser(self.name)
        return subparser

    def get_func(self):
        return func


class PhaseCommand(Command):

    def __init__(self, name, aliases=[]):
        super(PhaseCommand, self).__init__(name, self.main, aliases)

    def add_parser(self, parser):
        subparser = super(PhaseCommand, self).add_parser(parser)
        subparser.add_argument("sessionname", nargs=1)
        return subparser

    def main(self, options):
        self.config = Config(configfiles, vars(options))
        self.manager = SessionManager(self.config, options.sessionname[0],
                                      force=options.force)


class BuildCommand(PhaseCommand):

    def __init__(self):
        super(BuildCommand, self),__init__("build")

    def main(self, options):
        super(BuildCommand, self).main(options)
        self.manager.build()


class ConfigureCommand(PhaseCommand):

    def __init__(self):
        super(ConfigureCommand, self),__init__("configure", ["conf"])

    def main(self, options):
        super(ConfigureCommand, self).main(options)
        self.manager.configure()


class ExtractCommand(PhaseCommand):

    def __init__(self):
        super(ExtractCommand, self),__init__("extract", ["ex"])

    def main(self, options):
        super(ExtractCommand, self).main(options)
        self.manager.extract()


class DownloadCommand(PhaseCommand):

    def __init__(self):
        super(DownloadCommand, self),__init__("download", ["down"])

    def main(self, options):
        super(DownloadCommand, self).main(options)
        self.manager.download()


class DestrootCommand(PhaseCommand):

    def __init__(self):
        super(DestrootCommand, self),__init__("destroot", ["dest"])

    def main(self, options):
        super(DestrootCommand, self).main(options)
        self.manager.destroot()


class InstallCommand(PhaseCommand):

    def __init__(self):
        super(InstallCommand, self),__init__("install", ["inst"])

    def main(self, options):
        super(InstallCommand, self).main(options)
        self.manager.install()


class UninstallCommand(PhaseCommand):

    def __init__(self):
        super(UninstallCommand, self),__init__("uninstall", ["uninst", "remove"])

    def main(self, options):
        super(UninstallCommand, self).main(options)
        self.manager.uninstall()


class DropCommand(PhaseCommand):

    def __init__(self):
        super(DropCommand, self),__init__("drop")

    def main(self, options):
        super(DropCommand, self).main(options)
        self.manager.uninstall()


class ActivateCommand(PhaseCommand):

    def __init__(self):
        super(ActivateCommand, self),__init__("activate")

    def main(self, options):
        super(ActivateCommand, self).main(options)
        self.manager.activate()


class DeactivateCommand(PhaseCommand):

    def __init__(self):
        super(DeactivateCommand, self),__init__("deactivate")

    def main(self, options):
        super(DeactivateCommand, self).main(options)
        self.manager.deactivate()


class CleanCommand(PhaseCommand):

    def __init__(self):
        super(CleanCommand, self),__init__("clean")

    def main(self, options):
        super(CleanCommand, self).main(options)
        self.manager.clean()


class DistcleanCommand(PhaseCommand):

    def __init__(self):
        super(DistcleanCommand, self),__init__("distclean")

    def main(self, options):
        super(DistcleanCommand, self).main(options)
        self.manager.distclean()


class DependsCommand(PhaseCommand):

    def __init__(self):
        super(DependsCommand, self),__init__("depends", ["deps"])

    def main(self, options):
        super(DependsCommand, self).main(options)
        self.manager.depends()


