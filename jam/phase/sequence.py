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


class SequenceError(Exception):

    def __init__(self, sequence_name, session_name, value):
        self.sequence_name = sequence_name
        self.session_name = session_name
        self.value = value

    def __str__(self):
        return "Error while executing sequence '%s' for session '%s': %s" %\
                (self.sequence_name, self.session_name, self.value)


class SequenceEntry(object):

    def __init__(self, phase, method_name, always = False):
        self.phase = phase
        self.method_name = method_name
        self.always = always


class Sequence(object):

    def __init__(self, name, required_phase, result_phase,
                 parent_seq=None):
        self.name = name
        self.parent_seq = parent_seq
        self.required_phase = required_phase
        self.result_phase = result_phase
        self.sequence = []

    def add(self, phase, method_name, always = False):
        self.add_entry(SequenceEntry(phase, method_name, always))

    def add_entry(self, entry):
        self.sequence.append(entry)

    def call(self, session, force=False):
        current_phase = session.get_current_phase()
        if self.parent_seq:
            self.parent_seq.call(session)
        if current_phase < self.required_phase:
            raise SequenceError(self.name, session.name,
                    "session is in phase '%s' but required is '%s'" %\
                    (current_phase.name, self.required_phase.name))
        set_phase = False
        for entry in self.sequence:
            if current_phase < entry.phase or entry.always or force:
                method = getattr(session, entry.method_name)
                method()
                set_phase = True
        # only set phase if method calls were successfully executed
        if set_phase:
            session.set_phase(self.result_phase)

