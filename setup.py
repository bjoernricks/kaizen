#!/usr/bin/env python
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
#

from setuptools import setup, find_packages

import kaizen

with open("README") as readme:
    setup(name="kaizen",
        version=kaizen.__version__,
        description="",
        author="Björn Ricks",
        author_email="bjoern.ricks@gmail.com",
        url="https://github.com/bjoernricks/kaizen",
        license = "LGPLv2+, GPLv2+",
        long_description=readme.read(),
        packages=find_packages(),
        package_data = {"" : ["*.txt", "*.rst"],
            },
        # entry_points = { "console_scripts": ["kaizen=jam.console.main:main"] },
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
