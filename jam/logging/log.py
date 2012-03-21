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
    return logging.getLogger("jam")

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

