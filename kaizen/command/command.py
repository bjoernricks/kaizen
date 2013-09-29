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

from kaizen.rules.create import RulesCreator
from kaizen.console.console import Console
from kaizen.command.parser import NameVersionParser


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
        subparser = parser.add_parser(self.name, #aliases=self.aliases,
                                      usage=self.usage,
                                      description=self.description,
                                      help=self.description)
        subparser.set_defaults(func=self.func)
        return subparser

    def get_func(self):
        return func


class CommandWithSubCommands(Command):

    def __init__(self, name, usage, description):
        self.usage = usage
        super(CommandWithSubCommands, self).__init__(name, self.pre_main, [],
                                                     description)

    def add_parser(self, parser):
        self.cmd = super(CommandWithSubCommands, self).add_parser(parser,
                                                                  self.usage)
        subparser = self.cmd.add_subparsers(dest="subcommand",
            title="subcommands", description="valid subcommands", metavar="")
        self.add_cmds(subparser)

    def pre_main(self, options, config):
        if not options.subcommand:
            self.cmd.print_help()
            return
        self.main(options, config)

    def add_cmds(self, subparser):
        pass

    def main(self, options, config):
        pass


class RulesNameCommand(Command):

    def __init__(self, name, description=None, aliases=[]):
        super(RulesNameCommand, self).__init__(name, self.main,
                                                 aliases, description)

    def add_parser(self, parser):
        usage = "%(prog)s [global options] " + self.name + " <rulesname> " \
                "{arguments}"
        subparser = super(RulesNameCommand, self).add_parser(parser, usage)
        subparser.add_argument("rulesname", nargs=1)
        return subparser

    def main(self, options, config):
        pass


class BuildCommand(RulesNameCommand):

    def __init__(self):
        description = "Run build process"
        super(BuildCommand, self).__init__("build", description)

    def main(self, options, config):
        Console(config).build_rules(options.rulesname[0],
                                      options.force)


class PatchCommand(RulesNameCommand):

    def __init__(self):
        description = "Apply patches to sources"
        super(PatchCommand, self).__init__("patch", description)

    def main(self, options, config):
        Console(config).patch_rules(options.rulesname[0],
                                      options.force)


class UnPatchCommand(RulesNameCommand):

    def __init__(self):
        description = "Revert patches applied sources"
        super(UnPatchCommand, self).__init__("unpatch", description)

    def main(self, options, config):
        Console(config).unpatch_rules(options.rulesname[0],
                                        options.force)


class ConfigureCommand(RulesNameCommand):

    def __init__(self):
        description = "Configure rules"
        super(ConfigureCommand, self).__init__("configure", description,
                                               ["conf"])

    def main(self, options, config):
        Console(config).configure_rules(options.rulesname[0],
                                          options.force)


class ExtractCommand(RulesNameCommand):

    def __init__(self):
        description = "Extract downloaded sources"
        super(ExtractCommand, self).__init__("extract", description, [])

    def main(self, options, config):
        Console(config).extract_rules(options.rulesname[0],
                                        options.force)


class DownloadCommand(RulesNameCommand):

    def __init__(self):
        description = "Download sources of rules"
        super(DownloadCommand, self).__init__("download", description,
                                              ["fetch"])

    def main(self, options, config):
        Console(config).download_rules(options.rulesname[0],
                                         options.all, options.force)

    def add_parser(self, parser):
        subparser = super(DownloadCommand, self).add_parser(parser)
        subparser.add_argument("--all", action="store_true",
                               help="download also sources from dependencies")


class DestrootCommand(RulesNameCommand):

    def __init__(self):
        description = "Install rules into the destroot directory"
        super(DestrootCommand, self).__init__("destroot", description,
                                              ["dest"])

    def main(self, options, config):
        Console(config).destroot_rules(options.rulesname[0],
                                         options.force)


