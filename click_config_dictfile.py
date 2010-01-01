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

# Dictionary file functions for the configuration file.

"""
This module provides functions for writing and reading Python dictionaries as
text files, formatted for readability.

"""

def write_dict_to_file(dictionary, filename):
    """Write a dictionary to a text file."""
    file_handle = open(filename, 'w')
    dict_string = format_dict(dictionary)
    file_handle.writelines(dict_string)
    file_handle.close()

def format_dict(dictionary, indent_level=0):
    """
    Format the dictionary string for readability.
    Otherwise, repr(dictionary) would work.
    """
    indent_level += 1
    indent = "    " * indent_level
    string = "{\n"
    for key in sorted(dictionary.iterkeys()):
        string += indent + repr(key) + ': '
        value = dictionary[key]
        if type(value).__name__ == 'dict':
            string += indent + format_dict(value, indent_level) + ',\n'
        elif type(value).__name__ == 'list':
            string += format_list(value, indent_level) + ',\n'
        else:
            string += repr(value) + ',\n'
    string += indent + "}"
    return string
    
def format_list(list_, indent_level=0):
    """
    Format the dictionary string for readability.
    Otherwise, repr(list_) would work.
    """
    indent_level += 1
    indent = "    " * indent_level
    string = "[\n"
    for value in list_:
        if type(value).__name__ == 'dict':
            string += indent + format_dict(value, indent_level) + ',\n'
        elif type(value).__name__ == 'list':
            string += indent + format_list(value, indent_level) + ',\n'
        else:
            string += indent + repr(value) + ',\n'
    string += indent + "]"
    return string
    
def read_dict_from_file(filename):
    """Read a properly formatted text file in as a dictionary."""
    file_handle = open(filename, 'r')
    dict_string = file_handle.read()
    file_handle.close()
    dictionary = eval(dict_string)
    return dictionary

