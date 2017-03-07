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

_REFS = ['$ref', ':ref:']


def get_json_pointer(node):
    """
    Generate a unique link in order to make the node's value linkable.
    The link follows the JSON Pointer style.

    Args:
        node(``TreeNode``): the node whose value needs to be linkable

    Returns:
        string: the value consists of the node's ancestors values, the
            nodes'value itself and its ID
    """
    ancestors = node.ancestors()
    if ancestors:
        root = ancestors.pop(0)
        ancestors_path = ''

        if ancestors:
            ancestors_path = '/' + '/'.join([n.id for n in ancestors])

        return '{}#{}/{}'.format(root.value, ancestors_path, node.id)
    return '{}#/'.format(node.id)


def ref2json_pointer(value):
    """
    Return a json pointer from the given string. ``value`` must be a
    restructured-text ref or a $ref schema element.

    Example:

        $ref: elements/title.json       -->     :ref:`title.json#/`

    Args:
        value(string): the value containing a :ref: string.

    Returns:
        string: a restructured-text `:ref:` link pointing to the correspondent
            json pointer of `value`

    Raises:
        ValueError if a node containing a non-ref value is provided.
    """
    # check if `$ref` or `:ref:` are in the string
    if split_key_val(value)[0] not in _REFS:
        raise ValueError('Expected input containing a :ref: or $ref value. '
                         'Instead, got {}'.format(value))

    value = split_key_val(value)[1]
    value = value.split('/')[-1]
    return ':ref:`{}#/`'.format(value)


def resolver(node, required_item=False, key=None):
    """
    This function returns the json pointer related to the `node`'s content.
    If no matches are found in node's ancestors, then the flat value is
    returned. The ancestors upper limit for matching is defined by the
    ``TreeNode.relative_search`` function.

    If the ``research_value`` arg is provided, it will be used as searching
    criterion instead of the node's value.

    Args:
        node(``TreeNode``): the node whose content has to be resolved
            as a JSON pointer.

        required_item(bool): this flag indicates if the node is nested in a
            `required` node. Used by ``TreeNode.relative_search`` function.

        key(string): the string used to mach a node in the tree.

    Result:
        string: a json pointer to a node that matches the ``node``'s content,
            otherwise the node's content itself.
    """
    search_by = key if key else node.id
    relative_node = node.relative_search(required_item)

    if relative_node:
        return ':ref:`{}`'.format(get_json_pointer(relative_node) +
                                  '/' + search_by)
    else:
        return ':ref:`{}`'.format(search_by)


def split_key_val(custom_string, separator=": "):
    """
    Return a (key, value) tuple by splitting the string in the first occurrence
    of ``separator`` character.

    Args:
        custom_string(string): the string to split
        separator(string): he character used to split ``custom_string``

    Returns:
        a (key, value) tuple
    """
    key = custom_string.split(separator)[0]
    start_index = custom_string.index(separator)

    # substring starting after ': ' (blank space included)
    val = custom_string[start_index + 2:]
    return key, val