class InstallCommand(RulesNameCommand):

    def __init__(self):
        description = "Install rules"
        super(InstallCommand, self).__init__("install", description,
                                             ["inst"])

    def main(self, options, config):
        Console(config).install_rules(options.rulesname[0],
                                        options.force)


class UninstallCommand(RulesNameCommand):

    def __init__(self):
        description = "Uninstall rules"
        super(UninstallCommand, self).__init__("uninstall", description,
                                               ["uninst"])
    def add_parser(self, parser):
        parser = super(UninstallCommand, self).add_parser(parser)
        parser.add_argument("version", nargs='?', default=None)
        return parser

    def main(self, options, config):
        Console(config).uninstall_rules(options.rulesname[0],
                                          options.version,
                                          options.force)


class ActivateCommand(RulesNameCommand):

    def __init__(self):
        description = "Activate rules"
        super(ActivateCommand, self).__init__("activate", description)

    def main(self, options, config):
        Console(config).activate_rules(options.rulesname[0],
                                         options.force)


class DeactivateCommand(RulesNameCommand):

    def __init__(self):
        description = "Deactivate rules"
        super(DeactivateCommand, self).__init__("deactivate", description)

    def main(self, options, config):
        Console(config).deactivate_rules(options.rulesname[0],
                                                options.force)


class DeleteCommand(RulesNameCommand):

    def __init__(self):
        description = "Delete (parts of) rules"
        super(DeleteCommand, self).__init__("delete", description, [])

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
        rulesname = options.rulesname[0]
        force = options.force
        if options.distclean:
            console.distclean_rules(rulesname, force)
        elif options.source:
            console.delete_source_rules(rulesname, force)
        elif options.destroot:
            console.delete_destroot_rules(rulesname, force)
        elif options.download:
            console.delete_download_rules(rulesname, force)
        elif options.clean:
            console.clean_rules(rulesname, force)
        else:
            console.delete_build_rules(rulesname, force)


class DependsCommand(RulesNameCommand):

    def __init__(self):
        description = "List dependencies of rules"
        super(DependsCommand, self).__init__("depends", description,
                                             ["deps"])

    def main(self, options, config):
        Console(config).list_rules_dependencies(options.rulesname[0])


class CreateCommand(Command):

    def __init__(self):
        description = "Create new Rules"
        super(CreateCommand, self).__init__("create", self.main, [],
                                            description)

    def add_parser(self, parser):
        usage = "%(prog)s [options] " + self.name + " url {arguments}"
        subparser = super(CreateCommand, self).add_parser(parser, usage)
        subparser.add_argument("url", nargs=1, help="url to download source file")
        subparser.add_argument("--template", choices=["cmake", "python",
                               "autotools"], help="specify a template for the"\
                               " new rules. If empty kaizen will guess the"\
                               " right one.")
        subparser.add_argument("--name", "-n", help="name of the new "\
                               "rules. If empty kaizen will determine the "\
                               " name from the source file")
        subparser.add_argument("--rules-version", "-s", help="version of the new "\
                               "rules. If empty kaizen will determine the "\
                               " version from the source file", dest="version")
        subparser.add_argument("--keep", action="store_true", 
                               help="keep temporary directory")
        subparser.add_argument("--print", dest="stdout", action="store_true",
                               help="print to stdout instead of creating a "\
                               "new rules")

    def main(self, options, config):
        creator = RulesCreator(config, options.url[0], options.keep)
        if options.name:
            creator.set_name(options.name)

        if options.template:
            creator.set_template(options.template)

        if options.version:
            creator.set_version(options.version)

        creator.create(options.stdout)


