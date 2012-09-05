# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# kaizen - Continuously improve, build and manage free software
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

import urllib2
import os.path
import shutil
import ftplib

import kaizen.logging

from urlparse import urlparse

from kaizen.utils import Hash
from kaizen.error import KaizenError

class DownloaderError(KaizenError):
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

    depends = []

    def __init__(self, rules, urlstr):
        self.rules = rules
        self.urlstr = urlstr
        self.log = kaizen.logging.getLogger(self)

    def copy(self, destination, overwrite=False):
        raise NotImplementedError()

    def verify(self, hashes):
        pass


class FileDownloader(Downloader):

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
    def get_filename(self, destination):
        filename = os.path.basename(self.urlstr)
        if os.path.isdir(destination):
            return os.path.join(destination, filename)
        return destination


class FtpDownloader(FileDownloader):

    def __init__(self, rules, urlstr):
        super(FtpDownloader, self).__init__(rules, urlstr)
        self.url = urlparse(self.urlstr)

    def copy(self, destination, overwrite=False):
        filename = self.get_filename(destination)
        self.filename = filename

        if os.path.exists(filename) and not overwrite:
            self.log.info("'%s' has been downloaded already" % filename)
            return

        ftp = ftplib.FTP(self.url.netloc)
        ftp.login()

        with open(filename, 'w') as f:
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
            ftp.retrbinary("RETR " + self.url.path, f.write)
            ftp.quit()
        return filename


class HttpDownloader(FileDownloader):

    def copy(self, destination, overwrite=False):
        filename = self.get_filename(destination)
        self.filename = filename

        if os.path.exists(filename) and not overwrite:
            self.log.info("'%s' has been downloaded already" % filename)
            return

        u = urllib2.urlopen(self.urlstr)
        f = open(filename, 'w')
        meta = u.info()
        content_length_header = meta.getheaders("Content-Length")
        if content_length_header:
            filesize = int(content_length_header[0])
            self.log.info("downloading %s to %s (%.2f KiB)" % (self.urlstr,
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

        return filename


class LocalFileDownloader(Downloader):

    def __init__(self, url, root_dir=None):
        self.url = url
        self.root_dir = root_dir
        self.log = kaizen.logging.getLogger(self)

    def copy(self, filename, overwrite=False):
        path = self.url.path
        if not self.url.scheme and self.root_dir:
            path = os.path.join(self.root_dir, path)
        self.log.debug("copying '%s' to '%s'" % (path, filename))
        shutil.copy(path, filename)


class GitDownloader(Downloader):

    def __init__(self, rules, urlstr):
        super(GitDownloader, self).__init__(rules, urlstr)
        self.branch = getattr(rules, "branch", None)

    def copy(self, path, overwrite=False):
        from dulwich.repo import Repo
        from dulwich.client import get_transport_and_path
        r = Repo.init(path)
        client, host_path = get_transport_and_path(self.url)
        remote_refs = client.fetch(host_path, r,
            determine_wants=r.object_store.determine_wants_all,
            progress=sys.stdout.write)
        if self.branch:
            r["HEAD"] = remote_refs[branch]
        else:
            r["HEAD"] = remote_refs["HEAD"]


class UrlDownloader(Downloader):

    def __init__(self, rules, urlstr):
        super(UrlDownloader, self).__init__(rules, urlstr)
        urltype = getattr(rules, "download_type", None)

        if urlstr.startswith("git") or urltype == "git":
            self.downloader = GitDownloader(rules, urlstr)
            return

        url = urlparse(urlstr)
        if url.scheme == 'http' or url.scheme == 'https' or urltype == "http" \
            or urltype == "https":
            self.downloader = HttpDownloader(rules, urlstr)
        elif url.scheme == "file" or not url.scheme or urltype == "file":
            self.downloader = LocalFileDownloader(url, rules.rules_path)
        elif url.scheme == "ftp" or urltype == "ftp":
            self.downloader = FtpDownloader(url)
        else:
            raise UnkownUrlScheme(url.scheme, self.url)

    def copy(self, destination, overwrite=False):
        return self.downloader.copy(destination, overwrite)

    def verify(self, hashes):
        self.downloader.verify(hashes)
