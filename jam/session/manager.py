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

import os.path

import jam.log

from jam.session.error import SessionError
from jam.session.wrapper import SessionWrapper
from jam.session.depend import DependencyAnalyser
from jam.phase.phase import Phases
from jam.phase.sequence import Sequence, UnSequence


class SessionManager(object):

    url = []
    patches = []

    def __init__(self, config, name, force=False):
        self.config = config
        self.force = force
        self.session_name = name
        self.log = jam.log.getLogger("jam.sessionmanager")
        self.session_wrapper = SessionWrapper(name, config, force)
        self.phases = Phases()
        self.init_sequences()

    def init_sequences(self):
        self.download_seq = Sequence("download", self.phases.get("None"),
                                     self.phases.get("Downloaded"),
                                     ["download"])

        self.extract_seq = Sequence("extract", self.phases.get("None"),
                                    self.phases.get("Extracted"), ["extract"],
                                    False, self.download_seq)
        self.patch_seq = Sequence("patch", self.phases.get("None"),
                                  self.phases.get("Patched"), ["patch"], False,
                                  self.extract_seq)
        self.configure_seq = Sequence("configure",
                                      self.phases.get("None"),
                                      self.phases.get("Configured"),
                                      ["configure"], False, self.patch_seq)
        self.build_seq = Sequence("build", self.phases.get("None"),
                                  self.phases.get("Built"), ["build"], False,
                                  self.configure_seq)
        self.destroot_seq = Sequence("destroot",
                                     self.phases.get("None"),
                                     self.phases.get("Destrooted"),
                                     ["destroot"], False, self.build_seq)
        self.activate_seq = Sequence("activate",
                                     self.phases.get("None"),
                                     self.phases.get("Activated"), ["activate"],
                                     False, self.destroot_seq)
        self.deactivate_seq = UnSequence("deactivate",
                                         self.phases.get("Activated"),
                                         self.phases.get("Destrooted"),
                                         self.phases.get("Activated"),
                                         ["deactivate"])
        self.delete_destroot_seq = UnSequence("delete_destroot",
                                              self.phases.get("Destrooted"),
                                              self.phases.get("Built"),
                                              self.phases.get("Destrooted"),
                                              ["delete_destroot"], False,
                                              self.deactivate_seq)
        self.distclean_seq = UnSequence("distclean",
                                        self.phases.get("Configured"),
                                        self.phases.get("Built"),
                                        self.phases.get("Configured"),
                                        ["distclean"], False,
                                        self.delete_destroot_seq)
        self.delete_build_seq = UnSequence("delete_destroot",
                                           self.phases.get("Built"),
                                           self.phases.get("Patched"),
                                           self.phases.get("Built"),
                                           ["delete_build"], False,
                                           self.distclean_seq)
        self.unpatch_seq = UnSequence("unpatch",
                                      self.phases.get("Patched"),
                                      self.phases.get("Extracted"),
                                      self.phases.get("Patched"),
                                      ["unpatch"], False,
                                      self.delete_build_seq)
        self.delete_source_seq = UnSequence("delete_source",
                                            self.phases.get("Extracted"),
                                            self.phases.get("Downloaded"),
                                            self.phases.get("Extracted"),
                                            ["delete_source"], False,
                                            self.unpatch_seq)
        self.delete_download_seq = UnSequence("delete_download",
                                              self.phases.get("Downloaded"),
                                              self.phases.get("None"),
                                              self.phases.get("Downloaded"),
                                              ["delete_download"], False,
                                              self.delete_source_seq)
        self.install_seq = Sequence("install",
                                   self.phases.get("None"),
                                   self.phases.get("Activated"), [],
                                   False, self.activate_seq)

        self.uninstall_seq = UnSequence("uninstall",
                                        self.phases.get("Extracted"),
                                        self.phases.get("Downloaded"),
                                        self.phases.get("Extracted"),
                                        [""], False,
                                        self.delete_source_seq)

    def install_dependencies(self):
        dependencies = self.session_wrapper.depends()
        for dependency in dependencies.itervalues():
            current_phase = dependency.session.get_current_phase()
            if not current_phase == self.phases.get("Activated"):
                self.install_seq(dependency.session)

    def download(self, all=False, resume_on_error=True):
        if all:
            dependencies = self.session_wrapper.depends()
            for dependency in dependencies.itervalues():
                if not resume_on_error:
                    self.download_seq(dependency.session)
                else:
                    try:
                        self.download_seq(dependency.session)
                    except Error, e:
                        self.log.err("Error while downloading " + 
                                     "session '%s': %s" %\
                                     (dependency.name, e))
        self.download_seq(self.session_wrapper, self.force)

    def extract(self):
        self.extract_seq(self.session_wrapper, self.force)

    def archive(self):
        self.log.info("%s:phase:archive" % self.session_name)

    def configure(self):
        self.install_dependencies()
        self.configure_seq(self.session_wrapper, self.force)

    def build(self):
        self.install_dependencies()
        self.build_seq(self.session_wrapper, self.force)

    def destroot(self):
        self.install_dependencies()
        self.destroot_seq(self.session_wrapper, self.force)

    def install(self):
        self.install_dependencies()
        self.log.info("%s:running install" % self.session_name)
        self.activate_seq(self.session_wrapper, self.force)

    def uninstall(self):
        self.log.info("%s:running uninstall" % self.session_name)
        self.uninstall_seq(self.session_wrapper, self.force)

    def activate(self):
        self.install_dependencies()
        self.activate_seq(self.session_wrapper, self.force)

    def deactivate(self):
        self.deactivate_seq(self.session_wrapper, self.force)

    def patch(self):
        self.patch_seq(self.session_wrapper, self.force)

    def unpatch(self):
        self.unpatch_seq(self.session_wrapper, self.force)

    def clean(self):
        self.session_wrapper.clean()

    def distclean(self):
        self.log.normal(self.session_wrapper.distclean())

    def depends(self):
        return self.session_wrapper.depends()

    def drop(self):
        self.log.info("%s:phase:drop" % self.session_name)
        #TODO remove session destdir


