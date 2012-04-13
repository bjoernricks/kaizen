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

from ConfigParser import RawConfigParser

from jam.session.handler import SessionHandler
from jam.session.error import SessionError

class UnresolvedDependencies(SessionError):

    def __init__(self, session_name, missing):
        self.missing = missing
        value = "Couldn't not resolve all dependencies\n"
        for dependency in self.missing.itervalues():
            if dependency.version:
                value += "'%s' version '%s' is missing\n" % (dependency.name,
                                                            dependency.version)
            else:
                value += "'%s' is missing\n" % dependency.name
        super(UnresolvedDependencies, self).__init__(session_name, value)


class DependencyAnalyser(object):

    dependency_field = "depends"

    def __init__(self, config, session):
        self.config = config
        self.session = session
        self.dependencies = dict()
        self.missing = dict()
        self.systemprovider = SystemProvider(config)
        self.log = jam.logging.getLogger(self)
        self.systemprovider.load()

    def analyse_session(self, session):
        dependencies = []
        depends = getattr(session.session, self.dependency_field)
        if not depends:
            return dependencies
        for depend in depends:
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
            elif self.systemprovider and self.systemprovider.provides(name):
                dependency = self.systemprovider.get(name)
                self.dependencies[name] = dependency
            else:
                try:
                    depend_session = SessionHandler(self.config, name)
                    dependency = SessionDependency(depend_session, name, version)
                    self.dependencies[name] = dependency
                    cur_deps = self.analyse_session(depend_session)
                    dependency.add_dependencies(cur_deps)
                except SessionError, e:
                    self.log.error("Error while loading dependency '%s': %s" % \
                                   (name, e))
                    dependency = Dependency(name)
                    self.missing[name] = dependency
                    self.dependencies[name] = dependency
            dependencies.append(dependency)
        return dependencies

    def analyse(self):
        self.analyse_session(self.session)
        return self.dependencies

    def get_missing(self):
        return self.missing


class RuntimeDependencyAnalyser(DependencyAnalyser):

    dependency_field = "runtime_depends"


class Dependency(object):

    NONE, SESSION, SYSTEM = range(3)

    def __init__(self, name, version=None, type=NONE):
        self.type = type
        self.name = name
        self.version = version
        self.dependencies = []

    def get_type(self):
        return self.type

    def add_dependency(self, dependency):
        self.dependencies.append(dependency)

    def add_dependencies(self, dependencies):
        self.dependencies.extend(dependencies)


class SessionDependency(Dependency):

    def __init__(self, session, name, version=None):
        self.session = session
        super(SessionDependency, self).__init__(name, version,
                                                Dependency.SESSION)


class SystemDependency(Dependency):

    def __init__(self, name, version=None):
        super(SystemDependency, self).__init__(name, version,
                                               Dependency.SYSTEM)


class SystemProvider(object):

    def __init__(self, config):
        self.config = config
        self.log = jam.logging.getLogger(self)
        self.configparser = RawConfigParser()

    def load(self, filename=None):
        self.configparser = RawConfigParser()
        if not filename:
            filename = self.config.get("system")
        if not filename or not os.path.isfile(filename):
            self.log.debug("no config file found for system povided "\
                           "dependencies. Config file %r will be created" % \
                           filename)
        else:
            self.configparser.read(filename)
        if not self.configparser.has_section("provides"):
            self.log.debug("system config file '%s' has to provides section. "\
                           "Section will be created." % filename)
            self.configparser.add_section("provides")

    def provides(self, name):
        return self.configparser and self.configparser.has_option("provides",
                                                                  name)

    def get(self, name):
        if not self.provides(name):
            return None
        version = self.configparser.get("provides", name)
        return SystemDependency(name, version)

    def add(self, name, version):
        if not self.configparser:
            return
        if version is None:
            version = ''
        self.configparser.set("provides", name, version)

    def remove(self, name):
        if not self.configparser:
            return False
        return self.configparser.remove_option("provides", name)

    def save(self, filename=None):
        if not filename:
            filename = self.config.get("system")
        f = open(filename, "w")
        self.configparser.write(f)
        f.close()

    def list(self):
        if not self.configparser:
            return []
        return self.configparser.items("provides")
