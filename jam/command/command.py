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

from jam.session import SessionManager


class Command(object):

    def __init__(self, name, config, func, aliases=[]):
        self.name = name
        self.func = func
        self.aliases = aliases
        self.config = config

    def add_parser(self, parser, usage=None):
        if usage:
            self.usage = usage
        else:
            self.usage = "%(prog)s [options] " + self.name + " {arguments}"
        subparser = parser.add_parser(self.name, aliases=self.aliases,
                                      usage=self.usage)
        subparser.set_defaults(func=self.func)
        return subparser

    def get_func(self):
        return func


class PhaseCommand(Command):

    def __init__(self, name, config, help, aliases=[]):
        super(PhaseCommand, self).__init__(name, config, self.main, aliases)
        self.help = help

    def add_parser(self, parser):
        subparser = super(PhaseCommand, self).add_parser(parser)
        subparser.add_argument("sessionname", nargs=1)
        return subparser

    def main(self, options):
        self.manager = SessionManager(self.config, options.sessionname[0],
                                      force=options.force)


class BuildCommand(PhaseCommand):

    def __init__(self, config):
        help = "run build process"
        super(BuildCommand, self).__init__("build", config, help)

    def main(self, options):
        super(BuildCommand, self).main(options)
        self.manager.build()


class ConfigureCommand(PhaseCommand):

    def __init__(self, config):
        help = ""
        super(ConfigureCommand, self).__init__("configure", config, help,
                                               ["conf"])

    def main(self, options):
        super(ConfigureCommand, self).main(options)
        self.manager.configure()


class ExtractCommand(PhaseCommand):

    def __init__(self, config):
        help = ""
        super(ExtractCommand, self).__init__("extract", config, help, ["ex"])

    def main(self, options):
        super(ExtractCommand, self).main(options)
        self.manager.extract()


class DownloadCommand(PhaseCommand):

    def __init__(self, config):
        help = ""
        super(DownloadCommand, self).__init__("download", config, help,
                                              ["down"])

    def main(self, options):
        super(DownloadCommand, self).main(options)
        self.manager.download()


class DestrootCommand(PhaseCommand):

    def __init__(self, config):
        help = ""
        super(DestrootCommand, self).__init__("destroot", config, help,
                                              ["dest"])

    def main(self, options):
        super(DestrootCommand, self).main(options)
        self.manager.destroot()


class InstallCommand(PhaseCommand):

    def __init__(self, config):
        help = ""
        super(InstallCommand, self).__init__("install", config, help,
                                             ["inst"])

    def main(self, options):
        super(InstallCommand, self).main(options)
        self.manager.install()


class UninstallCommand(PhaseCommand):

    def __init__(self, config):
        help = ""
        super(UninstallCommand, self).__init__("uninstall", config, help,
                                               ["uninst", "remove"])

    def main(self, options):
        super(UninstallCommand, self).main(options)
        self.manager.uninstall()


class DropCommand(PhaseCommand):

    def __init__(self, config):
        help = ""
        super(DropCommand, self).__init__("drop", config, help)

    def main(self, options):
        super(DropCommand, self).main(options)
        self.manager.uninstall()


class ActivateCommand(PhaseCommand):

    def __init__(self, config):
        help = ""
        super(ActivateCommand, self).__init__("activate", config, help)

    def main(self, options):
        super(ActivateCommand, self).main(options)
        self.manager.activate()


class DeactivateCommand(PhaseCommand):

    def __init__(self, config):
        help = ""
        super(DeactivateCommand, self).__init__("deactivate", config, help)

    def main(self, options):
        super(DeactivateCommand, self).main(options)
        self.manager.deactivate()


class CleanCommand(PhaseCommand):

    def __init__(self, config):
        help = ""
        super(CleanCommand, self).__init__("clean", config, help)

    def main(self, options):
        super(CleanCommand, self).main(options)
        self.manager.clean()


class DistcleanCommand(PhaseCommand):

    def __init__(self, config):
        help = ""
        super(DistcleanCommand, self).__init__("distclean", config, help)

    def main(self, options):
        super(DistcleanCommand, self).main(options)
        self.manager.distclean()


class DependsCommand(PhaseCommand):

    def __init__(self, config):
        help = ""
        super(DependsCommand, self).__init__("depends", config, help,
                                             ["deps"])

    def main(self, options):
        super(DependsCommand, self).main(options)
        self.manager.depends()


