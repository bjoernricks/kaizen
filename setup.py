#!/usr/bin/env python
# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

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

from setuptools import setup, find_packages

import os.path
import jam.config

def read(fname):
    return open(os.path.join(os.path.dirname(__file__),
                             fname)).read()

setup(name="jam",
      version=jam.config.JAM_VERSION,
      description="",
      author="Björn Ricks",
      author_email="bjoern.ricks@gmail.com",
      url="https://github.com/bjoernricks/jam",
      license = "LGPLv2+, GPLv2+",
      long_description=read("README.md"),
      packages=find_packages(),
      package_data = { "" : ["*.txt", "*.md"],
                     },
      entry_points = { "console_scripts": ["jam=jam.main:main"] },
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Topic :: Utilities",
          "Topic :: Software Development",
          "Topic :: Software Development :: Build Tools",
          "Topic :: System :: Archiving :: Packaging",
          "Topic :: System :: Systems Administration",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "Intended Audience :: System Administrators",
          "Intended Audience :: End Users/Desktop",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
          "License :: OSI Approved :: MIT License",
          "License :: OSI Approved :: Python Software Foundation License",
          "Operating System :: MacOS",
          "Operating System :: POSIX",
          "Programming Language :: Python",
      ]
     )