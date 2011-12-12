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

import jam

from jam.external.argparse import ArgumentParser as ArgParser


class ArgumentParser(ArgParser):

    def __init__(self, usage=None):
        if not usage:
            usage = "%(prog)s [options] command {arguments}"
        description = "jam - Orchestrate your software"
        version = "%(prog)s " + jam.__version__
        super(ArgumentParser, self).__init__(usage=usage,
                                             description=description,
                                             add_help=False)
        self.add_argument("--config", dest="config",
                            help="path to the config file")
        self.add_argument("--sessions", help="path to sessions")
        self.add_argument("-d", "--debug", action="store_true", dest="debug",
                          help="enable debug output")
        self.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                          help="enable verbose output")
        self.add_argument("-f", "--force", action="store_true", dest="force",
                          help="force an action e.g. re-download sources")
        self.add_argument("--settings", action="store_true",
                            help="print jam settings")
        self.add_argument("--version", action="version", version=version)

    def set_help(self):
        self.add_argument("--help", "-h", action="help",
                          help="show this help message and exit. To get help "\
                               "for a command use 'command --help'")
