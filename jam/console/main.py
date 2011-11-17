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

import jam.log
import jam.command

from jam.config import Config, JAM_CONFIG_FILES
from jam.external.argparse import ArgumentParser
from jam.utils import Loader

class Main(object):

    def print_settings(self):
        self.logger.out("Version: '%s'" % self.config.get("version"))
        self.logger.out("Debug: '%s'" % self.config.get("debug"))
        self.logger.out("Verbose: '%s'" % self.config.get("verbose"))
        self.logger.out("Root: '%s'" % self.config.get("rootdir"))
        self.logger.out("Sessions: '%s'" % self.config.get("sessions"))
        self.logger.out("Destroot: '%s'" % self.config.get("destroot"))
        self.logger.out("Buildroot: '%s'" % self.config.get("buildroot"))
        self.logger.out("Downloadroot: '%s'" % self.config.get("downloadroot"))

    def main(self):
        if sys.version_info < (2, 4):
            raise Exception("jam requires Python 2.4 or higher.")
        usage = "%(prog)s [options] command {arguments}"
        description = "jam - Orchestrate your software"
        version = "%(prog)s " + jam.__version__

        self.logger = jam.log.getRootLogger()

        parser = ArgumentParser(usage=usage, description=description,
                                add_help=False)
        parser.add_argument("--config", dest="config",
                            help="path to the config file")
        parser.add_argument("--sessions", help="path to sessions")
        parser.add_argument("-d", "--debug", action="store_true", dest="debug",
                          help="enable debug output")
        parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                          help="enable verbose output")
        parser.add_argument("-f", "--force", action="store_true", dest="force",
                          help="force an action e.g. re-download sources")
        parser.add_argument("--settings", action="store_true",
                            help="print jam settings")
        parser.add_argument("--version", action="version", version=version)

        known_args = parser.parse_known_args()
        options = known_args[0]

        if options.config:
            configfiles.append(options.config)

        self.config = Config(JAM_CONFIG_FILES, vars(options))

        if options.settings:
            self.print_settings()
            return

        if self.config.get("debug"):
            self.logger.set_level(jam.log.Logger.DEBUG)
            self.print_settings()

        subparsers = parser.add_subparsers(dest="command", title="commands",
                                           description="valid commands",
                                           metavar="")

        for command in Loader().classes(jam.command, all=True):
            command(self.config).add_parser(subparsers)

        parser.add_argument("--help", "-h", action="help",
                            help="show this help message and exit. To get help "\
                                 "for a command use 'command --help'")

        options = parser.parse_args()
        if not hasattr(options, "func"):
            parser.print_help()
            return
        options.func(options)


def main():
    Main().main()

if __name__ == "__main__":
    main()
