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

import os
from collections import OrderedDict
from copy import copy

from six import string_types

_BLACK_LIST = []
_ROOT = "Root"
_NESTED_ELEMENT_FIELD = 'title'
NESTED_ELEMENT_NAME = 'element'
_NESTED_LIST_NAME = 'sub_list'
_PROPERTIES = 'properties'

# Python 2-3 compatibility
try:
    UNICODE_EXISTS = bool(type(unicode))
except NameError:
    unicode = str


class TreeNode(object):
    """Basic representation of a recursive tree data structure.

    Every node has a value field of string type, a list of children of the same
    type, and a reference to its parent node. Furthermore, every node has a
    level field, which tells the node's height in a hierarchical structure.
    When a parent node is provided, the level is increased by 1, otherwise
    the node is considered a root node, having level 0.
    """

    _ID = 0

    def __init__(self, val='', parent=None):
        """
        Constructor.

        Create a new TreeNode instance holding the given value.
        It also comes up with an empty children list.
        If a parent is provided, this node is appended to its children list and
        its level is given by increasing by 1 the parent's level.

        Args:
            val (string): the node's value
            parent (``TreeNode``): the node's parent.
        """
        self.value = unicode(val).strip()
        self.children = []
        self.parent = parent
        self.id = self.value

        if parent is not None:
            parent.children.append(self)
            self.lvl = parent.lvl + 1
        else:
            self.lvl = 0

    def is_leaf(self):
        """
        Check if the current TreeNode instance is a leaf node.

        Return:
            bool: True if the node has at least one child, else False
        """
        return len(self.children) is 0

    def __str__(self, level=0):
        ret = "\t" * level + repr(self.value) + "\n"
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret

    def __eq__(self, other):
        """
        Compares the current TreeNode instance with the given one in input,
        applying the following recursive definition: two TreeNode nodes are
        equal if their value is the same and
        if their children are
        equals.

        Args:
            other: the object to compare with.

        Return:
            bool: True if objects are equals as defined above, else False.
        """
        if not isinstance(other, self.__class__):
            return False

        if self.value == other.value and \
                len(self.children) == len(other.children):
            return all(child == other_child for child, other_child
                       in zip(self.children, other.children))
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def ancestors(self):
        """
        Return the list of ancestors of this node, ordered from the root to
        the node's parent.

        Returns:
             a list of ``TreeNode``
        """
        ancestors = []
        tmp = self
        while tmp.parent is not None:
            ancestors.append(tmp.parent)
            tmp = tmp.parent
        ancestors.reverse()
        return ancestors

    @classmethod
    def _next_id(cls):
        cls._ID += 1
        return cls._ID

    @classmethod
    def dict2tree(cls, dictionary, root_node, excluded_key=''):
        """
        Given a dictionary, this function recursively creates a full tree data
        structures that maps the given input. The ``root_node`` param is used
        as root of the new tree data structure.
        Leaves string values are aggregated to parents nodes in order to
        provide <key, val> values.


        If one of the blacklist's values matches a the current object's value,
        the whole sub-tree building process is
        interrupted.

        Args:
            dictionary(dict): a dictionary recursively processed to build a
                TreeNode by retrieving its content.

            root_node(``TreeNode``): the new tree's root that maps the given
                dictionary.

            excluded_key(string): csv containing schema's keywords to ignore

        Returns:
            ``TreeNode``: the built tree that maps the given dictionary
        """
        if dictionary is None:
            return TreeNode(_ROOT)

        if root_node is None:
            root_node = TreeNode(_ROOT)

        global _BLACK_LIST
        _BLACK_LIST = [key.strip() for key in excluded_key.split(',')]
        dictionary = OrderedDict(sorted(dictionary.items()))
        _build_tree(dictionary, root_node)

        return root_node

    def get_ancestor(self, value):
        """
        Return the first ancestor whose value field matches the given ``value``

        Args:
            value(string): the string used to search the closest ancestor.

        Return:
            ``TreeNode``: the closest ancestor that matches ``value``.
                If no one is found, None is given.
        """
        ancestor = self.parent
        while ancestor is not None:
            if ancestor.value == value:
                return ancestor
            else:
                ancestor = ancestor.parent
        return None

    def search_in_parents_siblings_subtrees(self, value):
        """
        Search a node matching the given `value` in the subtrees nested in
        this node's siblings.

        Args:
            value(string): the research key

        Returns:
            ``TreeNode``: the first node matching the given value.
                If no one is found, None.
        """
        siblings = copy(self.parent.parent.children) \
            if (self.parent and self.parent.parent) else []

        if self.parent in siblings:
            siblings.remove(self.parent)

        while siblings:
            node = siblings.pop()

            if node.value == value:
                return node

            siblings = node.children + siblings

        return None

    def relative_search(self, required_parent):
        """
         This function search the closest parent or sibling matching
         ``_PROPERTIES``. The research depends on ``required_parent``. If it
         is True the node is searched among siblings, otherwise into ancestors.

         Args:
             required_parent(bool): flag used to search in siblings

         Returns:
             ``TreeNode``: the found node, if any, else None.
        """
        if required_parent:
            return self.search_in_parents_siblings_subtrees(_PROPERTIES)
        else:
            return self.get_ancestor(_PROPERTIES)


