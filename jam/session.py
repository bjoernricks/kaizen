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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import sys
import inspect
import logging

class SessionConfig(object):

    def __init__(self):
        self.jam_prefix = "/opt/local"
        self.jam_download_cache = "/opt/local/jam/cache"
        self.jam_sessions = "/opt/local/jam/session"
        self.jam_destroot = "/opt/local/jam/destroot"


class SessionManager(object):

    url = []
    patches = []

    def __init__(self, name, config):
        self.config = config
        self.session_name = name
        self.log = logging.getLogger("jam.sessionmanager")

    def create_cache_dirs(self):
        name = self.session_name
        cache_dir = os.path.join(self.config.download_cache(), name)
        os.makedirs(cache_dir)
        self.log.debug("create cache dirs in %s", cache_dir)
        data_dir = os.path.join(cache_dir, "data")
        self.log.debug("create cache datadir in %s", data_dir)
        os.mkdir(self.datadir)
        patch_dir = os.path.join(cache_dir, "patches")
        self.log.debug("create cache patchdir in %s", patch_dir)
        os.mkdir(self.patch_dir)

        return (data_dir, patch_dir)

    def download(self):
        self.log.info("%s: download", self.sessionname)
        (data_dir, patch_dir) = self.create_cache_dirs()

        for url in self.url:
            dl = Downloader(url) 
            dl.copy(data_dir)
        for patch in self.patches:
            dl = Downloader(patch)
            dl.copy(patch_dir)

    def extract(self):
        pass

    def archive(self):
        pass

    def configure(self):
        pass

    def build(self):
        pass

    def destroot(self):
        pass

    def install(self):
        pass

    def uninstall(self):
        pass

    def activate(self):
        pass

    def deactivate(self):
        pass

    def patch(self):
        pass

    def unpatch(self):
        pass


class Session(object):
    
    depends = []
    url = []
    patches = []

    def configure(self):
        pass

    def build(self):
        pass

    def patch(self):
        pass

    def unpatch(self):
        pass


class SessionLoader(object):

    def __init__(self, config):
        self.config = config
        self.log = logging.getLogger("jam.sessionloader")
        self.add_path()

    def add_path(self):
        path = self.config.jam_sessions
        if not path in sys.path:
            sys.path.append(path)

    def module(self, name):
        try:
            return __import__(name, globals(), locals(), ['*'])
        except ImportError:
            self.log.warn("Could not import module '%s'", name)
            return None
    

    def classes(self, modulename, parentclass=None):
        classes = []
        module = self.module(modulename)
        if not module:
            return classes
        self.log.debug("Imported module '%s'", module)
        for key, value in module.__dict__.items():
            if inspect.isclass(value):
                if parentclass:
                    if not issubclass(value, parentclass):
                        continue
                self.log.debug("Found class '%s'", value)
                classes.append(value)
        return classes

    def sessions(self, module):
        return self.classes(module, Session)

    def load(self, sessionname):
        sessions = self.sessions(sessionname)
        if not sessions:
            self.log.warning("Could not load any session with name '%s'",
                             sessionname)
            return None
        session = sessions[0]()
        self.log.info("Loaded session '%s'", sessionname)
        return session
