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

import jam.logging

from jam.error import JamError
from jam.phase.phase import phases_list

DOWNLOAD = "download"
EXTRACT = "extract"
PATCH = "patch"
CONFIGURE = "configure"
BUILD = "build"
DESTROOT = "destroot"
ACTIVATE = "activate"
DEACTIVATE = "deactivate"
DELETE_DESTROOT = "delete_destroot"
DELETE_BUILD = "delete_build"
DISTCLEAN = "distclean"
UNPATCH = "unpatch"
DELETE_SOURCE = "delete_source"
DELETE_DOWNLOAD = "delete_download"

class SequenceError(JamError):

    def __init__(self, sequence_name, session_name, value):
        self.sequence_name = sequence_name
        self.session_name = session_name
        self.value = value

    def __str__(self):
        return "Error while executing sequence '%s' for session '%s': %s" %\
                (self.sequence_name, self.session_name, self.value)


class Sequence(object):

    def __init__(self, name, pre_sequence_name, post_sequence_name,
                 required_phase_name, set_phase_name, unset_phase_name,
                 method_names):
        self.log = jam.logging.getLogger(self)
        self.name = name
        self.pre_sequence_name = pre_sequence_name
        self.post_sequence_name = post_sequence_name
        self.required_phase_name = required_phase_name
        if set_phase_name:
            self.set_phase = phases_list.get(set_phase_name)
        else:
            self.set_phase = None
        if unset_phase_name:
            self.unset_phase = phases_list.get(unset_phase_name)
        else:
            self.unset_phase = None
        self.method_names = method_names
        self.is_run = False
        self.pre_sequence = None
        self.post_sequence = None

    def set_pre_sequence(self, sequence):
        self.pre_sequence = sequence

    def set_post_sequence(self, sequence):
        self.post_sequence = sequence

    def __call__(self, session, force=False):
        if self.pre_sequence:
            self.pre_sequence(session)

        call_me = self.must_be_run(session)
        if not call_me and force:
            call_me = True
            self.log.warn("Forcing to call a phase can have several side " \
                          "effects. You should be really aware of what " \
                          "you are doing!")
        if call_me:
            self.call_methods(session)
            self.handle_phase(session)
            self.is_run = True

        if self.post_sequence:
            self.post_sequence(session)

    def handle_phase(self, session):
        if self.set_phase:
            session.set_phase(self.set_phase)
        if self.unset_phase:
            session.unset_phase(self.unset_phase)

    def must_be_run(self, session):
        if self.pre_sequence:
            if self.pre_sequence.has_been_run():
                return True

        phases = session.get_phases()
        for phase in self.set_phase_name:
            if not phase in phases:
                return True
        return False

    def has_been_run(self):
        return self.is_run

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


class UnSequence(Sequence):

    def __init__(self, name, required_phase, result_phase, unset_phase,
                 method_names, always=False, parent_seq=None):
        super(UnSequence, self).__init__(name, required_phase, result_phase,
                                         method_names, always, parent_seq)
        self.unset_phase = unset_phase

    def must_be_called(self, session):
        return self.always or (self.unset_phase in session.get_phases())

    def handle_phase(self, session):
        session.unset_phase(self.unset_phase)

    def call(self, session, force=False):
        if self.parent_seq:
            self.parent_seq.call(session)
        call_me = self.must_be_called(session)
        if not call_me and force:
            call_me = True
            self.log.warn("Forcing to call a phase can have several side " \
                          "effects. You should be really aware of what " \
                          "you are doing!")
        if call_me:
            self.call_methods(session)
            self.handle_phase(session)
            return True
        return False


class SetSequence(Sequence):

    def __init__(self, name, pre_sequence_name, set_phase_name):
        super(SetSequence, self).__init__(name, pre_sequence_name, None, None,
                                          set_phase_name, None, [name])
