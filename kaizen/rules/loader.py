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

import kaizen.logging

from kaizen.utils import Loader, real_path
from kaizen.rules.rules import Rules

class RulesLoader(Loader):

    def __init__(self, config):
        super(RulesLoader, self).__init__()
        self.config = config
        self.log = kaizen.logging.getLogger(self)
        paths = self.config.get("rules")
        self.add_paths([real_path(path.strip()) for path in paths])

    def rules(self, modulename):
        as_module = "kaizen.rules._modules." + modulename
        module = self.module(modulename, as_module)
        if not module:
            return None
        return self.classes(module, Rules)

    def load(self, rulesname):
        rulestring = rulesname + ".rules"
        rules = self.rules(rulestring)
        if not rules:
            self.log.warn("Could not load any rules with name '%s'" %
                          rulesname)
            return None
        rules = rules[0]
        self.log.debug("Loaded rules class '%s'" % rules.__name__)
        return rules
