# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# kaizen - Continously improve, build and manage free software
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

import imp
import inspect
import os.path
import sys

import kaizen.logging


class Loader(object):

    def __init__(self):
        self.log = kaizen.logging.getLogger(self)
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

