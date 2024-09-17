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
This module allows to parse json and yaml schemas, generating restructured-text
content to document it.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

import yaml

from jsonschema2rst.rst_utils import NL, RST_DIRECTIVES
from jsonschema2rst.rst_writer import JSON_EXTENSION, change_extension, restify
from jsonschema2rst.tree_node import TreeNode

SORTING_ORDER = [
    "title",
    "description",
    "type",
    "format",
    "minimum",
    "maximum",
    "pattern",
    "required"
]


def schema2rst(schema_file, excluded_key):
    """
    Parse a json/yaml schema file into RST text.

    Example:
        with open("schema.json") as schema:
            print(jsonschema2rst(schema))

    Args:
        schema_file(file): a json or yaml schema file descriptor.

        excluded_key(string): csv containing schema's keywords to ignore

    Returns:
        string: a restructured-text string representing ``schema_file``
    """
    tree = TreeNode(os.path.basename(
        change_extension(schema_file.name, JSON_EXTENSION)))

    rst = RST_DIRECTIVES
    TreeNode.dict2tree(yaml.full_load(schema_file), tree, excluded_key)
    rst += _traverse_bfs(tree, _node2rst)
    return rst


def _node2rst(node):
    return NL + restify(node) + NL


def _traverse_bfs(node, traverse_func):
    """
    Traverse the tree rooted in ``node`` using the Breadth-first search (BFS)
    approach, applying to each node the ``traverse_func``  function.

    Args:
        node(``TreeNode``): the tree's root to traverse.

        traverse_func(function): the function to apply to each node in the tree

    Returns:
        The addition/concatenation of ``traverse_func`` results.
    """
    result = traverse_func(node)
    leaves = [child for child in node.children if child.is_leaf()]
    inners = [child for child in node.children if not child.is_leaf()]

    leaves = _sort_nodes(leaves, node.value)
    inners = _sort_nodes(inners, node.value)

    for leaf in leaves:
        result += _traverse_bfs(leaf, traverse_func)

    for inner in inners:
        result += _traverse_bfs(inner, traverse_func)

    return result


def _sort_nodes(leaves, parent_val=''):
    """
    Return a list of nodes ordered in according to the ``SORTING_ORDER``
    elements' index, if ``parent_val`` is not `properties`. Elements with a
    value not listed in ``SORTING_ORDER`` are appendend in a lexicographic
    order to the list.

    Example:
        (let's consider just the nodes values)

        leaves = ['pattern: foo', 'description: custom desc', 'title: bar']

        returns: ['title: bar', 'description: custom desc', 'pattern: foo']
                 |______________________________________|  |_______________|
                                    |                              |
                             SORTING_ORDER                lexicographic order
    Args:
        leaves(list<``TreeNode``>): the list of nodes to sort
        parent_val(string): the parent node's value

    Returns:
        the given list sorted in according to ``SORTING_ORDER``
    """
    priority = []
    if parent_val != 'properties':
        for key in SORTING_ORDER:
            for leaf in leaves:
                if key in leaf.value:
                    priority.append(leaf)
                    leaves.remove(leaf)
                    break

    # sorts lexicographically the rest of the list
    leaves = sorted(leaves, key=lambda node: node.value)
    return priority + leaves
