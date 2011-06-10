#!/usr/bin/env python
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


import jam.log
import jam.command

from jam.config import Config, JAM_VERSION, JAM_CONFIG_FILES
from jam.external.argparse import ArgumentParser
from jam.utils import Loader

def print_settings(logger, config):
    logger.out("Version: '%s'" % config.get("version"))
    logger.out("Debug: '%s'" % config.get("debug"))
    logger.out("Verbose: '%s'" % config.get("verbose"))
    logger.out("Root: '%s'" % config.get("rootdir"))
    logger.out("Sessions: '%s'" % config.get("sessions"))
    logger.out("Destroot: '%s'" % config.get("destroot"))
    logger.out("Buildroot: '%s'" % config.get("buildroot"))
    logger.out("Downloadroot: '%s'" % config.get("downloadroot"))

def main():
    usage = "%(prog)s [options] command {arguments}"
    description = "jam - Orchestrate your software"
    version = "%(prog)s " + JAM_VERSION

    jamlogger = jam.log.getRootLogger()

    parser = ArgumentParser(usage=usage, description=description, add_help=False)
    parser.add_argument("--config", dest="config", help="path to the config file")
    parser.add_argument("--sessions", help="path to sessions")
    parser.add_argument("-d", "--debug", action="store_true", dest="debug",
                      help="enable debug output")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                      help="enable verbose output")
    parser.add_argument("-f", "--force", action="store_true", dest="force",
                      help="force an action e.g. re-download sources")
    parser.add_argument("--settings", action="store_true", help="print jam settings")
    parser.add_argument("--version", action="version", version=version)

    known_args = parser.parse_known_args()
    options = known_args[0]

    if options.config:
        configfiles.append(options.config)

    config = Config(JAM_CONFIG_FILES, vars(options))

    if options.settings:
        print_settings(jamlogger, config)
        return

    if config.get("debug"):
        jamlogger.set_level(jam.log.Logger.DEBUG)
        print_settings(jamlogger, config)

    subparsers = parser.add_subparsers(dest="command", title="commands",
                                       description="valid commands",
                                       help="additional help")

    for command in Loader().classes(jam.command, all=True):
        command(config).add_parser(subparsers)

    parser.add_argument("--help", "-h", action="help",
                        help="show this help message and exit. To get help "\
                             "for a command use 'command --help'")

    options = parser.parse_args()
    options.func(options)


main()
