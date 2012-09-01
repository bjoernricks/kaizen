# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# kaizen - Continously improve, build and manage free software
#
# Copyright (C) 2007, 2008 by Intevation GmbH
# Copyright (C) 2011  Björn Ricks <bjoern.ricks@gmail.com>
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

"""Helper functions to run subprocesses in various ways"""

import os
import subprocess

from kaizen.error import JamError


class SubprocessError(JamError):

    def __init__(self, command, returncode, output=None):
        self.command = command
        self.returncode = returncode
        self.output = output

    def __str__(self):
        retval = "Command %s finished with return code %d" % (self.command,
                     self.returncode)
        if self.output:
            retval += "Output was: '%s'" % self.output
        return retval


def call(command, suppress_output=False, extra_env=None, inputdata=None,
         logfile=None, **kw):
    """Run command as a subprocess and wait until it is finished.

    The command should be given as a list of strings to avoid problems
    with shell quoting.  If the command exits with a return code other
    than 0, a SubprocessError is raised.
    """
    if inputdata is not None:
        kw["stdin"] = subprocess.PIPE
    if logfile:
        kw["stdout"] = kw["stderr"] = open(logfile, "w")
    elif suppress_output:
        kw["stdout"] = open(os.devnull, "w")
        kw["stderr"] = open(os.devnull, "w")
    env = kw.pop("env", None)
    if extra_env:
        if env is None:
            env = os.environ.copy()
        env.update(extra_env)
    try:
        process = subprocess.Popen(command, env=env, **kw)
    except OSError,e:
        raise SubprocessError(command, e.errno, e.strerror)

    if inputdata is not None:
        process.stdin.write(inputdata)
        process.stdin.close()
    ret = process.wait()
    if ret != 0:
        raise SubprocessError(command, ret)


def capture_output(command, **kw):
    """Return the stdout and stderr of the command as a string

    The command should be given as a list of strings to avoid problems
    with shell quoting.  If the command exits with a return code other
    than 0, a SubprocessError is raised.
    """
    proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, **kw)
    output = proc.communicate()[0]
    if proc.returncode != 0:
        raise SubprocessError(command, proc.returncode, output)
    return output

def capture_stdout(command, **kw):
    """Return the stdout of the command as a string

    The command should be given as a list of strings to avoid problems
    with shell quoting.  If the command exits with a return code other
    than 0, a SubprocessError is raised.
    """
    proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, **kw)
    output, error = proc.communicate()
    if proc.returncode != 0:
        raise SubprocessError(command, proc.returncode, error)
    return output
