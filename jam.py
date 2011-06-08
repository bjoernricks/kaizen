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

import jam.config
import jam.download
import jam.session
import jam.log


from jam.config import JAM_VERSION, JAM_CONFIG_FILES
from jam.external.argparse import ArgumentParser

def print_settings(logger, config):
    logger.out("Version: '%s'" % config.get("version"))
    logger.out("Debug: '%s'" % config.get("debug"))
    logger.out("Verbose: '%s'" % config.get("verbose"))
    logger.out("Dir: '%s'" % config.get("dir"))
    logger.out("Sessions: '%s'" % config.get("sessions"))
    logger.out("Destroot: '%s'" % config.get("destroot"))
    logger.out("Buildroot: '%s'" % config.get("buildroot"))
    logger.out("Downloadroot: '%s'" % config.get("downloadroot"))

def main():
    usage = "%(prog)s [options] command {arguments}"
    description = "jam - Orchestrate your software"
    version = "%(prog)s " + JAM_VERSION

    parser = ArgumentParser(usage=usage, description=description)
    parser.add_argument("--config", dest="config", help="path to the config file")
    parser.add_argument("--sessions", help="path to sessions")
    parser.add_argument("-d", "--debug", action="store_true", dest="debug",
                      help="enable debug output")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                      help="enable verbose output")
    parser.add_argument("-f", "--force", action="store_true", dest="force",
                      help="force an action e.g. re-download sources")
    parser.add_argument("--settings", action="store_true", help="print jam settings")
    parser.add_argument('--version', action='version', version=version)

    subparsers = parser.add_subparsers(dest="command", title="commands",
                                       description="valid commands",
                                       help="additional help")

    commands = ["build", "configure", "extract", "download", "destroot",
                "install", "activate", "deactivate", "update", "upgrade",
                "distclean", "clean", "depends"]
    for command in commands:
        subparser = subparsers.add_parser(command)
        subparser.add_argument("session", nargs=1)

    options = parser.parse_args()


    if options.config:
        configfiles.append(options.config)

    jamlogger = jam.log.getRootLogger()
    config = jam.config.Config(JAM_CONFIG_FILES, vars(options))

    if options.settings:
        print_settings(jamlogger, config)
        return

    if config.get("debug"):
        jamlogger.set_level(jam.log.Logger.DEBUG)
        print_settings(jamlogger, config)

    command = options.command

    manager = jam.session.SessionManager(config, options.session[0],
                                         force=options.force)
    if command == "build":
       manager.build()
    elif command == "configure":
        manager.configure()
    elif command == "extract":
        manager.extract()
    elif command == "download":
        manager.download()
    elif command == "destroot":
        manager.destroot()
    elif command == "install":
        manager.install()
    elif command == "activate":
        manager.activate()
    elif command == "deactivate":
        manager.deactivate()
    elif command == "clean":
        manager.clean()
    elif command == "distclean":
        manager.distclean()
    elif command == "depends":
        manager.depends()


main()
