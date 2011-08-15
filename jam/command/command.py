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
from jam.session.create import SessionCreator


class Command(object):

    def __init__(self, name, config, func, aliases=[], description=None):
        self.name = name
        self.func = func
        self.aliases = aliases
        self.config = config
        self.description = description

    def add_parser(self, parser, usage=None):
        if usage:
            self.usage = usage
        else:
            self.usage = "%(prog)s [options] " + self.name + " {arguments}"
        subparser = parser.add_parser(self.name, aliases=self.aliases,
                                      usage=self.usage,
                                      description=self.description)
        subparser.set_defaults(func=self.func)
        return subparser

    def get_func(self):
        return func


class SessionNameCommand(Command):

    def __init__(self, name, config, func, aliases=[], description=None):
        super(SessionNameCommand, self).__init__(name, config, func, aliases,
                                                 description)

    def add_parser(self, parser):
        subparser = super(SessionNameCommand, self).add_parser(parser)
        subparser.add_argument("sessionname", nargs=1)
        return subparser


class PhaseCommand(SessionNameCommand):

    def __init__(self, name, config, description, aliases=[]):
        super(PhaseCommand, self).__init__(name, config, self.main, aliases,
                                           description)

    def main(self, options):
        self.manager = SessionManager(self.config, options.sessionname[0],
                                      force=options.force)


class BuildCommand(PhaseCommand):

    def __init__(self, config):
        description = "run build process"
        super(BuildCommand, self).__init__("build", config, description)

    def main(self, options):
        super(BuildCommand, self).main(options)
        self.manager.build()


class ConfigureCommand(PhaseCommand):

    def __init__(self, config):
        description = ""
        super(ConfigureCommand, self).__init__("configure", config, description,
                                               ["conf"])

    def main(self, options):
        super(ConfigureCommand, self).main(options)
        self.manager.configure()


class ExtractCommand(PhaseCommand):

    def __init__(self, config):
        description = ""
        super(ExtractCommand, self).__init__("extract", config, description, ["ex"])

    def main(self, options):
        super(ExtractCommand, self).main(options)
        self.manager.extract()


class DownloadCommand(PhaseCommand):

    def __init__(self, config):
        description = ""
        super(DownloadCommand, self).__init__("download", config, description,
                                              ["down"])

    def main(self, options):
        super(DownloadCommand, self).main(options)
        self.manager.download()


class DestrootCommand(PhaseCommand):

    def __init__(self, config):
        description = ""
        super(DestrootCommand, self).__init__("destroot", config, description,
                                              ["dest"])

    def main(self, options):
        super(DestrootCommand, self).main(options)
        self.manager.destroot()


class InstallCommand(PhaseCommand):

    def __init__(self, config):
        description = ""
        super(InstallCommand, self).__init__("install", config, description,
                                             ["inst"])

    def main(self, options):
        super(InstallCommand, self).main(options)
        self.manager.install()


class UninstallCommand(PhaseCommand):

    def __init__(self, config):
        description = ""
        super(UninstallCommand, self).__init__("uninstall", config, description,
                                               ["uninst", "remove"])

    def main(self, options):
        super(UninstallCommand, self).main(options)
        self.manager.uninstall()


class DropCommand(PhaseCommand):

    def __init__(self, config):
        description = ""
        super(DropCommand, self).__init__("drop", config, description)

    def main(self, options):
        super(DropCommand, self).main(options)
        self.manager.uninstall()


class ActivateCommand(PhaseCommand):

    def __init__(self, config):
        description = ""
        super(ActivateCommand, self).__init__("activate", config, description)

    def main(self, options):
        super(ActivateCommand, self).main(options)
        self.manager.activate()


class DeactivateCommand(PhaseCommand):

    def __init__(self, config):
        description = ""
        super(DeactivateCommand, self).__init__("deactivate", config, description)

    def main(self, options):
        super(DeactivateCommand, self).main(options)
        self.manager.deactivate()


class CleanCommand(PhaseCommand):

    def __init__(self, config):
        description = ""
        super(CleanCommand, self).__init__("clean", config, description)

    def main(self, options):
        super(CleanCommand, self).main(options)
        self.manager.clean()


class DistcleanCommand(PhaseCommand):

    def __init__(self, config):
        description = ""
        super(DistcleanCommand, self).__init__("distclean", config, description)

    def main(self, options):
        super(DistcleanCommand, self).main(options)
        self.manager.distclean()


class DependsCommand(PhaseCommand):

    def __init__(self, config):
        description = ""
        super(DependsCommand, self).__init__("depends", config, description,
                                             ["deps"])

    def main(self, options):
        super(DependsCommand, self).main(options)
        dependency_names = self.manager.depends().keys()
        if not dependency_names:
            return
        print "Session %s depends on:" % options.sessionname[0]
        for dependency_name in dependency_names:
            print "--> %s" % dependency_name


class CreateCommand(Command):

    def __init__(self, config):
        description = "Create a new Session"
        super(CreateCommand, self).__init__("create", config, self.main, [],
                                            description)

    def add_parser(self, parser):
        usage = "%(prog)s [options] " + self.name + " url {arguments}"
        subparser = super(CreateCommand, self).add_parser(parser, usage)
        subparser.add_argument("url", nargs=1, help="url to download source file")
        subparser.add_argument("--template", choices=["cmake", "python",
                               "autotools"], help="specify a template for the"\
                               " new session. If empty jam will guess the"\
                               " right one.")
        subparser.add_argument("--name", "-n", help="name of the new "\
                               "session. If empty jam will determine the "\
                               " name from the source file")
        subparser.add_argument("--version", "-v", help="version of the new "\
                               "session. If empty jam will determine the "\
                               " version from the source file")
        subparser.add_argument("--keep", action="store_true", 
                               help="keep temporary directory")
        subparser.add_argument("--print", dest="stdout", action="store_true",
                               help="print to stdout instead of creating a "\
                               "new session")

    def main(self, options):
        creator = SessionCreator(self.config, options.url[0], options.keep)
        if options.name:
            creator.set_name(options.name)

        if options.template:
            creator.set_template(options.template)

        if options.version:
            creator.set_version(options.version)

        creator.create(options.stdout)

