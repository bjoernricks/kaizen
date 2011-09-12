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


class Phase(object):

    def __init__(self, name, value):
        self.value = value
        self.name = name

    def __cmp__(self, other):
        if self.value < other.value:
            return -1
        if self.value == other.value:
            return 0
        if self.value > other.value:
            return 1

    def __eq__(self, other):
        if not isinstance(other, Phase):
            return False
        return self.value == other.value

    def __neq__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.value

    def __repr__(self):
        return "<Phase name='%s' value='%s' id='%s'>" % (self.name, self.value,
                                                         id(self))


class Phases(object):

    def __init__(self):
        self.phases = dict()
        self.phase_names = [
                             "None",
                             "Downloaded",
                             "Extracted",
                             "Patched",
                             "Configured",
                             "Built",
                             "Destrooted",
                             "Activated",
                           ]
        for i, name in enumerate(self.phase_names):
            self.phases[name] = Phase(name, i)


    def get(self, name):
        return self.phases[name]


phases_list = Phases()
