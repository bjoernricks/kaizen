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

import os

from jam.session.manager import SessionManager, SessionsList
from jam.session.depend import Dependency, SystemProvider
from jam.system.patch import Quilt


class Console(object):

    def __init__(self, config):
        self.config = config
        self.quiet = self.config.get("quiet")

    def list_session_files(self, sessionname):
        manager = SessionManager(self.config, sessionname)
        files = manager.get_installed_files()
        if files:
            print "\n".join([file.filename for file in files])
        else:
            print "'%s' has no files installed" % sessionname

    def list_session_phases(self, sessionname):
        manager = SessionManager(self.config, sessionname)
        phases = manager.get_session_phases()
        if phases:
            print ", ".join([phase.name for phase in phases])
        else:
            print "'%s' has no phase" % sessionname

    def _print_dependencies(self, dependencies, max_length):
        for name, dependency in dependencies.items():
            if dependency.get_type() == Dependency.NONE:
                provided_by = "not available"
            elif dependency.get_type() == Dependency.SESSION:
                provided_by = "provided by session"
            elif dependency.get_type() == Dependency.SYSTEM:
                provided_by = "provided by system"
            else:
                provided_by = "unknown"
            print "--> %s%s(%s)" % (name, self._get_filler(name, max_length),
                                    provided_by)

    def list_session_dependencies(self, sessionname):
        manager = SessionManager(self.config, sessionname)
        (build, runtime) = manager.depends()
        if not build and not runtime:
            print "%s has no dependencies" % sessionname
            return
        print "Session %s depends on:" % sessionname
        max_length = max([len(name) for name in build.keys()] + \
            [len(name) for name in runtime.keys()])
        if runtime:
            print "\nRuntime dependencies:"
            self._print_dependencies(runtime, max_length)
        if build:
            print "\nBuild dependencies:"
            self._print_dependencies(build, max_length)

    def list_installed_sessions(self):
        slist = SessionsList(self.config)
        installed = slist.get_installed_sessions()
        max_length = max([len(s.session) for s in installed])
        for s in installed:
            print "%s%s%s" % (s.session, self._get_filler(s.session,
                              max_length), s.version)

    def list_activated_sessions(self):
        slist = SessionsList(self.config)
        installed = slist.get_activated_sessions()
        max_length = max([len(s.session) for s in installed])
        for s in installed:
            print "%s%s%s" % (s.session, self._get_filler(s.session,
                              max_length), s.version)

    def build_session(self, sessionname, force=False):
        manager = SessionManager(self.config, sessionname, force)
        manager.build()

    def patch_session(self, sessionname, force=False):
        manager = SessionManager(self.config, sessionname, force)
        manager.patch()

    def unpatch_session(self, sessionname, force=False):
        manager = SessionManager(self.config, sessionname, force)
        manager.unpatch()

    def configure_session(self, sessionname, force=False):
        manager = SessionManager(self.config, sessionname, force)
        manager.configure()

    def extract_session(self, sessionname, force=False):
        manager = SessionManager(self.config, sessionname, force)
        manager.extract()

    def download_session(self, sessionname, download_all, force=False):
        manager = SessionManager(self.config, sessionname, force)
        manager.download(download_all)

    def destroot_session(self, sessionname, force=False):
        manager = SessionManager(self.config, sessionname, force)
        manager.destroot()

    def install_session(self, sessionname, force=False):
        manager = SessionManager(self.config, sessionname, force)
        manager.install()

    def uninstall_session(self, sessionname, force=False):
        manager = SessionManager(self.config, sessionname, force)
        manager.uninstall()

    def activate_session(self, sessionname, force=False):
        manager = SessionManager(self.config, sessionname, force)
        manager.activate()

    def deactivate_session(self, sessionname, force=False):
        manager = SessionManager(self.config, sessionname, force)
        manager.deactivate()

    def distclean_session(self, sessionname, force=False):
        manager = SessionManager(self.config, sessionname, force)
        manager.distclean()

    def clean_session(self, sessionname, force=False):
        manager = SessionManager(self.config, sessionname, force)
        manager.clean()

    def delete_source_session(self, sessionname, force=False):
        manager = SessionManager(self.config, sessionname, force)
        manager.delete_source()

    def delete_destroot_session(self, sessionname, force=False):
        manager = SessionManager(self.config, sessionname, force)
        manager.delete_destroot()

    def delete_download_session(self, sessionname, force=False):
        manager = SessionManager(self.config, sessionname, force)
        manager.delete_download()

    def delete_build_session(self, sessionname, force=False):
        manager = SessionManager(self.config, sessionname, force)
        manager.delete_build()

    def add_system_provides(self, name, version):
        provider = SystemProvider(self.config)
        provider.load()
        provider.add(name, version)
        provider.save()
        if not self.quiet:
            print "added software '%s' provided by the system successfully" % \
                    name

    def remove_system_provides(self, name):
        provider = SystemProvider(self.config)
        provider.load()
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
        max_length = max([len(session) for session, version in provider.list()])
        for session, version in sorted(provider.list()):
            print "%s%s%s" % (session, self._get_filler(session,
                              max_length), version)

    def quilt_pop(self, sessionname, all=False):
        quilt = self._quilt(sessionname)
        if all:
            quilt.unapply()
        else:
            quilt.pop()

    def quilt_push(self, sessionname, all=False):
        quilt = self._quilt(sessionname)
        if all:
            quilt.apply()
        else:
            quilt.push()

    def quilt_refresh(self, sessionname):
        quilt = self._quilt(sessionname)
        quilt.refresh()

    def quilt_delete(self, sessionname):
        quilt = self._quilt(sessionname)
        quilt.delete()

    def quilt_new(self, sessionname, patchname):
        quilt = self._quilt(sessionname)
        quilt.new(patchname)

    def quilt_import(self, sessionname, patches):
        quilt = self._quilt(sessionname, os.getcwd())
        quilt.import_patches(patches)

    def quilt_edit(self, sessionname, filenames):
        quilt = self._quilt(sessionname)
        quilt.edit(filenames)

    def _quilt(self, sessionname, src_path=None):
        manager = SessionManager(self.config, sessionname)
        # session must be at least in phase extract
        manager.extract()
        session = manager.session_wrapper.session
        if not src_path:
            src_path = session.src_path
        return Quilt(src_path, session.patch_path, session.patches,
                     self.config.get("verbose"))

    def _get_filler(self, text, max_length):
        return " " * (max_length - len(text) + 1)
