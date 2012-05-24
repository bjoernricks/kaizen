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

import jam.logging

from jam.session.error import SessionError
from jam.session.handler import SessionHandler
from jam.session.depend import DependencyAnalyser, Dependency, \
                               UnresolvedDependencies, RuntimeDependencyAnalyser
from jam.phase.phase import phases_list
from jam.phase.sequence import Sequence, UnSequence
from jam.db.db import Db
from jam.db.objects import Installed, SessionPhase
from jam.utils.signals import ForwardSignal


class SessionManager(object):

    url = []
    patches = []

    def __init__(self, config, name, version=None, force=False):
        self.config = config
        self.force = force
        self.session_name = name
        self.log = jam.logging.getLogger(self)
        self.handler = SessionHandler(config, name, version, force)
        self.db = Db(config)
        self._init_signals()
        self.init_sequences()

    def init_sequences(self):
        self.downlood_seq = self.handler.download_seq
        self.extract_seq = self.handler.extract_seq
        self.patch_seq = self.handler.patch_seq
        self.configure_seq = self.handler.configure_seq
        self.build_seq = self.handler.build_seq
        self.destroot_seq = self.handler.destroot_seq
        self.activate_seq = self.handler.activate_seq

        self.deactivate_seq = UnSequence("deactivate",
                                         phases_list.get("Activated"),
                                         phases_list.get("Destrooted"),
                                         phases_list.get("Activated"),
                                         ["deactivate"])
        self.delete_destroot_seq = UnSequence("delete_destroot",
                                              phases_list.get("Destrooted"),
                                              phases_list.get("Built"),
                                              phases_list.get("Destrooted"),
                                              ["delete_destroot"], False,
                                              self.deactivate_seq)
        self.distclean_seq = UnSequence("distclean",
                                        phases_list.get("Configured"),
                                        phases_list.get("Built"),
                                        phases_list.get("Configured"),
                                        ["distclean"], False,
                                        self.delete_destroot_seq)
        self.delete_build_seq = UnSequence("delete_build",
                                           phases_list.get("Built"),
                                           phases_list.get("Patched"),
                                           phases_list.get("Built"),
                                           ["delete_build"], False,
                                           self.distclean_seq)
        self.unpatch_seq = UnSequence("unpatch",
                                      phases_list.get("Patched"),
                                      phases_list.get("Extracted"),
                                      phases_list.get("Patched"),
                                      ["unpatch"], False,
                                      self.delete_build_seq)
        # unpatch_db_seq: just remove phase from db
        self.unpatch_db_seq = UnSequence("unpatch",
                                         phases_list.get("Patched"),
                                         phases_list.get("Extracted"),
                                         phases_list.get("Patched"),
                                         [], False,
                                         self.delete_build_seq)
        self.delete_source_seq = UnSequence("delete_source",
                                            phases_list.get("Extracted"),
                                            phases_list.get("Downloaded"),
                                            phases_list.get("Extracted"),
                                            ["delete_source"], False,
                                            self.unpatch_db_seq)
        self.delete_download_seq = UnSequence("delete_download",
                                              phases_list.get("Downloaded"),
                                              phases_list.get("None"),
                                              phases_list.get("Downloaded"),
                                              ["delete_download"], False,
                                              self.delete_source_seq)
        self.install_seq = Sequence("install",
                                   phases_list.get("None"),
                                   phases_list.get("Activated"), [],
                                   False, self.activate_seq)

        self.uninstall_seq = UnSequence("uninstall",
                                        phases_list.get("Extracted"),
                                        phases_list.get("Downloaded"),
                                        phases_list.get("Extracted"),
                                        [""], False,
                                        self.delete_source_seq)

    def _init_signals(self):
        self.already_activated = \
            ForwardSignal(self.handler.already_activated)

    def _install_dependencies(self, depanalyzer):
        dependencies = depanalyzer.analyse()
        missing = depanalyzer.get_missing()
        if missing:
            raise UnresolvedDependencies(self.session_name, missing)
        for dependency in dependencies.itervalues():
            if not dependency.get_type() == Dependency.SESSION:
                continue
            if not phases_list.get("Activated") in \
                dependency.session.get_phases():
                self.install_seq(dependency.session)

    def install_dependencies(self):
        depanalyzer = DependencyAnalyser(self.config, self.handler)
        self._install_dependencies(depanalyzer)

    def install_runtime_dependencies(self):
        depanalyzer = RuntimeDependencyAnalyser(self.config,
                                                self.handler)
        self._install_dependencies(depanalyzer)

    def download(self, all=False, resume_on_error=True):
        if all:
            dependencies = self.handler.build_depends()
            for dependency in dependencies.itervalues():
                if not dependency.get_type() == Dependency.SESSION:
                    continue
                if not resume_on_error:
                    self.download_seq(dependency.session)
                else:
                    try:
                        self.download_seq(dependency.session)
                    except Error, e:
                        self.log.err("Error while downloading " + 
                                     "session '%s': %s" %\
                                     (dependency.name, e))
        self.download_seq(self.handler, self.force)

    def extract(self):
        self.extract_seq(self.handler, self.force)

    def archive(self):
        self.log.info("%s:phase:archive" % self.session_name)

    def configure(self):
        self.install_dependencies()
        self.configure_seq(self.handler, self.force)

    def build(self):
        self.install_dependencies()
        self.build_seq(self.handler, self.force)

    def destroot(self):
        self.install_dependencies()
        self.destroot_seq(self.handler, self.force)

    def install(self):
        self.install_dependencies()
        self.log.info("%s:running install" % self.session_name)
        self.install_seq(self.handler, self.force)
        self.common_activate()

    def uninstall(self):
        self.log.info("%s:running uninstall" % self.session_name)
        self.uninstall_seq(self.handler, self.force)
        self.common_deactivate()

    def common_deactivate(self):
        installed = self.db.session.query(Installed).get(self.session_name)
        if installed:
            self.db.session.delete(installed)
            self.db.session.commit()

    def common_activate(self):
        installed = self.db.session.query(Installed).get(self.session_name)
        if not installed:
            installed = Installed(self.session_name,
                    self.handler.get_version())
        else:
            installed.version = self.handler.get_version()
        self.db.session.add(installed)
        self.db.session.commit()
        self.install_runtime_dependencies()

    def activate(self):
        self.install_dependencies()
        self.activate_seq(self.handler, self.force)
        self.common_activate()

    def deactivate(self):
        self.deactivate_seq(self.handler, self.force)
        self.common_deactivate()

    def patch(self):
        self.patch_seq(self.handler, self.force)

    def unpatch(self):
        self.unpatch_seq(self.handler, self.force)

    def clean(self):
        self.handler.clean()

    def distclean(self):
        self.distclean_seq(self.handler, self.force)

    def depends(self):
        return self.handler.depends()

    def delete_destroot(self):
        self.delete_destroot_seq(self.handler, self.force)

    def delete_build(self):
        self.delete_build_seq(self.handler, self.force)

    def delete_source(self):
        self.delete_source_seq(self.handler, self.force)

    def delete_download(self):
        self.delete_download_seq(self.handler, self.force)

    def get_installed_files(self):
        return self.handler.get_installed_files()

    def get_session_phases(self):
        return self.handler.get_phases()


class SessionsList(object):

    def __init__(self, config):
        self.db = Db(config)

    def get_installed_sessions(self):
        return self.db.session.query(Installed).order_by(Installed.session).all()

    def get_activated_sessions(self):
        return self.db.session.query(SessionPhase).filter(
                                     SessionPhase.phase ==
                                     phases_list.get("Activated")).order_by(
                                             SessionPhase.session).all()
    def get_destrooted_sessions(self):
        return self.db.session.query(SessionPhase).filter(
                                     SessionPhase.phase ==
                                     phases_list.get("Destrooted")).order_by(
                                             SessionPhase.session).all()

    def get_downloaded_sessions(self):
        return self.db.session.query(SessionPhase).filter(
                                     SessionPhase.phase ==
                                     phases_list.get("Downloaded")).order_by(
                                             SessionPhase.session).all()
