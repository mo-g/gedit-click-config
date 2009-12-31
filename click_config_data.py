# -*- coding: utf8 -*-
#  Click_Config plugin for Gedit
#
#  Copyright (C) 2009 Derek Veit
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
This module provides objects for storing and changing the configuration data in
the Click_Config plugin for Gedit.

Classes:
SelectionOp -- a text selection operation
ConfigSet -- a set of SelectionOp names, one for each type of click
Config -- the whole store of configuration data for Click_Config

"""

import copy
import os
import shutil

from click_config_dictfile import read_dict_from_file, write_dict_to_file

class SelectionOp(object):
    
    """
    Stores a named regex expression and flags for selecting text.
    
    Usage:
    
    select_op = SelectionOp(
        name='Gedit word',
        pattern=r"[a-zA-Z]+|[0-9]+|[^a-zA-Z0-9]+",
        flags=0
        preserved=True)
    
    Public attributes:
    name -- Name of the SelectionOp.
    pattern -- Pattern suitable as an argument to re.compile.
    flags -- Regular expression flags (based on Python re module constants).
    preserved -- Read-only flag for ConfigUI to check before modifying.).
    
    """
    
    def __init__(self, name_or_dict=None, pattern='', flags=0, preserved=0):
        """
        Define a new SelectionOp from a name, a regex pattern, and regex flags
        or from a dictionary with keys 'name', 'pattern', and 'flags'.
        """
        self.name = ''
        """Name of the SelectionOp."""
        
        self.pattern = ''
        """Pattern suitable as an argument to re.compile."""
        
        self.flags = 0
        """Regular expression flags (based on Python re module constants)."""
        
        self.preserved = False
        """Read-only flag for ConfigUI to check before modifying.)."""
        
        if isinstance(name_or_dict, dict):
            dictionary = name_or_dict
            self.from_dict(dictionary)
        else:
            name = name_or_dict or 'None'
            self.name = name
            self.pattern = pattern
            self.flags = flags
            self.preserved = preserved
    
    def copy(self):
        """Return a copy of the SelectionOp."""
        return copy.deepcopy(self)
    
    def to_dict(self):
        """Return a dictionary representing this object."""
        return {
            'name': self.name,
            'pattern': self.pattern,
            'flags': self.flags,
            'preserved': self.preserved,
            }
    
    def from_dict(self, dictionary):
        """Return a dictionary representing this object."""
        self.name = dictionary['name']
        self.pattern = dictionary['pattern']
        self.flags = dictionary['flags']
        self.preserved = dictionary['preserved']
    
    def is_equal_to(self, op):
        is_equal = (
            self.name == op.name and
            self.pattern == op.pattern and
            self.flags == op.flags and
            self.preserved == op.preserved
            )
        return is_equal

class ConfigSet(object):
    
    """
    Stores a named set of SelectionOp names, one for each of five click types.
    
    Usage:
    
    configset = ConfigSet(
        name='Gedit built-in',
        op_names=['None', 'Gedit word', 'Line', 'None', 'None'])
        #    single, double, triple, quadrulpe, quintuple
    
    """
    
    def __init__(self, name_or_dict=None, op_names=None, preserved=0):
        """
        Define a new ConfigSet from a name and a list of SelectionOp names
        or from a dictionary with keys 'name' and 'op_names'.
        """
        self.name = ''
        """Name of the ConfigSet."""
        
        self.op_names = []
        """A SelectionOp name for each click type."""
        
        self.preserved = False
        """Read-only flag for ConfigUI to check before modifying.)."""
        
        if isinstance(name_or_dict, dict):
            dictionary = name_or_dict
            self.from_dict(dictionary)
        else:
            name = name_or_dict
            self.name = name
            self.op_names = op_names
            self.preserved = preserved
        
    def copy(self):
        """Return a copy of the ConfigSet."""
        return copy.deepcopy(self)
    
    def to_dict(self):
        """Return a dictionary representing this object."""
        return {
            'name': self.name,
            'op_names': self.op_names,
            'preserved': self.preserved,
            }
    
    def from_dict(self, dictionary):
        """Return a dictionary representing this object."""
        self.name = dictionary['name']
        self.op_names = dictionary['op_names']
        self.preserved = dictionary['preserved']
    
    def is_equal_to(self, configset):
        is_equal = (
            self.name == configset.name and
            self.op_names == configset.op_names and
            self.preserved == configset.preserved
            )
        return is_equal

class Config(object):
    
    """
    Main data store for Click_Config.
    
    Usage:
    
    conf = Config()
    conf.filename = '/home/[user]/.gnome2/gedit/plugins/configfile'
    conf.load()
    
    for configset in conf.configsets:
        print configset.name
        for op_name in configset.op_names:
            print '    %s' % op_name
    
    click = 2  # double-click
    select_op = conf.get_op(2)
    
    configset = conf.get_configset()
    
    conf.set_op(2, 'Line')
    conf.set_op(2, 'Line', 'Custom configset name')
    
    select_op_name = conf.get_op(2).name
    select_op_name = conf.get_op(2, 'Custom set name').name
    
    pattern = conf.get_pattern(   )
    
    conf.save()
    
    """
    
    def __init__(self):
        """Start empty configuration."""
        
        self.current_configset_name = ''
        """Name of the current ConfigSet."""
        
        self.current_op_name = ''
        """Name of the current SelectionOp (for the Define section)."""
        
        self.configsets = []
        """List of ConfigSet objects (not just the names)."""
        
        self.ops = []
        """List of SelectionOp objects (not just the names)."""
        
        self.filename = ''
        """Full path and filename for configuration file."""
    
    def copy(self):
        """Return a copy of the Config."""
        return copy.deepcopy(self)
    
    # ConfigSet access
    
    def add_configset(self, configset):
        configset_name = configset.name
        configset_names = [item.name for item in self.configsets]
        if configset_name in configset_names:
            index = configset_names.index(configset_name)
            self.configsets[index] = configset
        else:
            self.configsets.append(configset)
    
    def remove_configset(self, configset):
        self.configsets.remove(configset)
    
    def get_configset(self, configset_name=None):
        """
        Return the ConfigSet with this name,
        or return the current ConfigSet if no name is given.
        """
        configset_name = configset_name or self.current_configset_name
        for item in self.configsets:
            if item.name == configset_name:
                configset = item
                break
        return configset
    
    def set_configset(self, configset=None, configset_name=None):
        """
        Add the ConfigSet if provided as an object.
        Set the ConfigSet name as current.
        Required argument:
                configset
            or  configset_name
        """
        if configset:
            self.add_configset(configset)
            configset_name = configset.name
        self.current_configset_name = configset_name
    
    def get_configset_names(self):
        """Return a list of the ConfigSet names."""
        configset_names = [item.name for item in self.configsets]
        configset_names = configset_names[0:2] + sorted(configset_names[2:])
        return configset_names
    
    # SelectionOp access
    
    def add_op(self, op):
        op_name = op.name
        op_names = [item.name for item in self.ops]
        if op_name in op_names:
            index = op_names.index(op_name)
            self.ops[index] = op
        else:
            self.ops.append(op)
    
    def remove_op(self, op_or_op_name):
        if isinstance(op_or_op_name, str):
            op_name = op_or_op_name
            op = self.get_op(op_name=op_name)
        else:
            op = op_or_op_name
        self.ops.remove(op)
    
    def get_op(self,
        op_name=None,
        click=None,
        configset_name=None,
        configset=None
        ):
        """
        Return the SelectionOp associated with given criteria.
        Arguments can be: op_name
                      or  configset and click
                      or  configset_name and click
                      or  click (will use current ConfigSet)
        Otherwise, returns the current SelectionOp (of the Define section).
        """
        if not op_name:
            if click:
                configset = (configset or
                            self.get_configset(configset_name))
                op_name = configset.op_names[click - 1]
            else:
                op_name = self.current_op_name
        for op in self.ops:
            if op.name == op_name:
                return op
    
    def set_op(self,
        op=None,
        op_name=None,
        click=None,
        configset_name=None,
        configset=None
        ):
        """
        Set the SelectionOp associated with given criteria.
        Required argument:
                op
            or  op_name
        Optional arguments:
                configset and click
            or  configset_name and click
            or  click (will use current ConfigSet)
        Otherwise, sets the current SelectionOp (of the Define section).
        """
        if op:
            self.add_op(op)
            op_name = op.name
        if click:
            configset = (configset or
                        self.get_configset(configset_name))
            index = self.configsets.index(configset)
            self.configsets[index].op_names[click - 1] = op_name
        else:
            self.current_op_name = op_name
    
    def get_op_names(self):
        """Return a list of the SelectionOp names."""
        op_names = [op.name for op in self.ops]
        op_names = op_names[0:1] + sorted(op_names[1:])
        return op_names
    
    # SelectionOp attribute access
    
    def get_pattern(self,
        op=None,
        op_name=None,
        click=None,
        configset_name=None,
        configset=None
        ):
        """
        Return the regex pattern associated with given criteria.
        Optional arguments:
                op
            or  op_name
            or  configset and click
            or  configset_name and click
            or  click (will use current ConfigSet)
        Otherwise, returns pattern from the current op (of the Define section).
        """
        op = op or self.get_op(op_name, click, configset_name, configset)
        pattern = op.pattern
        return pattern
    
    def get_flags(self,
        op=None,
        op_name=None,
        click=None,
        configset_name=None,
        configset=None
        ):
        """
        Return the regex flags associated with given criteria.
        Optional arguments:
                op
            or  op_name
            or  configset and click
            or  configset_name and click
            or  click (will use current ConfigSet)
        Otherwise, returns flags from the current op (of the Define section).
        """
        op = op or self.get_op(op_name, click, configset_name, configset)
        flags = op.flags
        return flags
    
    def set_pattern(self,
        pattern,
        op=None,
        op_name=None,
        click=None,
        configset_name=None,
        configset=None
        ):
        """
        Sets the regex pattern for the given criteria.
        Required argument:
                pattern
        Optional arguments:
                op
            or  op_name
            or  configset and click
            or  configset_name and click
            or  click (will use current ConfigSet)
        Otherwise, sets the pattern for the current op (of the Define section).
        """
        op = op or self.get_op(op_name, click, configset_name, configset)
        index = self.ops.index(op)
        self.ops[index].pattern = pattern
    
    def set_flags(self,
        flags,
        op=None,
        op_name=None,
        click=None,
        configset_name=None,
        configset=None
        ):
        """
        Sets the regex flags for the given criteria.
        Required argument:
                flags
        Optional arguments:
                op
            or  op_name
            or  configset and click
            or  configset_name and click
            or  click (will use current ConfigSet)
        Otherwise, sets the flags for the current op (of the Define section).
        """
        op = op or self.get_op(op_name, click, configset_name, configset)
        index = self.ops.index(op)
        self.ops[index].flags = flags
    
    # File access
    
    def load(self):
        """Load the configuration."""
        config_dict = read_dict_from_file(self.filename)
        self.current_configset_name = config_dict['current_configset_name']
        self.current_op_name = config_dict['current_op_name']
        self.configsets = \
            [ConfigSet(dict_) for dict_ in config_dict['configsets']]
        self.ops = \
            [SelectionOp(dict_) for dict_ in config_dict['ops']]
    
    def save(self):
        """Save the configuration."""
        config_dict = {}
        config_dict['current_configset_name'] = self.current_configset_name
        config_dict['current_op_name'] = self.current_op_name
        config_dict['configsets'] = [item.to_dict() for item in self.configsets]
        config_dict['ops'] = [item.to_dict() for item in self.ops]
        if os.path.exists(self.filename):
            shutil.copy2(self.filename, self.filename + '~')
        write_dict_to_file(config_dict, self.filename)
    
    def is_equal_to(self, config):
        if len(self.ops) != len(config.ops):
            return False
        for i in range(len(self.ops)):
            if not self.ops[i].is_equal_to(config.ops[i]):
                return False
        if len(self.configsets) != len(config.configsets):
            return False
        for i in range(len(self.configsets)):
            if not self.configsets[i].is_equal_to(config.configsets[i]):
                return False
        is_equal = (
            self.current_configset_name == config.current_configset_name and
            self.current_op_name == config.current_op_name
            )
        return is_equal

