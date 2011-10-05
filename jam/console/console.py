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

from jam.session.manager import SessionManager, SessionsList


class Console(object):

    def __init__(self, config):
        self.config = config

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

    def list_session_dependencies(self, sessionname):
        manager = SessionManager(self.config, sessionname)
        dependency_names = manager.depends().keys()
        if not dependency_names:
            return
        print "Session %s depends on:" % sessionname
        for dependency_name in dependency_names:
            print "--> %s" % dependency_name

    def list_installed_sessions(self):
        slist = SessionsList(self.config)
        installed = slist.get_installed_sessions()
        for session in installed:
            print "%s\t%s" % (session.session, session.version)

    def list_activated_sessions(self):
        slist = SessionsList(self.config)
        installed = slist.get_activated_sessions()
        for session in installed:
            print "%s\t%s" % (session.session, session.version)

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

