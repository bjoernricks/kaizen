# vim:fileencoding=utf-8:et::sw=4:ts=4:tw=80:

# jam - An advanced package manager for Free Software
#
# Copyright (C) 2011  Björn Ricks <bjoern.ricks@googlemail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import os
import os.path
import hashlib # requires python 2.5

import jam.log

log = jam.log.getLogger(__name__)

class Hash(object):

    def __init__(self, filename):
        self.filename = filename
        self.md5_value = None
        self.sha1_value = None

    def md5(self):
        if not self.md5_value:
            self.md5_value = self._calculate_hash(hashlib.md5)
        return self.md5_value

    def sha1(self):
        if not self.sha1_value:
            self.sha1_value = self._calculate_hash(hashlibs.sha1)
        return self.sha1_value

    def _calculate_hash(self, hashalgorithm):
        """ calculates a hash of a file """
        if not os.path.isfile(self.filename):
            raise RuntimeError("Could not calculate hash. File not found: %s"
                                % self.filename)
        f = file(self.filename, 'rb')
        m = hashalgorithm()
        while True:
            d = f.read(8096)
            if not d:
               break
            m.update(d)
        f.close()
        return m.hexdigest()


def list_dir(dir, all_dirs=False):
    files = []
    dirs = []
    contents = os.listdir(dir)
    for content in contents:
        path = os.path.join(dir, content)
        if os.path.isdir(path):
            (newdirs, newfiles) = list_dir(path, all_dirs)
            if not newdirs or all_dirs:
                dirs.append(path)
            files.extend(newfiles)
            dirs.extend(newdirs)
        else:
            files.append(path)
    return (dirs, files)

def list_subdir(dir, all_dirs=False):
    files = []
    dirs = []
    cwd = os.getcwd()
    os.chdir(dir)
    contents = os.listdir(dir)
    for content in contents:
        if os.path.isdir(content):
            (newdirs, newfiles) = list_dir(content, all_dirs)
            if not newdirs or all_dirs:
                dirs.append(content)
            files.extend(newfiles)
            dirs.extend(newdirs)
        else:
            files.append(content)
    os.chdir(cwd)
    return (dirs, files)

def realpath(path):
    return os.path.abspath(os.path.expanduser(path))

def extract_file(self, file_name, dest_dir):
    if not os.path.isfile(file_name):
        raise RuntimeError("Unable to extract file. '%s' is does not exit or \
                           is not a file." % file_name)
    if tarfile.is_tarfile(file_name):
        log.debug("Extracting tar file '%s' to '%s'" %
                      (file_name, dest_dir))
        file = tarfile.open(file_name)
        file.extractall(dest_dir)
    elif zipfile.is_zipfile(file_name):
        log.debug("Extracting zip file '%s' to '%s'" %
                      (file_name, dest_dir))
        file = zipfile.ZipFile(file_name)
        file.extractall(dest_fir)

