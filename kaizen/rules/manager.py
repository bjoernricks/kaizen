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

import os.path

import kaizen.logging

from kaizen.rules.error import RulesError
from kaizen.rules.handler import RulesHandler
from kaizen.rules.depend import DependencyAnalyser, Dependency, \
                               UnresolvedDependencies, DependencyEvaluator, \
                               RuntimeDependencyAnalyser
from kaizen.phase.phase import phases_list
from kaizen.db.db import Db
from kaizen.db.objects import Installed, RulesPhase
from kaizen.utils.signals import ForwardSignal


class RulesManager(object):

    url = []
    patches = []

    def __init__(self, config, name, version=None, force=False):
        self.config = config
        self.force = force
        self.rules_name = name
        self.log = kaizen.logging.getLogger(self)
        self.handler = RulesHandler(config, name, version, force)
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
        self.deactivate_seq = self.handler.deactivate_seq
        self.delete_destroot_seq = self.handler.delete_destroot_seq
        self.delete_build_seq = self.handler.delete_build_seq
        self.distclean_seq = self.handler.distclean_seq
        self.unpatch_seq = self.handler.unpatch_seq
        self.delete_source_seq = self.handler.delete_source_seq
        self.delete_download_seq = self.handler.delete_download_seq

        self.install_seq = self.activate_seq
        self.uninstall_seq = self.delete_source_seq

        # self.install_seq = Sequence("install",
        #                            phases_list.get("None"),
        #                            phases_list.get("Activated"), [],
        #                            False, self.activate_seq)

        # self.uninstall_seq = UnSequence("uninstall",
        #                                 phases_list.get("Extracted"),
        #                                 phases_list.get("Downloaded"),
        #                                 phases_list.get("Extracted"),
        #                                 [""], False,
        #                                 self.delete_source_seq)

    def _init_signals(self):
        self.already_activated = \
            ForwardSignal(self.handler.already_activated)

    def _install_dependencies(self, depanalyzer):
        dependencies = depanalyzer.analyse()
        missing = depanalyzer.get_missing()
        if missing:
            raise UnresolvedDependencies(self.rules_name, missing)
        for dependency in DependencyEvaluator(dependencies).list():
            if not dependency.get_type() == Dependency.SESSION:
                continue
            if not phases_list.get("Activated") in \
                dependency.rules.get_phases():
                self.install_seq(dependency.rules)

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
                    self.download_seq(dependency.rules)
                else:
                    try:
                        self.download_seq(dependency.rules)
                    except Error, e:
                        self.log.err("Error while downloading " + 
                                     "rules '%s': %s" %\
                                     (dependency.name, e))
        self.download_seq(self.handler, self.force)

    def extract(self):
        self.extract_seq(self.handler, self.force)

    def archive(self):
        self.log.info("%s:phase:archive" % self.rules_name)

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
        self.log.info("%s:running install" % self.rules_name)
        self.install_seq(self.handler, self.force)
        self.common_activate()

    def uninstall(self):
        self.log.info("%s:running uninstall" % self.rules_name)
        self.uninstall_seq(self.handler, self.force)
        self.common_deactivate()

    def common_deactivate(self):
        installed = self.db.session.query(Installed).get(self.rules_name)
        if installed:
            self.db.session.delete(installed)
            self.db.session.commit()

    def common_activate(self):
        installed = self.db.session.query(Installed).get(self.rules_name)
        if not installed:
            installed = Installed(self.rules_name,
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

    def get_rules_phases(self):
        return self.handler.get_phases()


class RulesList(object):

    def __init__(self, config):
        self.db = Db(config)

    def get_installed_rules(self):
        return self.db.session.query(Installed).order_by(Installed.rules).all()

    def get_activated_rules(self):
        return self.db.session.query(RulesPhase).filter(
                                     RulesPhase.phase ==
                                     phases_list.get("Activated")).order_by(
                                             RulesPhase.rules).all()
    def get_destrooted_rules(self):
        return self.db.session.query(RulesPhase).filter(
                                     RulesPhase.phase ==
                                     phases_list.get("Destrooted")).order_by(
                                             RulesPhase.rules).all()

    def get_downloaded_rules(self):
        return self.db.session.query(RulesPhase).filter(
                                     RulesPhase.phase ==
                                     phases_list.get("Downloaded")).order_by(
                                             RulesPhase.rules).all()
