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

import jam.log

log = jam.log.getLogger(__file__)

class SequenceError(Exception):

    def __init__(self, sequence_name, session_name, value):
        self.sequence_name = sequence_name
        self.session_name = session_name
        self.value = value

    def __str__(self):
        return "Error while executing sequence '%s' for session '%s': %s" %\
                (self.sequence_name, self.session_name, self.value)


class Sequence(object):

    def __init__(self, name, required_phase, result_phase, method_names,
                 always=False, parent_seq=None):
        self.name = name
        self.parent_seq = parent_seq
        self.required_phase = required_phase
        self.result_phase = result_phase
        self.method_names = method_names
        self.always = always

    def must_be_called(self, session):
        return self.always or not (self.result_phase in session.get_phases())

    def __call__(self, session, force=False):
        if not self.method_names:
            log.debug("No method to call is set. Nothing to do for sequence " \
                      "'%s'." % self.name)
            return
        current_phase = session.get_current_phase()
        if current_phase < self.required_phase:
            raise SequenceError(self.name, session.session_name,
                    "session is in phase '%s' but required is '%s'" %\
                    (current_phase.name, self.required_phase.name))
        set_phase = self.call(session, force)
        if set_phase:
            session.set_current_phase(self.result_phase)

    def handle_phase(self, session):
        session.set_phase(self.result_phase)

    def call(self, session, force=False):
        call_me = self.must_be_called(session)
        if not call_me and force:
            call_me = True
            log.warn("Forcing to call a phase can have several side " \
                     "effects. You should be really aware of what " \
                     "you are doing!")
        if call_me:
            if self.parent_seq:
                self.parent_seq.call(session)
            self.call_methods(session)
            self.handle_phase(session)
            return True
        return False

    def call_methods(self, session):
        for method_name in self.method_names:
            if isinstance(method_name, basestring):
                if not hasattr(session, method_name):
                    raise SequenceError(self.name, session.session_name,
                            "No such method '%s'." % method_name)
                method = getattr(session, method_name)
            else:
                method = method_name
            method() # may raise an error

    def __repr__(self):
        return "<Sequence name='%s' id='%s'>" % (self.name, id(self))
