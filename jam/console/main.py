#!/usr/bin/env python
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

import sys

import jam.logging
import jam.command

from jam.config import Config, JAM_CONFIG_FILES
from jam.utils import Loader
from jam.command.parser import ArgumentParser

class Main(object):

    def print_settings(self):
        jam.logging.out("Version:      %r" % self.config.get("version"))
        jam.logging.out("Debug:        %r" % self.config.get("debug"))
        jam.logging.out("Verbose:      %r" % self.config.get("verbose"))
        jam.logging.out("Sessions:     %r" % self.config.get("sessions"))
        jam.logging.out("Root:         %r" % self.config.get("rootdir"))
        jam.logging.out("Destroot:     %r" % self.config.get("destroot"))
        jam.logging.out("Buildroot:    %r" % self.config.get("buildroot"))
        jam.logging.out("Downloadroot: %r" % self.config.get("downloadroot"))
        jam.logging.out("Buildjobs:    %r\n" % self.config.get("buildjobs"))

    def main(self):
        if sys.version_info < (2, 4):
            raise Exception("jam requires Python 2.4 or higher.")

        formatter = jam.logging.Formatter("%(levelname)s - %(name)s - %(message)s")
        self.logger = jam.logging.getRootLogger()
        handler = jam.logging.ColorStreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        parser = ArgumentParser(create_late=True)
        all_args = sys.argv[1:]
        args = parser.parse_known_args(all_args)
        options = args[0]

        if options.config:
            configfiles.append(options.config)

        if options.settings:
            self.print_settings()
            return

        #parse config for debug option
        config = Config(JAM_CONFIG_FILES, vars(options))

        if config.get("debug"):
            self.logger.setLevel(jam.logging.DEBUG)

        subparsers = parser.add_subparsers(dest="command", title="commands",
                                           description="valid commands",
                                           metavar="")

        for command in Loader().classes(jam.command, all=True):
            command().add_parser(subparsers)

        options = parser.parse_args(all_args)

        self.config = Config(JAM_CONFIG_FILES, vars(options))

        if self.config.get("debug"):
            self.print_settings()

        if not hasattr(options, "func"):
            parser.print_help()
            return

        options.func(options, self.config)


def main():
    Main().main()

if __name__ == "__main__":
    main()
