# -*- coding: utf-8 -*-

# kaizen - Continuously improve, build and manage free software
#
# Copyright (C) 2014  Björn Ricks <bjoern.ricks@gmail.com>
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

from kommons.cli import Argument, OptionArgument, Subparser

from kaizen.cli.console import Console


class ListSettingsSubparser(Subparser):

    __description__ = "list all settings"

    def __call__(self, options, config):
        Console(config).list_settings()


class ListInstalledSubparser(Subparser):

    __description__ = "list all installed rules"

    def __call__(self, options, config):
        Console(config).list_installed_rules()


class ListDependenciesSubparser(Subparser):

    __description__ = "list all dependencies of a rule"

    rulename = Argument(help="name of the rule")

    def __call__(self, options, config):
        Console(config).list_rules_dependencies(options.rulename)


class ListRulesFilesSubparsers(Subparser):

    __description__ = "list all installed files of a rule"

    rulename = Argument(help="name of the rule")

    def __call__(self, options, config):
        Console(config).list_rules_files(options.rulename)


class ListSubparser(Subparser):

    __description__ = "list settings, etc."

    settings = ListSettingsSubparser()
    installed = ListInstalledSubparser()
    dependencies = ListDependenciesSubparser()
    files = ListRulesFilesSubparsers()
