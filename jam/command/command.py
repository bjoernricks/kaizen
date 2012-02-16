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

from jam.session.create import SessionCreator
from jam.console.console import Console


class Command(object):

    def __init__(self, name, func, aliases=[], description=""):
        self.name = name
        self.func = func
        self.aliases = aliases
        self.description = description

    def add_parser(self, parser, usage=None):
        if usage:
            self.usage = usage
        else:
            self.usage = "%(prog)s [global options] " + self.name + \
                         " {optional arguments}"
        subparser = parser.add_parser(self.name, aliases=self.aliases,
                                      usage=self.usage,
                                      description=self.description,
                                      help=self.description)
        subparser.set_defaults(func=self.func)
        return subparser

    def get_func(self):
        return func


class SessionNameCommand(Command):

    def __init__(self, name, description=None, aliases=[]):
        super(SessionNameCommand, self).__init__(name, self.main,
                                                 aliases, description)

    def add_parser(self, parser):
        usage = "%(prog)s [global options] " + self.name + " <sessionname> " \
                "{arguments}"
        subparser = super(SessionNameCommand, self).add_parser(parser, usage)
        subparser.add_argument("sessionname", nargs=1)
        return subparser

    def main(self, options, config):
        pass


class BuildCommand(SessionNameCommand):

    def __init__(self):
        description = "run build process"
        super(BuildCommand, self).__init__("build", description)

    def main(self, options, config):
        Console(config).build_session(options.sessionname[0],
                                      options.force)


class PatchCommand(SessionNameCommand):

    def __init__(self):
        description = "apply patches to sources"
        super(PatchCommand, self).__init__("patch", description)

    def main(self, options, config):
        Console(config).patch_session(options.sessionname[0],
                                      options.force)


class UnPatchCommand(SessionNameCommand):

    def __init__(self):
        description = "revert patches applied sources"
        super(UnPatchCommand, self).__init__("unpatch", description)

    def main(self, options, config):
        Console(config).unpatch_session(options.sessionname[0],
                                        options.force)


class ConfigureCommand(SessionNameCommand):

    def __init__(self):
        description = ""
        super(ConfigureCommand, self).__init__("configure", description,
                                               ["conf"])

    def main(self, options, config):
        Console(config).configure_session(options.sessionname[0],
                                          options.force)


class ExtractCommand(SessionNameCommand):

    def __init__(self):
        description = ""
        super(ExtractCommand, self).__init__("extract", description, ["ex"])

    def main(self, options, config):
        Console(config).extract_session(options.sessionname[0],
                                        options.force)


class DownloadCommand(SessionNameCommand):

    def __init__(self):
        description = ""
        super(DownloadCommand, self).__init__("download", description,
                                              ["down", "fetch"])

    def main(self, options, config):
        Console(config).download_session(options.sessionname[0],
                                         options.all, options.force)

    def add_parser(self, parser):
        subparser = super(DownloadCommand, self).add_parser(parser)
        subparser.add_argument("--all", action="store_true",
                               help="download also sources from dependencies")


class DestrootCommand(SessionNameCommand):

    def __init__(self):
        description = ""
        super(DestrootCommand, self).__init__("destroot", description,
                                              ["dest"])

    def main(self, options, config):
        Console(config).destroot_session(options.sessionname[0],
                                         options.force)


class InstallCommand(SessionNameCommand):

    def __init__(self):
        description = ""
        super(InstallCommand, self).__init__("install", description,
                                             ["inst"])

    def main(self, options, config):
        Console(config).install_session(options.sessionname[0],
                                        options.force)


class UninstallCommand(SessionNameCommand):

    def __init__(self):
        description = ""
        super(UninstallCommand, self).__init__("uninstall", description,
                                               ["uninst", "remove"])

    def main(self, options, config):
        Console(config).uninstall_session(options.sessionname[0],
                                          options.force)


class ActivateCommand(SessionNameCommand):

    def __init__(self):
        description = ""
        super(ActivateCommand, self).__init__("activate", description)

    def main(self, options, config):
        Console(config).activate_session(options.sessionname[0],
                                         options.force)


class DeactivateCommand(SessionNameCommand):

    def __init__(self):
        description = ""
        super(DeactivateCommand, self).__init__("deactivate", description)

    def main(self, options, config):
        Console(config).deactivate_session(options.sessionname[0],
                                                options.force)


