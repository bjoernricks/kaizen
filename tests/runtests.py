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

import os
import sys
import unittest
import optparse

test_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(test_dir, os.pardir))

from kaizen.utils import list_dir

def find_test_modules(dirname, package = None):
    if package:
        prefix = package + "."
    else:
        prefix = ""

    suffix = ".py"
    (dirs, files) = list_dir(dirname, True)
    names = []
    for dir in dirs:
        dirname = dir.replace(test_dir + "/", "")
        names.extend([dirname + "." + prefix + name[:-len(suffix)] + ".suite"
            for name in os.listdir(dir)
                if name.startswith("test_") and name.endswith(suffix)])
    return names


def main():
    parser = optparse.OptionParser()
    parser.set_defaults(verbosity=1)
    parser.add_option("-v", "--verbose", action="store_const", const=2,
                      dest="verbosity")
    opts, rest = parser.parse_args()

    if rest:
        names = rest
    else:
        names = find_test_modules(test_dir)
    suite = unittest.defaultTestLoader.loadTestsFromNames(names)
    runner = unittest.TextTestRunner(verbosity=opts.verbosity)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())


if __name__ == "__main__":
    main()
