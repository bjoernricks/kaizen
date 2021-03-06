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

class Info(object):

    def __init__(self, description, license, maintainer, category, homepage,
                 scm, scm_web):
        self.description = description
        self.license = license
        self.maintainer = maintainer
        self.category = category
        self.homepage = homepage
        self.scm = scm
        self.scm_web = scm_web


class Installed(object):

    def __init__(self, rules, version):
        self.rules = rules
        self.version = version


class File(object):

    def __init__(self, filename, rules):
        self.filename = filename
        self.rules = rules


class Directory(object):

    def __init__(self, directory, rules):
        self.directory = directory
        self.rules = rules


class RulesPhase(object):

    def __init__(self, rules, version, phase):
        self.rules = rules
        self.version = version
        self.phase = phase

    def __repr__(self):
        return "<RulesPhase id='0x%x' rules='%s' version='%s' phase='%s'>" % (
               id(self), self.rules, self.version, self.phase.name)


class SchemaVersion(object):

    def __init__(self, version):
        self.version = version

    def __repr__(self):
        return "<SchmemaVersion id='0x%x' version=%r>" % (id(self),
                self.version)


class UpdateVersion(object):

    def __init__(self, update, version, datetime):
        self.update = update
        self.version = version
        self.datetime = datetime

    def __repr__(self):
        return "<UpdateVersion id='0x%x' update=%r version=%r datetime=%r>" % (
                id(self), self.update, self.version, self.datetime)


class InstallDirectories(object):

    def __init__(self, rules, version, download=None, source=None, build=None,
                 destroot=None):
        self.rules = rules
        self.version = version
        self.download = download
        self.source = source
        self.build = build
        self.destroot = destroot

    def __repr__(self):
        return "<InstallDirectories id='0x%x' rules=%r version=%r " \
               "download=%r source=%r build=%r destroot=%r>" % (id(self),
                       self.rules, self.version, self.download, self.source,
                       self.build, self.destroot)
