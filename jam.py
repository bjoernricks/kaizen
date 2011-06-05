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

from optparse import OptionParser

from jam.utils import realpath

def main():
    usage = "usage: %prog [options] command {arguments}"
    configfiles = ["/etc/jamrc", realpath("~/.jam/jamrc")]

    parser = OptionParser(usage)
    parser.add_option("--config", dest="config", help="Path to the config file")
    parser.add_option("--sessions", help="Path to sessions")
    parser.add_option("-d", "--debug", action="store_const", dest="debug",
                      const="1", help="Enable debug output")
    parser.add_option("-v", "--verbose", action="store_const", dest="verbose",
                      const="1", help="Enable verbose output")
    parser.add_option("-f", "--force", action="store_true", dest="force",
                     help="Force an action e.g. re-download sources")
    parser.add_option("--version", action="store_true",
                      help="Print version information")

    (options, args) = parser.parse_args()

    if not args:
        parser.print_help()
        return

    if options.config:
        configfiles.append(options.config)

    jamlogger = jam.log.getRootLogger()

    config = jam.config.Config(configfiles, vars(options))
    if config.get("debug"):
        jamlogger.set_level(jam.log.Logger.DEBUG)

    command = args[0]

    manager = jam.session.SessionManager(config, args[1], force=options.force)
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
