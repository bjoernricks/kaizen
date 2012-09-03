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

import os

from kaizen.rules.manager import RulesManager, RulesList
from kaizen.rules.depend import Dependency, SystemProvider, DependencyEvaluator
from kaizen.system.patch import Quilt
from kaizen.db.update.upgrade import Upgrade
from kaizen.logging.out import out


class Console(object):

    def __init__(self, config):
        self.config = config
        self.quiet = self.config.get("quiet")

    def list_rules_files(self, rulesname):
        manager = RulesManager(self.config, rulesname)
        files = manager.get_installed_files()
        if files:
            print "\n".join([file.filename for file in files])
        else:
            print "'%s' has no files installed" % rulesname

    def list_rules_phases(self, rulesname):
        manager = RulesManager(self.config, rulesname)
        phases = manager.get_rules_phases()
        if phases:
            print ", ".join([phase.name for phase in phases])
        else:
            print "'%s' has no phase" % rulesname

    def _print_dependencies(self, dependencies, max_length):
        for dependency in dependencies:
            if dependency.get_type() == Dependency.NONE:
                provided_by = "not available"
            elif dependency.get_type() == Dependency.SESSION:
                provided_by = "provided by rules"
            elif dependency.get_type() == Dependency.SYSTEM:
                provided_by = "provided by system"
            else:
                provided_by = "unknown"
            name = dependency.get_name()
            print "--> %s%s(%s)" % (name, self._get_filler(name, max_length),
                                    provided_by)

    def list_rules_dependencies(self, rulesname):
        manager = RulesManager(self.config, rulesname)
        (build, runtime) = manager.depends()
        if not build and not runtime:
            print "%s has no dependencies" % rulesname
            return
        build_deps = DependencyEvaluator(build).list()
        runtime_deps = DependencyEvaluator(runtime).list()
        print "Rules %s depends on:" % rulesname
        max_length = max([len(dep.get_name()) for dep in build_deps + \
                              runtime_deps])
        if runtime:
            print "\nRuntime dependencies:"
            self._print_dependencies(runtime_deps, max_length)
        if build:
            print "\nBuild dependencies:"
            self._print_dependencies(build_deps, max_length)

    def list_installed_rules(self):
        slist = RulesList(self.config)
        installed = slist.get_installed_rules()
        max_length = max([len(s.rules) for s in installed])
        for s in installed:
            print "%s%s%s" % (s.rules, self._get_filler(s.rules,
                              max_length), s.version)

    def list_activated_rules(self):
        slist = RulesList(self.config)
        installed = slist.get_activated_rules()
        max_length = max([len(s.rules) for s in installed])
        for s in installed:
            print "%s%s%s" % (s.rules, self._get_filler(s.rules,
                              max_length), s.version)

    def build_rules(self, rulesname, force=False):
        manager = RulesManager(self.config, rulesname, force)
        manager.build()

    def patch_rules(self, rulesname, force=False):
        manager = RulesManager(self.config, rulesname, force)
        manager.patch()

    def unpatch_rules(self, rulesname, force=False):
        manager = RulesManager(self.config, rulesname, force)
        manager.unpatch()

    def configure_rules(self, rulesname, force=False):
        manager = RulesManager(self.config, rulesname, force)
        manager.configure()

    def extract_rules(self, rulesname, force=False):
        manager = RulesManager(self.config, rulesname, force)
        manager.extract()

    def download_rules(self, rulesname, download_all, force=False):
        manager = RulesManager(self.config, rulesname, force)
        manager.download(download_all)

    def destroot_rules(self, rulesname, force=False):
        manager = RulesManager(self.config, rulesname, force)
        manager.destroot()

    def install_rules(self, rulesname, force=False):
        manager = RulesManager(self.config, rulesname, force)
        manager.already_activated.connect(self.on_rules_already_activated)
        manager.install()

    def uninstall_rules(self, rulesname, version=None, force=False):
        manager = RulesManager(self.config, rulesname, version, force)
        manager.uninstall()

    def activate_rules(self, rulesname, force=False):
        manager = RulesManager(self.config, rulesname, force)
        manager.already_activated.connect(self.on_rules_already_activated)
        manager.activate()

    def deactivate_rules(self, rulesname, force=False):
        manager = RulesManager(self.config, rulesname, force)
        manager.deactivate()

    def distclean_rules(self, rulesname, force=False):
        manager = RulesManager(self.config, rulesname, force)
        manager.distclean()

    def clean_rules(self, rulesname, force=False):
        manager = RulesManager(self.config, rulesname, force)
        manager.clean()

    def delete_source_rules(self, rulesname, force=False):
        manager = RulesManager(self.config, rulesname, force)
        manager.delete_source()

    def delete_destroot_rules(self, rulesname, force=False):
        manager = RulesManager(self.config, rulesname, force)
        manager.delete_destroot()

    def delete_download_rules(self, rulesname, force=False):
        manager = RulesManager(self.config, rulesname, force)
        manager.delete_download()

    def delete_build_rules(self, rulesname, force=False):
        manager = RulesManager(self.config, rulesname, force)
        manager.delete_build()

    def add_system_provides(self, names):
        provider = SystemProvider(self.config)
        provider.load()
        for name in names:
            provider.add(name[0], name[1])
        provider.save()
        if not self.quiet:
            print "Added software '%s' provided by the system successfully" % \
                   ", ".join([name[0] for name in names])

    def remove_system_provides(self, names):
        provider = SystemProvider(self.config)
        provider.load()
        for name in names:
            success = provider.remove(name)
            provider.save()
            if not self.quiet:
                if success:
                    print "removed '%s' sucessfully" % name
                else:
                    print "'%s' couldn't be removed" % name

    def list_system_provides(self):
        provider = SystemProvider(self.config)
        provider.load()
        if provider.is_empty():
            print "System provides no dependencies"
            return
        max_length = max([len(rules) for rules, version in provider.list()])
        for rules, version in sorted(provider.list()):
            print "%s%s%s" % (rules, self._get_filler(rules,
                              max_length), version)

    def quilt_pop(self, rulesname, all=False):
        quilt = self._quilt(rulesname)
        if all:
            quilt.unapply()
        else:
            quilt.pop()

    def quilt_push(self, rulesname, all=False):
        quilt = self._quilt(rulesname)
        if all:
            quilt.apply()
        else:
            quilt.push()

    def quilt_refresh(self, rulesname):
        quilt = self._quilt(rulesname)
        quilt.refresh()

    def quilt_delete(self, rulesname):
        quilt = self._quilt(rulesname)
        quilt.delete()

    def quilt_new(self, rulesname, patchname):
        quilt = self._quilt(rulesname)
        quilt.new(patchname)

    def quilt_import(self, rulesname, patches):
        quilt = self._quilt(rulesname, os.getcwd())
        quilt.import_patches(patches)

    def quilt_edit(self, rulesname, filenames):
        quilt = self._quilt(rulesname)
        quilt.edit(filenames)

    def _quilt(self, rulesname, src_path=None):
        manager = RulesManager(self.config, rulesname)
        # rules must be at least in phase extract
        manager.extract()
        rules = manager.rules_wrapper.rules
        if not src_path:
            src_path = rules.src_path
        return Quilt(src_path, rules.patch_path, rules.patches,
                     self.config.get("verbose"))

    def _get_filler(self, text, max_length):
        return " " * (max_length - len(text) + 1)

    def upgrade(self):
        upgrade = Upgrade(self.config)
        upgrade.run()

    def on_rules_already_activated(self):
        out("Rules is already activated.")
