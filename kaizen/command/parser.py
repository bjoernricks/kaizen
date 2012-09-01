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

from jam.external.argparse import ArgumentParser as ArgParser, ArgumentError


class ArgumentParser(ArgParser):

    def __init__(self, usage=None, create_late=False, **kwargs):
        if not usage:
            usage = "%(prog)s [options] command {arguments}"
        description = "jam - Orchestrate your software"
        kwargs.pop("description", None)
        kwargs.pop("usage", None)
        add_help = kwargs.pop("add_help", False)
        self.args_added = False
        super(ArgumentParser, self).__init__(usage=usage,
                                             description=description,
                                             add_help=add_help, **kwargs)
        self.group = self.add_argument_group("global options")
        self.group.add_argument("--config", dest="config",
                          help="path to the config file")
        self.group.add_argument("--sessions", help="path to sessions")
        self.group.add_argument("-d", "--debug", action="store_true",
                          dest="debug",
                          help="enable debug output")
        self.group.add_argument("--settings", action="store_true",
                          help="print jam settings")
        if not create_late:
            self._add_additional_arguments()

    def _add_additional_arguments(self):
        if self.args_added:
            return
        version = "%(prog)s " + jam.__version__
        self.group.add_argument("--version", action="version", version=version)
        self.group.add_argument("-v", "--verbose", action="store_true",
                          dest="verbose",
                          help="enable verbose output")
        self.group.add_argument("-f", "--force", action="store_true",
                          dest="force",
                          help="force an action e.g. re-download sources")
        self.group.add_argument("--buildjobs", type=int, metavar="JOBS",
                          help="set number of build jobs")
        self.set_help()
        self.args_added = True

    def parse_known_args(self, args=None, namespace=None):
        args = super(ArgumentParser, self).parse_known_args(args, namespace)
        self._add_additional_arguments()
        return args

    def set_help(self):
        self.group.add_argument("--help", "-h", action="help",
                help="show this help message and exit. To get help "\
                        "for a command use 'command --help'")


class NameVersionParser(object):

    def __init__(self):
        self.names = []

    def parse(self, names):
        cur_name = None
        for name in names:
            if name.startswith("@"):
                if cur_name is None:
                    raise ArgumentError(None, "Version parameter %r must be "
                                        "passed after the session name" % name)
                self.names.append((cur_name, name[1:]))
                cur_name = None
            else:
                if not cur_name is None:
                    self.names.append((cur_name, ""))
                cur_name = name

        if not cur_name is None:
            self.names.append((cur_name, ""))

        return self.names