def _build_tree(obj, node=None, parent_obj=None):

    if isinstance(obj, list):

        for index, item in enumerate(obj):

            if isinstance(item, dict):
                _process_dict_item(item, node, index)

            elif isinstance(item, list):
                _process_list_item(item, node, index)

            else:  # Create child node, implicitly appended itself to parent
                TreeNode(unicode(item), node)

    elif isinstance(obj, bool) \
            or isinstance(obj, int) \
            or isinstance(obj, float):
        # this is a leaf node, append this value to its parent's value
        node.value += ': ' + unicode(obj)

    elif isinstance(obj, string_types):

        if obj in _BLACK_LIST:
            return

        res = parent_obj.get(obj, None)  # a string can be a dictionary key

        if res is None:  # not a dictionary

            if not improve_parent(obj, node):
                node.value += ': ' + unicode(obj)

        else:  # a dictionary

            if isinstance(res, string_types) or isinstance(res, bool) \
                    or isinstance(res, int) or isinstance(res, float):

                node_value = unicode(obj) + ': ' + unicode(res)
                # create a leaf node, connected to the parent one
                TreeNode(node_value, node)

            else:
                child = TreeNode(obj, node)
                _build_tree(res, child, obj)

    else:
        for prop in obj:

            if isinstance(obj[prop], list):
                child = TreeNode(prop, node)
                _build_tree(obj[prop], child, prop)

            elif isinstance(obj[prop], dict):
                child = TreeNode(prop, node)
                _build_tree(obj[prop], child)

            else:
                _build_tree(prop, node, obj)


def _process_list_item(item, parent, intermediate_value=NESTED_ELEMENT_NAME):
    # create an intermediate node and append to it all children nodes
    intermediate = TreeNode(intermediate_value, parent)
    for sub_item in item:
        _build_tree(sub_item, intermediate, item)


def _process_dict_item(item, parent, intermediate_value=NESTED_ELEMENT_NAME):
    # create an intermediate node and append all key children nodes to it
    intermediate = TreeNode(intermediate_value, parent)
    for key in item.keys():

        if key in _BLACK_LIST:
            continue

        child = TreeNode(key, intermediate)
        _build_tree(item[key], child, item)


def improve_parent(obj, node):
    # if a previously nested element had no name and a default one has been
    # assigned to it (e.g. NESTED_ELEMENT_NAME), then the title is used to
    # give a more meaningful name.
    if node.value == _NESTED_ELEMENT_FIELD:

        if node.parent is not None and \
                (node.parent.value == NESTED_ELEMENT_NAME or
                 node.parent.value.isdigit()):
            node.parent.value = unicode(obj)
            node.value = ""
            return True
    return False


if __name__ == '__main__':
    import yaml
    import urllib2

    filename = "temp_file"
    link = "https://raw.githubusercontent.com/inspirehep/inspire-schemas/" \
           "master/inspire_schemas/records/elements/id.yml"
    response = urllib2.urlopen(link)

    with open(filename, 'w') as temp:
        temp.write(response.read())

    with open(filename) as temp:
        schema = yaml.full_load(temp)
        tree = TreeNode("Test_Hep_Schema")
        TreeNode.dict2tree(schema, tree)
        print(tree)

    os.remove(filename)
