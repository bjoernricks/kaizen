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
import os.path
import inspect
import imp
import string
import sys
import tarfile
import zipfile
import bz2file

import jam.logging

from jam.error import JamRuntimeError
try:
    from hashlib import md5 # requires python 2.5
    from hashlib import sha1 # requires python 2.5
except ImportError:
    from md5 import new as md5
    from sha import new as sha1

log = jam.logging.getLogger(__name__)

class Hash(object):

    def __init__(self, filename):
        self.filename = filename
        self.md5_value = None
        self.sha1_value = None

    def md5(self):
        if not self.md5_value:
            self.md5_value = self._calculate_hash(md5)
        return self.md5_value

    def sha1(self):
        if not self.sha1_value:
            self.sha1_value = self._calculate_hash(sha1)
        return self.sha1_value

    def _calculate_hash(self, hashalgorithm):
        """ calculates a hash of a file """
        if not os.path.isfile(self.filename):
            raise JamRuntimeError("Could not calculate hash. File not found: %s"
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


class Loader(object):

    def __init__(self):
        self.log = jam.logging.getLogger("jam.loader")
        self.paths = []

    def add_path(self, path):
        self.paths.append(path)

    def add_paths(self, paths):
        self.paths.extend(paths)

    def find_module(self, module, paths, as_module=None):
        if not as_module:
            as_module = module
        file, pathname, description = imp.find_module(module, paths)
        try:
            return imp.load_module(as_module, file, pathname, description)
        finally:
            if file:
                file.close()

    def module(self, name, as_module=None):
        if not as_module:
            as_module = module
        if "." in name:
            paths = []
            index = name.rfind(".")
            package = name[:index]
            module_name = name[index+1:]
            module_path = package.replace(".", os.path.sep)
            for path in self.paths:
                paths.append(os.path.join(path, module_path))
        else:
            module_name = name
            paths = self.paths
        if not paths:
            paths = self.paths
        try:
            if as_module in sys.modules:
                self.log.warn("Reloading '%s' module. This overwrites the " \
                        "previous loaded module with the same name." % \
                        as_module)
                del sys.modules[as_module]
            module = self.find_module(module_name, paths, as_module)
            self.log.debug("Imported module '%s'" % module)
            return module
        except ImportError, error:
            self.log.warn("Could not import module '%s'. %s" % (name, error))
            return None


    def classes(self, module, parentclass=None, all=False):
        classes = []
        for key, value in module.__dict__.items():
            if inspect.isclass(value):
                if parentclass:
                    if not issubclass(value, parentclass):
                        continue
                # only load classes from module
                if not all and value.__module__ != module.__name__:
                    self.log.debug("Skipping class '%s'" % value)
                    continue
                self.log.debug("Found class '%s'" % value)
                classes.append(value)
        return classes

    def load(self, modulename, classname):
        classes = self.classes(modulename)
        if not classes:
            self.log.warn("Could not load any class with name '%s'" %
                          classname)
            return None
        for loadedclass in classes:
            if loadedclass.__name__ == classname:
                self.log.info("Loaded class '%s'" % classname)
                return loadedclass
        self.log.warn("Could not load any class with name '%s'" %
                      classname)
        return None


class Template(object):

    def __init__(self, filename):
        path = real_path(os.path.join(os.path.dirname(__file__),
                         os.path.pardir, "templates"))
        f = open(os.path.join(path, filename), "r")
        try:
            text = f.read()
        finally:
            f.close()
        self.template = string.Template(text)

    def replace(self, vars):
        return self.template.safe_substitute(vars)


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

