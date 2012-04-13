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

from jam.error import JamError
from jam.utils import extract_file

class FileExtractError(JamError):
    pass


class FileExtract(object):

    def __init__(self, url):
        self.url = url
        self.log = jam.logging.getLogger(self)

    def extract(self, src_dir, dest_dir):
        raise NotImplementedError()


class ArchiveFile(FileExtract):

    def extract(self, src_dir, dest_dir):
        filename = self._get_filename()
        archive_file = os.path.join(src_dir, filename)
        if os.path.isfile(archive_file):
            if not os.path.exists(dest_dir):
                self.log.debug("Creating destination dir '%s'" % dest_dir)
                os.makedirs(dest_dir)
            self.log.info("Extract '%s' to '%s'" % (archive_file, dest_dir))
            extract_file(archive_file, dest_dir)

        else:
            raise FileExtractError("Could not extract '%s' to '%s'. File does "
                                     "not exist." % (archive_file, dest_dir))

    def _get_filename(self):
        file = self.url
        if isinstance(file, list):
            return file[1]
        else:
            return os.path.basename(file)


class NoneFile(FileExtract):

    def extract(self, src_dir, dest_dir):
        pass
