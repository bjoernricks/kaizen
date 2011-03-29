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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import logging

import jam.download
import jam.session

from optparse import OptionParser

def main():
    usage = "usage: %prog [options] command {arguments}"

    parser = OptionParser(usage)
    parser.add_option("--config", dest="config", help="Path to the config file")
    parser.add_option("--sessions", help="Path to sessions")
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      help="Enable debug output")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="Enable verbose output")
    parser.add_option("--version", action="store_true",
                      help="Print version information")

    (options, args) = parser.parse_args()

    if not args:
        parser.print_help()
        return

    logger = logging.getLogger("jam")
    logger.addHandler(logging.StreamHandler())

    config = {}
    if options.debug:
        logger.setLevel(logging.DEBUG)
        config["debug"] = True

    if options.verbose:
        config["verbose"] = True

    if options.sessions:
        config["jam_sessions"] = options.sessions

    session_config = jam.session.SessionConfig(config)

    command = args[0]

    manager = jam.session.SessionManager(session_config, args[1])
    if command == "build":
       manager.build()
    elif command == "extract":
        manager.extract()
    elif command == "download":
        manager.download()

main()
