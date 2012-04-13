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
import tarfile
import zipfile

import jam.logging

from jam.error import JamRuntimeError

log = jam.logging.getLogger(__name__)


def list_contents(dir):
    files = []
    dirs = []
    cwd = os.getcwd()
    os.chdir(dir)
    contents = os.listdir(dir)
    for content in contents:
        if os.path.isdir(content):
            dirs.append(content)
        else:
            files.append(content)
    os.chdir(cwd)
    return (dirs, files)

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

def real_path(path):
    return os.path.abspath(os.path.expanduser(path))

def extract_file(file_name, dest_dir):
    if not os.path.isfile(file_name):
        raise JamRuntimeError("Unable to extract file. '%s' is does not exit or \
                           is not a file." % file_name)
    if file_name.endswith(".bz2") or file_name.endswith(".tbz2"):
        # bz2 doesn't support multiple streams therefore use bz2file module
        import bz2file
        bz_file = bz2file.BZ2File(file_name)
        log.debug("Extracting tar.bz2 file '%s' to '%s'" %
                      (file_name, dest_dir))
        file = tarfile.TarFile(file_name, "r", bz_file)
    elif tarfile.is_tarfile(file_name):
        log.debug("Extracting tar file '%s' to '%s'" %
                      (file_name, dest_dir))
        file = tarfile.open(file_name)
    elif zipfile.is_zipfile(file_name):
        log.debug("Extracting zip file '%s' to '%s'" %
                      (file_name, dest_dir))
        file = zipfile.ZipFile(file_name)
    else:
        raise JamRuntimeError("Unable to extract file. '%s' can not be recognized " \
                           "as a valid source archive." % file_name)
    file.extractall(dest_dir)

def get_number_of_cpus():
    try:
        import multiprocessing
        return multiprocessing.cpu_count()
    except (ImportError, NotImplementedError):
        pass
    try:
        res = int(os.sysconf('SC_NPROCESSORS_ONLN'))
        if res > 0:
            return res
    except (AttributeError,ValueError):
        pass
