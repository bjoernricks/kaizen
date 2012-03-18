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

    def __init__(self, session, version):
        self.session = session
        self.version = version


class File(object):

    def __init__(self, filename, session):
        self.filename = filename
        self.session = session


class Directory(object):

    def __init__(self, directory, session):
        self.directory = directory
        self.session = session


class SessionPhase(object):

    def __init__(self, session, version, phase):
        self.session = session
        self.version = version
        self.phase = phase

    def __repr__(self):
        return "<SessionPhase id='0x%x' session='%s' version='%s' phase='%s'>" % (
               id(self), self.session, self.version, self.phase.name)


class SchemaVersion(object):

    def __init__(self, version):
        self.version

    def __repr__(self):
        return "<SchmemaVersion id='0x%x' version=%r>" % (id(self),
                self.version)


class UpdateVersion(object):

    def __init__(self, update, datetime):
        self.update = update
        self.datetime = datetime

    def __repr__(self):
        return "<UpdateVersion id='0x%x' update=%r datetime=%r>" % (id(self),
                self.update, self.datetime)


class InstallDirectories(object):

    def __init__(self, session, version, download=None, source=None, build=None,
                 destroot=None):
        self.session = session
        self.version = version
        self.download = download
        self.source = source
        self.build = build
        self.destroot = destroot
