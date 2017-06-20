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

"""
This module defines methods and rules used to parse a ``TreeNode`` to
restructured-text strings.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import re

from jsonschema2rst.json_pointer_util import *
from jsonschema2rst.rst_utils import *

PROPERTIES = bold('Properties:')
ANY_OF = 'May satisfy *any* of the following definitions:'
ALL_OF = 'Must satisfy *all* of the following definitions:'
ONE_OF = 'Must satisfy *exactly one* of the following definitions:'
ENUM = bold('Allowed values:')
ITEMS = "Every element of {} is:"
REQUIRED = 'Required'


CSS_SECT_TITLE = "section-title"
CSS_TITLE = "title"
CSS_SUB_TITLE = "sub-title"


YML_EXTENSION = '.yml'
JSON_EXTENSION = '.json'
RST_EXTENSION = '.rst'
HTML_EXTENSION = '.html'


SECTION_REPLACEMENT = {
    'items': lambda node: val2parent(node),
}

# this dict contains all nodes that have to be processed using their children
TO_REMOVE = {
    'properties': lambda node: PROPERTIES + get_links(node.children),
    'anyOf': lambda node: ANY_OF,
    'allOf': lambda node: ALL_OF,
    'oneOf': lambda node: ONE_OF,
    'enum': lambda node: ENUM + NL + get_enums(node),    # create a bullet list
    'required': lambda node: kv_field(REQUIRED, get_required(node)),
}

# dict of all nodes whose value, in [key, value] entry, has to be changed
TO_PROCESS = {
    '$ref': lambda node: kv_field('Reference', ref2json_pointer(node.value)),
    'title': lambda node: get_title(node),
    'description': lambda node: make_description(node),

}

# dict of all nodes whose key, in [key, value] entry, has to be replaced
TO_REPLACE = {
    'additionalProperties': 'Additional properties allowed',
    '$schema': 'Schema',
    '$ref': 'Reference',
    'uniqueItems': 'Unique Items',
    'True': 'Yes',
    'False': 'No',
}


TO_COLLAPSE = ['items']


_REF = ':ref:'
# does not match absolute ref link e.g. :ref:'filename#/path/to/prop'
ref_pattern = re.compile(r":ref:`[^#`]*`")


def restify(node):
    """
    Create a restructured-text string from a ``TreeNode`` object's value.

    Args:
        node(``TreeNode``): the node whose content is used to create a
            restructured-text string.

    Return:
        string: the node's value in restructured-text format. Note that value
            can be wrapped by some RST constructs.
    """
    if ':' in node.value:           # value has to be printed as "key: val"

        key, val = split_key_val(node.value)

        if key in TO_PROCESS.keys():
            return TO_PROCESS[key](node)

        if key in TO_REPLACE:
            key = TO_REPLACE[key]
            val = TO_REPLACE.get(val, val)

        return kv_field(key, val)

    else:
        if node.value in TO_COLLAPSE:
            rebase_level(node, -1)

        if node.value in TO_REMOVE:
            return _apply_rule(node, TO_REMOVE)

        else:
            if node.value in SECTION_REPLACEMENT:
                return _apply_rule(node, SECTION_REPLACEMENT)

            # value is a section title
            return section_link(node) + section_title(node)


def _file_title(node):
    if node.value.endswith(YML_EXTENSION):
        node.value = change_extension(node.value, JSON_EXTENSION)
    return container(node.value, CSS_SECT_TITLE)


def section_title(node):
    """
    Create a section title, using a different set of character based on node's
    level. If the title value is in SECTION_REPLACEMENT dictionary,
    it is replace by the correspondent new value
    e.g.

        SECTION_TITLE   ->  CUSTOM_TITLE
                            =============
    Args:
        node(``TreeNode``): the node representing a section

    Return:
        string: a restructured-text section title
    """
    sect_title = node.value

    if sect_title in SECTION_REPLACEMENT:
        sect_title = SECTION_REPLACEMENT(node)
    sect_title = change_extension(sect_title, '')
    return make_title(sect_title, node.lvl)


def make_description(node):
    """
    Ensure that inner RST formatted string will be used in the right manner.

    Args:
        node(``TreeNode``): the node containing a description.

    Return:
        string: a restructured-text plain string
    """
    description = split_key_val(node.value)[1]  # remove `description:`

    matches = ref_pattern.findall(description)

    for m in matches:
        ref = _REF + '`'
        search_key = m[len(ref):len(m) - 1]  # remove ":ref:`" and the last "`"

        working_ref = resolver(node, key=search_key)
        description = description.replace(m, working_ref)

    return description.strip()


def get_links(node_list):
    """
    Generate rst link, separated by a comma, for every node in the given list.
    Every link follows the JSON Pointer style.

    Args:
        node_list(list<TreeNode>): list of nodes from which generate links.

    Return:
        string: a csv string containing rst formatted links
    """
    return ', '.join([":ref:`{}`".format(get_json_pointer(node))
                      for node in sorted(node_list, key=lambda n:n.value)])


def get_enums(node):
    """
    Create a rst bullet list from the children list of a TreeNode object.

    Example:
                        enum                    * Europe
                      /  |  \          ->       * Asia
                Europe Asia America             * America

    Args:
        node(``TreeNode``): the node whose children will be represented as
            bullet list

    Return:
        string: a rst formatted bullet list
    """
    bullet_list = NL.join([bullet(child.value) for child in node.children])
    node.children = []      # children will not be processed again
    return NL + bullet_list


def get_required(node):
    """
    Return a string describing required values.
    Node's children list then is emptied to prevent items re-processing.
    e.g.

              required
                /  \
            value   schema      ->       Required: value, schema
    Args:
        node(``TreeNode``): the 'required' node

    Return:
        string: a formatted string listing all children' required values
     """
    required_list = ', '.join([resolver(child, True)
                               for child in node.children])

    node.children = []  # children will not be processed again
    return required_list


def get_title(node):
    title = split_key_val(node.value)[1]
    return container(title, CSS_TITLE)


def val2parent(node):
    """
    Append the node's parent value to the current node's one
    e.g.

                Parent:     job
                             |     ->    'job items'
                Node:      items
    Args:
        node(``TreeNode``): the parent node

    Return:
        string: a parent-value child-value formatted string
    """
    return container(ITEMS.format(bold(node.parent.value)), CSS_SUB_TITLE)


def _apply_rule(node, rules):
    func = rules.get(node.value)
    return func(node)


def rebase_level(node, amount):
    """
    Level field of every node in the subtree rooted in :param node,
    node excluded, is increased by :param amount.

    This method allows to change the level field in every node in a sub-tree.

    Exampple:
         Non-printed nodes don't allow their children to be printed correctly,
         since the RST nesting level is not respected (there will be a
         missing nesting level in the rst hierarchy).
         For this reason, all children' level fields are changed in order
         to respect the nesting.

         For example:
               LVL:    0      1        2       3
                     node0 - node1 - node2 - node3

             if node1 is going to not be printed, the hierarchy becomes:
               LVL:    0      1        1       2
                    node0 - node1 - node2 -- node3

    Args:
        node(``TreeNode``): the subtree's root to update
        amount(int): the increasing/decreasing value for nodes level.
    """
    for child in node.children:
        child.lvl += amount
        rebase_level(child, amount)


def change_extension(value, new_ext):
    """
    Treats `value` as a file name, changing its extension with `new_ext`. If it
    hasn't,
    the new extension is just added

    Args:
        value(string): the value to which change the extension
        new_ext(string): the new extension

    Returns:
        string: the given `value` having `new_ext` as extension.
    """
    return os.path.splitext(value)[0] + str(new_ext)
