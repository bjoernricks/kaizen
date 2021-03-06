# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# kaizen - Continuously improve, build and manage free software
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

import kaizen.logging

from kaizen.error import KaizenError
from kaizen.phase.phase import phases_list

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

class SequenceError(KaizenError):

    def __init__(self, sequence_name, rules_name, value):
        self.sequence_name = sequence_name
        self.rules_name = rules_name
        self.value = value

    def __str__(self):
        return "Error while executing sequence '%s' for rules '%s': %s" %\
                (self.sequence_name, self.rules_name, self.value)


class Sequence(object):

    def __init__(self, name, pre_sequence_name, post_sequence_name,
                 required_phase_name, set_phase_name, unset_phase_name,
                 method_names):
        self.log = kaizen.logging.getLogger(self)
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

    def __call__(self, rules, force=False):
        if self.pre_sequence:
            self.pre_sequence(rules)

        call_me = self.must_be_run(rules)
        if not call_me and force:
            call_me = True
            self.log.warn("Forcing to call a phase can have several side " \
                          "effects. You should be really aware of what " \
                          "you are doing!")
        if call_me:
            self.call_methods(rules)
            self.handle_phase(rules)
            self.is_run = True

        if self.post_sequence:
            self.post_sequence(rules)

    def handle_phase(self, rules):
        if self.set_phase:
            rules.set_phase(self.set_phase)
        if self.unset_phase:
            rules.unset_phase(self.unset_phase)

    def must_be_run(self, rules):
        if self.pre_sequence:
            if self.pre_sequence.has_been_run():
                return True

        return not (self.set_phase in rules.get_phases())

    def has_been_run(self):
        return self.is_run

    def call_methods(self, rules):
        for method_name in self.method_names:
            if isinstance(method_name, basestring):
                if not hasattr(rules, method_name):
                    raise SequenceError(self.name, rules.rules_name,
                            "No such method '%s'." % method_name)
                method = getattr(rules, method_name)
            else:
                method = method_name
            method() # may raise an error

    def __repr__(self):
        return "<Sequence name='%s' id='%s'>" % (self.name, id(self))


class SetSequence(Sequence):

    def __init__(self, name, pre_sequence_name, set_phase_name):
        super(SetSequence, self).__init__(name, pre_sequence_name, None, None,
                                          set_phase_name, None, [name])

class UnSetSequence(Sequence):

    def __init__(self, name, pre_sequence_name, required_phase_name):
        super(UnSetSequence, self).__init__(name, pre_sequence_name, None,
                                            required_phase_name, None,
                                            required_phase_name, [name])

    def must_be_run(self, rules):
        return self.unset_phase in rules.get_phases()