class ShowCommand(CommandWithSubCommands):

    def __init__(self):
        name = "show"
        description = "Show information about rules"
        usage = "%(prog)s [global options] " + name + \
                " <files|phases> rulesname"
        super(ShowCommand, self).__init__(name, usage, description)

    def add_cmds(self, subparser):
        usage = "%(prog)s [global options] " + self.name + \
                " files rulesname"
        cmd = subparser.add_parser("files", help="list installed files of a " \
                                   "rules", usage=usage)
        self._add_args(cmd)
        usage = "%(prog)s [global options] " + self.name + \
                " phases rulesname"
        cmd = subparser.add_parser("phases", help="list the current phases " \
                                   "rules", usage=usage)
        self._add_args(cmd)

    def main(self, options, config):
        console = Console(config)
        rules_name = options.rulesname[0]
        if options.subcommand == "phases":
            console.list_rules_phases(rules_name)
        elif options.subcommand == "files":
            console.list_rules_files(rules_name)

    def _add_args(self, cmd):
        cmd.add_argument("rulesname", nargs=1)


class ListCommand(CommandWithSubCommands):

    def __init__(self):
        description = ""
        name = "list"
        usage = "%(prog)s [global options] " + name + \
                " <installed|activated>"
        super(ListCommand, self).__init__(name, usage, description)

    def add_cmds(self, subparser):
        usage = "%(prog)s [global options] " + self.name + "installed"
        cmd = subparser.add_parser("installed", help="show installed rules",
                                   usage=usage)
        usage = "%(prog)s [global options] " + self.name +  "activated"
        cmd = subparser.add_parser("activated", help="show activated rules",
                                   usage=usage)

    def main(self, options, config):
        console = Console(config)
        if options.subcommand == "installed":
            console.list_installed_rules()
        elif options.subcommand == "activated":
            console.list_activated_rules()


class SystemProvidesCommand(CommandWithSubCommands):

    def __init__(self):
        name = "systemprovide"
        description = "Add or remove software provided by the system"
        usage = "%(prog)s [global options] " + name + \
                " add name1 [@version] [name2 [@version] ...]\n" + \
                "       %(prog)s [global options] " + name + \
                " remove name1 [name2 ...]\n" + \
                "       %(prog)s [global options] " + name + " list"
        super(SystemProvidesCommand, self).__init__(name, usage,  description)

    def add_cmds(self, subparser):
        usage = "%(prog)s [global options] " + self.name + \
                " add name1 [@version] [name2 [@version] ...]"
        cmd = subparser.add_parser("add", help="add software provided by " \
                                   "the system", usage=usage)
        self._add_args(cmd)
        usage = "%(prog)s [global options] " + self.name + \
                " remove name1 [name2 ...]"
        cmd = subparser.add_parser("remove", help="remove software provided " \
                                   "the system", usage=self.usage)
        self._add_args(cmd)
        usage = "%(prog)s [global options] " + self.name + \
                " list"
        cmd = subparser.add_parser("list", help="list software provided " \
                                   "the system", usage=self.usage)

    def main(self, options, config):
        console = Console(config)
        if options.subcommand == "list":
            console.list_system_provides()
            return
        if options.subcommand == "add":
            names = NameVersionParser().parse(options.name)
            console.add_system_provides(names)
        elif options.subcommand == "remove":
            names = options.name
            console.remove_system_provides(names)

    def _add_args(self, cmd):
        cmd.add_argument("name", nargs="+", help="name of the " \
                                "software provided by the system and optional "
                                "version")


