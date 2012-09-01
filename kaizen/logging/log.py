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

import logging
import os

def getLogger(name):
    if isinstance(name, basestring):
        logger_name = name
    elif isinstance(name, type):
        logger_name = "%s.%s" % (name.__module__, name.__name__)
    elif isinstance(name, object):
        cls = name.__class__
        logger_name = "%s.%s" % (cls.__module__, cls.__name__)
    return logging.getLogger(logger_name)

def getRootLogger():
    return logging.getLogger("kaizen")

def out(message, fg=0, bg=0):
    print "%s%s%s" % (Color.start(fg, bg), message, Color.reset())

class Color(object):

    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(30, 38)
    NONE = 0

    CSI_SEQ = "\033["
    RESET_SEQ = CSI_SEQ + "0m"

    @staticmethod
    def start(fg=0, bg=0):
        seq = Color.CSI_SEQ + str(fg)
        if bg:
            seq += ";" + str(bg + 10)
        seq += "m"
        return seq

    @staticmethod
    def reset():
        return Color.RESET_SEQ


class ColorStreamHandler(logging.StreamHandler):

    levels = {logging.DEBUG: Color.GREEN,
              logging.INFO: Color.GREEN,
              logging.WARNING: Color.RED,
              logging.ERROR: Color.RED,
              logging.CRITICAL: Color.RED,
              logging.NOTSET: Color.NONE,
              }

    def is_tty(self):
        if getattr(self.stream, "isatty", False):
            return self.stream.isatty() 
        return False

    def color(self, message, record):
        if record.levelno in self.levels:
            fg = self.levels[record.levelno]
            message = Color.start(fg) + message + Color.reset()
        return message

    def format(self, record):
        message = logging.StreamHandler.format(self, record)
        if self.is_tty:
            # Don't colorize any traceback
            parts = message.split('\n', 1)
            parts[0] = self.color(parts[0], record)
            message = '\n'.join(parts)
        return message

