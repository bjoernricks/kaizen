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

from kommons.cli import Parser, OptionArgument, Subparser

from kaizen.cli.create import CreateRuleSubparser
from kaizen.cli.list import ListSubparser
from kaizen.config import Config, KAIZEN_CONFIG_FILES
from kaizen.rules.error import RulesError


class KaizenParser(Parser):

    __description__ = "kaizen - build and manage free software"

    debug = OptionArgument(help="print debug output", action="store_true")
    verbose = OptionArgument(help="enable verbose output from rules",
                             action="store_true")
    config = OptionArgument(help="path to the config file")

    list = ListSubparser()
    create = CreateRuleSubparser()


if __name__ == "__main__":

    kparser = KaizenParser()
    args = kparser.parse_args()
    config = Config(KAIZEN_CONFIG_FILES, vars(args))
    try:
        args.func(args, config)
    except RulesError, e:
        print e
