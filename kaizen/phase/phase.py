# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# kaizen - Continously improve, build and manage free software
#
# Copyright (C) 2011  Björn Ricks <bjoern.ricks@gmail.com>
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


NONE = "None"
DOWNLOADED = "Downloaded"
EXTRACTED = "Extracted"
PATCHED = "Patched"
CONFIGURED = "Configured"
BUILT = "Built"
DESTROOTED = "Destrooted"
ACTIVATED = "Activated"

class UnknownPhaseError(Exception):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Phase '%s' does not exist." % (self.name)


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
                             NONE,
                             DOWNLOADED,
                             EXTRACTED,
                             PATCHED,
                             CONFIGURED,
                             BUILT,
                             DESTROOTED,
                             ACTIVATED,
                           ]
        for i, name in enumerate(self.phase_names):
            self.phases[name] = Phase(name, i)


    def get(self, name):
        if not name in self.phases:
            raise UnknownPhaseError(name)
        return self.phases[name]


phases_list = Phases()
