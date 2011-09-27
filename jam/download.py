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

import urllib2
import os.path
import shutil

import jam.log

from urlparse import urlparse

from jam.utils import Hash
from jam.error import JamError

class DownloaderError(JamError):
    pass

class DownloaderHashError(DownloaderError):

    def __init__(self, filename, expected, value, hashtype):
        self.filename = filename
        self.expected = expected
        self.value = value
        self.hashtype = hashtype

    def __str__(self):
        return "Invalid %s hash for '%s'. Calculated hash is '%s', expected " \
               "was '%s'" % (self.hashtype, self.filename, self.value, self.expected)


class HttpDownloader(object):

    def __init__(self, url):
        self.url = url
        self.log = jam.log.getLogger("jam.httpdownloader")

    def copy(self, filename):
        u = urllib2.urlopen(self.url)
        f = open(filename, 'w')
        meta = u.info()
        content_length_header = meta.getheaders("Content-Length")
        if content_length_header:
            filesize = int(content_length_header[0])
            self.log.info("downloading %s to %s (%.2f KiB)" % (self.url,
                                                               filename,
                                                               filesize / 1024))
        else:
            self.log.info("downloading %s to %s" % (self.url, filename))
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


class LocalFileDownloader(object):

    def __init__(self, url, root_dir=None):
        self.url = url
        self.root_dir = root_dir
        self.log = jam.log.getLogger("jam.localfiledownloader")

    def copy(self, filename):
        path = self.url.path
        if not self.url.scheme and self.root_dir:
            path = os.path.join(self.root_dir, path)
        self.log.debug("copying '%s' to '%s'" % (path, filename))
        shutil.copy(path, filename)


class Downloader:

    def __init__(self, urlstr, root_dir=None):
        url = urlparse(urlstr)
        self.url = urlstr
        self.root_dir = root_dir
        self.filename = os.path.basename(urlstr)
        self.log = jam.log.getLogger("jam.downloader")

        if url.scheme == 'http' or url.scheme == 'https':
            self.downloader = HttpDownloader(urlstr)
        elif url.scheme == "file" or not url.scheme:
            self.downloader = LocalFileDownloader(url, root_dir)
        # TODO: raise error if scheme is unknown

    def copy(self, destination, overwrite=False):
        if os.path.isdir(destination):
            filename = os.path.join(destination, self.filename)
        else:
            filename = destination
        self.filename = filename
        if not os.path.exists(filename) or overwrite:
            self.downloader.copy(filename)
        else:
            self.log.info("'%s' has been downloaded already" % self.filename)
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
                raise DownloaderHashError(self.filename, value, calc_value, type)
            else:
                self.log.debug("%s hash '%s' is valid for '%s'" % (type, value,
                                                           self.filename))
