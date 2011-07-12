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


class Files(object):

    def __init__(self, filename, session):
        self.filename = filename
        self.session = session


class Status(object):

    def __init__(session, version, phase):
        self.session = session
        self.version = version
        self.phase = phase
