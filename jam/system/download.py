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
import ftplib

import jam.logging

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


class UnkownUrlScheme(DownloaderError):

    def __init__(self, urlscheme, filename):
        self.urlscheme = urlscheme
        self.filename = filename

    def __str__(self):
        return "Unkown urlscheme '%s'. Can't download '%s'" % (self.urlscheme,
                    self.filename)


class Downloader(object):

    def copy(self, filename, overwrite=False):
        raise NotImplementedError()

    def verify(self, hashes):
        pass


class FtpDownloader(Downloader):

    def __init__(self, url):
        self.url = url
        self.log = jam.logging.getLogger("jam.ftpdownloader")

    def copy(self, filename, overwrite=False):
        ftp = ftplib.FTP(self.url.netloc)
        ftp.login()
        f = open(filename, 'w')
        try:
            filesize = ftp.size(self.url.path)
        except ftplib.all_errors:
            filesize = 0
        if filesize:
            self.log.info("downloading %s to %s (%.2f KiB)" % \
                          (self.url.geturl(), filename, filesize / 1024))
        else:
            self.log.info("downloading %s to %s" % \
                          (self.url.geturl(), filename))
        try:
            ftp.retrbinary("RETR " + self.url.path, f.write)
            ftp.quit()
        finally:
            f.close()


class HttpDownloader(Downloader):

    def __init__(self, url):
        self.url = url
        self.log = jam.logging.getLogger("jam.httpdownloader")

    def copy(self, filename, overwrite=False):
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


class LocalFileDownloader(Downloader):

    def __init__(self, url, root_dir=None):
        self.url = url
        self.root_dir = root_dir
        self.log = jam.logging.getLogger("jam.localfiledownloader")

    def copy(self, filename, overwrite=False):
        path = self.url.path
        if not self.url.scheme and self.root_dir:
            path = os.path.join(self.root_dir, path)
        self.log.debug("copying '%s' to '%s'" % (path, filename))
        shutil.copy(path, filename)


class GitDownloader(Downloader):

    def __init__(self, url, branch):
        self.url = url
        self.branch = branch

    def copy(self, filename):
        pass


class UrlDownloader(object):

    def __init__(self, session, urlstr):
        self.url = urlstr
        self.session = session
        self.log = jam.logging.getLogger("jam.downloader")

        if self.url.startswith("git"):
            self.downloader = GitDownloader(self.url, session.branch if
                                            hasattr(session, "branch") else None)
            self.filename = ""
            return

        url = urlparse(urlstr)
        self.filename = os.path.basename(urlstr)
        if url.scheme == 'http' or url.scheme == 'https':
            self.downloader = HttpDownloader(urlstr)
        elif url.scheme == "file" or not url.scheme:
            self.downloader = LocalFileDownloader(url, session.session_path)
        elif url.scheme == "ftp":
            self.downloader = FtpDownloader(url)
        else:
            raise UnkownUrlScheme(url.scheme, self.url)

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
        # TODO support more hash algorithms and calculate all hashes with the
        # same filedesriptor. Currently the file is opened several times
        # hashcalc.set_hashes(['hasha', 'hashb'])
        # calc_hash_dict = hashcalc.calculate_hashes()
        for (type, value) in hashes.items():
            if type == 'md5':
                calc_value = hashcalc.md5()
            elif type == 'sha1':
                calc_value = hashcalc.sha1()
            else:
                DownloaderError("Hash type '%s' for '%s' is not supported" %
                        (type, this.filename))
            if calc_value != value:
                # TODO calc all hashes and raise error afterwards
                raise DownloaderHashError(self.filename, value, calc_value, type)
            else:
                self.log.debug("%s hash '%s' is valid for '%s'" % (type, value,
                                                           self.filename))
