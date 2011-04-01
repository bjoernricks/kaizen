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

import urllib2
import os.path

import jam.log

from urlparse import urlparse

from jam.utils import Hash

class DownloaderError(Exception):
    pass

class DownloaderHashError(DownloaderError):

    def __init__(self, filename, expected, value):
        self.filename = filename
        self.expected = expected
        self.value = value

    def __str__(self):
        return "Invalid hash for '%s'. Calculated hash is '%s', expected was \
               '%s'" % (self.filename, self.value, self.expected)


class HttpDownloader(object):

    def __init__(self, url):
        self.url = url
        self.log = jam.log.getLogger("jam.httpdownloader")

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
        self.filename = os.path.basename(urlstr)
        self.log = jam.log.getLogger("jam.downloader")
        
        if url.scheme == 'http' or url.scheme == 'https':
            self.downloader = HttpDownloader(urlstr)

    def copy(self, destination, overwrite=False):
        if os.path.isdir(destination):
            filename = os.path.join(destination, self.filename)
        else:
            filename = destination
        self.filename = filename
        if not os.path.exists(filename) or overwrite:
            self.downloader.copy(filename)
        else:
            self.log.debug("'%s' has been downloaded already" % self.filename)
        return filename

    def verify(self, hashes):
        hashcalc = Hash(self.filename)
        for (type, value) in hashes.items():
            hashcalc.md5()
            if type == 'md5':
                calc_value = hashcalc.md5()
            elif type == 'sha1':
                calc_value = hashcalc.sha1()
            else:
                DownloaderError("Hash type '%s' for '%s' is not supported" %
                        (type, this.filename))
            if calc_value != value:
                raise DownloaderHashError(self.filename, value, calc_value)
            else:
                self.log.debug("Hash '%s' is valid for '%s'" % (value,
                                                           self.filename))
