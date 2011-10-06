# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# jam - An advanced package manager for Free Software
#
# This file is originally borrowed from git-buildpackage
# see https://honk.sigxcpu.org/piki/projects/git-buildpackage/
#
# Copyright (C) 2010 Guido Guenther <agx@sigxcpu.org>
# Copyright (C) 2011 Björn Ricks <bjoern.ricks@googlemail.com>
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

"""Simple colored logging class"""

import os
import sys

class Logger(object):

    DEBUG, INFO, NORMAL, WARNING, ERROR, NONE = range(6)

    COLOR_NONE = 0
    COLOR_BLACK, COLOR_RED, COLOR_GREEN = range(30,33)

    COLOR_SEQ = "\033[%dm"
    BOLD_SEQ = "\033[1m"


    format = ("%(color)s"
              "%(levelname)s:%(name)s: "
              "%(message)s"
              "%(coloroff)s")

    def __init__(self, name, level=None):
        self.levels = { self.NORMAL:  [ 'normal', self.COLOR_BLACK ],
                        self.DEBUG:   [ 'debug',  self.COLOR_GREEN ],
                        self.INFO:    [ 'info',   self.COLOR_GREEN ],
                        self.WARNING: [ 'warn',   self.COLOR_RED   ],
                        self.ERROR:   [ 'error',  self.COLOR_RED   ],
                        self.NONE:    [ 'none',   self.COLOR_NONE  ],
                        }
        self.name = name
        self.set_color(self._is_tty())
        self.set_level(level)

    def set_level(self, level):
        self.level = level

    def _is_tty(self):
        if (os.getenv("EMACS") and
            os.getenv("INSIDE_EMACS", "").endswith(",comint")):
            return False

        if (hasattr(sys.stderr, "isatty") and
            hasattr(sys.stdout, "isatty") and
            sys.stderr.isatty() and
            sys.stdout.isatty()):
            return True

        return False

    def set_color(self, color):
        self.color = color
        if self.color:
            self.get_color = self._color
            self.get_coloroff = self._color_off
        else:
            self.get_color = self.get_coloroff = self._color_dummy

    def _color_dummy(self, level=None):
        return ""

    def _color(self, level):
        return self.COLOR_SEQ % (self.levels[level][1])

    def _color_off(self):
        return self.COLOR_SEQ % self.COLOR_NONE


    def log(self, level, message):
        cur_level = self.level
        if not cur_level:
            cur_level = getRootLogger().level
        if level < cur_level:
            return

        out = [sys.stdout, sys.stderr][level >= self.WARNING]
        print >>out, self.format % { 'levelname': self.levels[level][0],
                                     'color': self.get_color(level),
                                     'message': message,
                                     'coloroff': self.get_coloroff(),
                                     'name': self.name,}

    def error(self, msg):
        self.log(Logger.ERROR, msg)

    def warn(self, msg):
        self.log(Logger.WARNING, msg)

    def info(self, msg):
        self.log(Logger.INFO, msg)

    def debug(self, msg):
        self.log(Logger.DEBUG, msg)

    def normal(self, msg):
        self.log(Logger.NORMAL, msg)

    def out(self, msg):
        print msg


loggers = {"jam": Logger("jam", Logger.INFO)}

def getLogger(name):
    if name in loggers:
        return loggers[name]
    logger = Logger(name)
    loggers[name] = logger
    return logger

def getRootLogger():
    return loggers["jam"]

