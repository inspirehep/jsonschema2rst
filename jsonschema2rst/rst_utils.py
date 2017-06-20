# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE-SCHEMAS.
# Copyright (C) 2017 CERN.
#
# INSPIRE-SCHEMAS is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE-SCHEMAS is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE-SCHEMAS; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from jsonschema2rst.json_pointer_util import get_json_pointer

ADORNMENT_SYMBOL = {
    0: '=',
    1: '*',
    2: '+',
    3: '-',
    4: '#',
    5: '~',
    6: '>',
    7: '<',
    8: '.',
}


NL = '\n'
NL2 = 2 * NL
BLANK_SPACE = ' '
TAB = '\t'

RST_DIRECTIVES = ''' '''
# \n.. contents:: Table of Contents'''
# .. section-numbering::'''


def emphasize(val):
    return '*{}* '.format(val)


def explicit_link(link, link_text=""):
    if not link_text:
        link_text = link
    return '`{} <{}>`_'.format(link_text, link)


def bold(val):
    return '**{}** '.format(val)


def literal(val):
    """
    Gives a restructured-text representation of the given value. If ``value``
    is a string containing more than one word they are separated by a comma
    having a plain style.

    Args:
        val(string) the string, containing one or more words separated by comma

    Returns:
        string: a restructured-text formatted string of words separated by
            plain commas
    """
    if val is None:
        return ""

    val_list = str(val).split(",")
    val_list = [_literal(word) for word in val_list]
    return ", ".join(val_list)


def _literal(val):
    return '``{}``'.format(val.strip())


def kv_field(k, v):
    v = str(v)
    if '`' not in v:
        v = literal(v)
    return ':{}: {}'.format(k, v)


def bullet(val):
    return '- {}'.format(val)


def section_link(node):
    return(NL + '.. _{}:' + NL2).format(get_json_pointer(node))


def line(level, value):
    if level < 0 or level >= len(ADORNMENT_SYMBOL):
        level = len(ADORNMENT_SYMBOL) - 1
    char = ADORNMENT_SYMBOL.get(level)
    return char * len(value)


def container(value, css=''):
    if not value:
        raise TypeError("Error: Can not create a container without content.")
    return '.. container:: {}\n\n {}'.format(css, value)


def make_title(value, level):
    value = str(value)
    return value + NL + line(level, value)