class QuiltCommand(CommandWithSubCommands):

    def __init__(self):
        name = "quilt"
        description = "Manage patches for rules with quilt"
        usage = "%(prog)s [global options] " + name + \
                " <pop|push> [-a] rulesname\n" + \
                "                            " + name + " refresh " + \
                "rulesname\n" + \
                "                            " + name + " new " + \
                "patchname rulesname\n" + \
                "                            " + name + " delete " + \
                "rulesname\n" + \
                "                            " + name + " edit " + \
                "<file1, file2, ...> rulesname\n" + \
                "                            " + name + " import " + \
                "<patch1, patch2, ...> rulesname\n"
        super(QuiltCommand, self).__init__(name, usage, description)

    def main(self, options, config):
        console = Console(config)
        rules_name = options.rulesname[0]

    def _get_usage(self, cmd, extra=None):
        usage = "%(prog)s [global options] " + self.name + " " + cmd + " "
        if extra:
            usage = usage + extra + " "
        usage = usage + "rulesname"
        return usage


    def add_cmds(self, subparser):
        cmd_str = "pop"
        cmd = subparser.add_parser(cmd_str, help="remove patch(es) from the " \
                                   "stack of applied patches.",
                                   usage=self._get_usage(cmd_str, "[-a]"))
        cmd.add_argument("-a", dest="all", help="remove all applied patches",
                action="store_true")
        self._add_args(cmd)

        cmd_str = "push"
        cmd = subparser.add_parser(cmd_str, help="apply patch(es) from the " \
                                   "series file", usage=self._get_usage(cmd_str,
                                   "[-a]"))
        cmd.add_argument("-a", dest="all", help="apply all patches",
                         action="store_true")
        self._add_args(cmd)

        cmd_str = "refresh"
        cmd = subparser.add_parser(cmd_str, help="refreshes the topmost patch",
                                   usage=self._get_usage(cmd_str))
        self._add_args(cmd)

        cmd_str = "new"
        cmd = subparser.add_parser(cmd_str, help="create a new patch with the" \
                                   "specified patch name, and insert it after" \
                                   "the topmost patch",
                                   usage=self._get_usage(cmd_str, "patchname"))
        cmd.add_argument("patchname", nargs=1, help="name of the new patch")
        self._add_args(cmd)

        cmd_str = "delete"
        cmd = subparser.add_parser(cmd_str, help="remove the topmost patch " \
                                   "from the series file",
                                   usage=self._get_usage(cmd_str))
        self._add_args(cmd)

        cmd_str = "import"
        cmd = subparser.add_parser(cmd_str, help="Import external patches. " \
                                   "The patches will be inserted following " \
                                   "the current top patch, and must be pushed" \
                                   " after import to apply them",
                                   usage=self._get_usage(cmd_str, "patchname"))
        cmd.add_argument("patches", nargs="+", help="list of patches")
        self._add_args(cmd)

        cmd_str = "edit"
        cmd = subparser.add_parser(cmd_str, help="Edit the specified file(s)" \
                                   " in $EDITOR after adding it (them) to " \
                                   "the topmost patch",
                                   usage=self._get_usage(cmd_str))
        cmd.add_argument("files", nargs="+", help="file to edit")
        self._add_args(cmd)

    def _add_args(self, cmd):
        cmd.add_argument("rulesname", nargs=1, help="name of the rules " \
                "to patch")

    def main(self, options, config):
        console = Console(config)
        subcmd = options.subcommand
        rulesname = options.rulesname[0]
        if subcmd == "push":
            console.quilt_push(rulesname, options.all)
        elif subcmd == "pop":
            console.quilt_pop(rulesname, options.all)
        elif subcmd == "refresh":
            console.quilt_refresh(rulesname)
        elif subcmd == "new":
            console.quilt_new(rulesname, options.patchname[0])
        elif subcmd == "delete":
            console.quilt_delete(rulesname)
        elif subcmd == "import":
            console.quilt_import(rulesname, options.patches)
        elif subcmd == "edit":
            console.quilt_edit(rulesname, options.files)


class UpgradeCommand(Command):

    def __init__(self):
        description = "Upgrade the current kaizen installation"
        super(UpgradeCommand, self).__init__("upgrade", self.main, [],
                                             description)

    def add_parser(self, parser):
        usage = "%(prog)s [global options] " + self.name + "{arguments}"
        subparser = super(UpgradeCommand, self).add_parser(parser, usage)
        return subparser

    def main(self, options, config):
        console = Console(config)
        console.upgrade()
