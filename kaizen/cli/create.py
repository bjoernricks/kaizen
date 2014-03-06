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


class CreateRuleSubparser(Subparser):

    __description__ = "create new rule from an url"

    rulename = Argument(help="name of the rule")
    url = Argument(help="url to download source file")
    template = OptionArgument(choices=["cmake", "python", "autotools"],
                              help="specify a template for the" \
                              " new rules. If empty kaizen will guess the" \
                              " right one.")
    name = OptionArgument(help="name of the new rule. If empty kaizen will " \
                          "determine the name from the source file")
    rulesversion = OptionArgument(help="version of the new " \
                            "rule. If empty kaizen will determine the " \
                            " version from the source file",
                            metavar="VERSION")
    keep = OptionArgument(action="store_true",
                          help="keep temporary directory")
    stdout = OptionArgument(dest="stdout", action="store_true",
                            help="print to stdout instead of creating a " \
                            "new rule")