class DeleteCommand(SessionNameCommand):

    def __init__(self):
        description = "clean a session"
        super(DeleteCommand, self).__init__("delete", description,
                                           ["del", "clean", "drop"])

    def add_parser(self, parser):
        subparser = super(DeleteCommand, self).add_parser(parser)
        group = subparser.add_mutually_exclusive_group()
        group.add_argument("--download", action="store_true",
                           help="delete the download directory")
        group.add_argument("--source", action="store_true",
                           help="delete the source directory")
        group.add_argument("--build", action="store_true",
                           help="delete the build directory [default]")
        group.add_argument("--clean", action="store_true",
                           help="clean the build directoryi")
        group.add_argument("--distclean", action="store_true",
                           help="distclean the build directory")
        group.add_argument("--destroot", action="store_true",
                           help="delete the destroot directory")
        return subparser

    def main(self, options, config):
        console = Console(config)
        sessionname = options.sessionname[0]
        force = options.force
        if options.distclean:
            console.distclean_session(sessionname, force)
        elif options.source:
            console.delete_source_session(sessionname, force)
        elif options.destroot:
            console.delete_destroot_session(sessionname, force)
        elif options.download:
            console.delete_download_session(sessionname, force)
        elif options.clean:
            console.clean_session(sessionname, force)
        else:
            console.delete_build_session(sessionname, force)


class DependsCommand(SessionNameCommand):

    def __init__(self):
        description = ""
        super(DependsCommand, self).__init__("depends", description,
                                             ["deps"])

    def main(self, options, config):
        Console(config).list_session_dependencies(options.sessionname[0])


class CreateCommand(Command):

    def __init__(self):
        description = "Create a new Session"
        super(CreateCommand, self).__init__("create", self.main, [],
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
        subparser.add_argument("--session-version", "-s", help="version of the new "\
                               "session. If empty jam will determine the "\
                               " version from the source file", dest="version")
        subparser.add_argument("--keep", action="store_true", 
                               help="keep temporary directory")
        subparser.add_argument("--print", dest="stdout", action="store_true",
                               help="print to stdout instead of creating a "\
                               "new session")

    def main(self, options, config):
        creator = SessionCreator(config, options.url[0], options.keep)
        if options.name:
            creator.set_name(options.name)

        if options.template:
            creator.set_template(options.template)

        if options.version:
            creator.set_version(options.version)

        creator.create(options.stdout)


class ShowCommand(SessionNameCommand):

    def __init__(self):
        description = ""
        super(ShowCommand, self).__init__("show", description)

    def add_parser(self, parser):
        subparser = super(ShowCommand, self).add_parser(parser)
        group = subparser.add_mutually_exclusive_group(required=True)
        group.add_argument("--files", help="list installed files of a session",
                           action="store_true")
        group.add_argument("--phases", help="list the current phases of a " \
                           "session", action="store_true")

    def main(self, options, config):
        console = Console(config)
        session_name = options.sessionname[0]
        if options.phases:
            console.list_session_phases(session_name)
        elif options.files:
            console.list_session_files(session_name)


class ListCommand(Command):

    def __init__(self):
        description = ""
        super(ListCommand, self).__init__("list", self.main, [],
                                          description)

    def add_parser(self, parser):
        subparser = super(ListCommand, self).add_parser(parser)
        group = subparser.add_mutually_exclusive_group(required=True)
        group.add_argument("--installed", help="show installed sessions",
                           action="store_true")
        group.add_argument("--activated", help="show installed sessions",
                           action="store_true")

    def main(self, options, config):
        console = Console(config)
        if options.installed:
            console.list_installed_sessions()
        elif options.activated:
            console.list_activated_sessions()


class SystemProvidesCommand(Command):

    def __init__(self):
        description = "add or remove software provided by the system"
        super(SystemProvidesCommand, self).__init__("systemprovide",
                                          self.main, [], description)

    def add_parser(self, parser):
        usage = "%(prog)s [global options] " + self.name + \
                " <--add|--remove> name [version]"
        subparser = super(SystemProvidesCommand, self).add_parser(parser, usage)
        group = subparser.add_mutually_exclusive_group(required=True)
        group.add_argument("--add", help="add software provided by the system",
                           action="store_true")
        group.add_argument("--remove", help="remove software provided by the " \
                           "system", action="store_true")
        subparser.add_argument("name", nargs=1, help="name of the " \
                               "software provided by the system")
        subparser.add_argument("version", nargs="?", help="version of the" \
                               " software provided by the system")

    def main(self, options, config):
        console = Console(config)
        name = options.name[0]
        version = None
        if options.version:
            version = options.version[0]
        if options.add:
            console.add_system_provides(name, version)
        elif options.remove:
            console.remove_system_provides(name)


class QuiltCommand(SessionNameCommand):

    def __init__(self):
        description = "Manage patches for a session with quilt"
        super(QuiltCommand, self).__init__("quilt", description)

    def main(self, options, config):
        console = Console(config)
        session_name = options.sessionname[0]
