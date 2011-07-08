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

import jam.session

class DependencyAnalyser(object):

    def __init__(self, config, session):
        self.config = config
        self.session = session
        self.session_loader = jam.session.SessionLoader(config)
        self.dependencies = dict()
        self.log = jam.log.getLogger("jam.dependencies")

    def analyse_session(self, session):
        dependencies = []
        for depend in session.depends:
            name = depend
            version = None
            if isinstance(depend, tuple):
                name = depend[0]
                version = depend[1]
            if not name:
                self.log.warn("Session '%s' has an empty dependency" %
                              session.name)
                continue
            if name in self.dependencies:
                dependency = self.dependencies[name] 
            else:
                depend_session = self.session_loader.load(name)
                if not depend_session:
                    self.log.error("Could not load dependency '%s'" % name)
                    continue
                dependency = Dependency(session, name, version)
                self.dependencies[name] = dependency
                cur_deps = self.analyse_session(depend_session)
                dependency.add_dependencies(cur_deps)
            dependencies.append(dependency)
        return dependencies

    def analyse(self):
        self.analyse_session(self.session)
        return self.dependencies


class Dependency(object):

    def __init__(self, session, name, version=None):
        self.session = session
        self.name = name
        self.version = version
        self.dependencies = []

    def add_dependency(self, dependency):
        self.dependencies.append(dependency)

    def add_dependencies(self, dependencies):
        self.dependencies.extend(dependencies)
