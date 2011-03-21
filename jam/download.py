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

import logging
import urllib2

from urlparse import urlparse

class HttpDownloader:

    def __init__(self, url):
        self.url = url
        self.log = logging.getLogger("jam.httpdownloader")

    def copy(self, filename):
        u = urllib2.urlopen(self.url)
        f = open(filename, 'w')
        meta = u.info()
        filesize = int(meta.getheaders("Content-Length")[0])
        self.log.info("downloading %s (%.2f KiB)", self.url, filesize / 1024)
        filesizedl = 0
        while True:
            buffer = u.read(8192)
            if not buffer:
                break
            filesizedl += len(buffer)
            f.write(buffer)
            #status = r"[%3.2f%%]" % (filesizedl * 100. / filesize)
            #print status
        f.close()

class Downloader:

    def __init__(self, urlstr):
        url = urlparse(urlstr)
        self.url = urlstr
        self.filename = o.path.basename(o.path)
        
        if url.scheme == 'http' or url.scheme == 'https':
            self.downloader = HttpDownloader(urlstr)

    def copy(self, destination):
        if os.path.isdir(destination):
            filename = os.path.join(destination, self.filename)
        else:
            filename = destination
        self.downloader.copy(filename)

