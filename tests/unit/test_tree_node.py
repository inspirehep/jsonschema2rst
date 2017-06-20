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

from jsonschema2rst.tree_node import TreeNode, improve_parent


def test_init_with_string():
    expected = "foo"
    node = TreeNode(expected)
    result = node.value

    assert result == expected
    assert node.lvl == 0
    assert node.children == []
    assert node.parent is None


def test_init_with_int():
    expected = "1"
    result = TreeNode(1).value

    assert result == expected


def test_init_with_none():
    expected = 'None'
    result = TreeNode(None).value

    assert result == expected


def test_init_with_integer():
    expected = '1'
    result = TreeNode(1).value

    assert result == expected


def test_init_without_val():
    expected = ''
    result = TreeNode().value

    assert result == expected


def test_is_leaf_true():
    leaf = TreeNode('leaf')

    assert leaf.is_leaf() is True


def test_is_leaf_false():
    parent = TreeNode('inner')
    TreeNode('leaf', parent)

    assert parent.is_leaf() is False


def test_str():
    pass


def test_eq_true():
    tree1 = TreeNode(1)
    sub_tree_1_1 = TreeNode(2, tree1)
    sub_tree_1_2 = TreeNode(3, tree1)

    tree2 = TreeNode(1)
    sub_tree_2_1 = TreeNode(2, tree2)
    sub_tree_2_2 = TreeNode(3, tree2)

    assert tree1 == tree2


def test_eq_false():
    tree1 = TreeNode(1)
    sub_tree_1_1 = TreeNode(2, tree1)
    sub_tree_1_2 = TreeNode(4, tree1)

    tree2 = TreeNode(1)
    sub_tree_2_1 = TreeNode(2, tree2)
    sub_tree_2_2 = TreeNode(3, tree2)

    assert not tree1 == tree2


def test_ancestors_empty_list_expected():
    expected = []
    result = TreeNode().ancestors()

    assert result == expected


def test_ancestors():
    tree = TreeNode(0)
    child_1 = TreeNode(1, tree)
    child_2 = TreeNode(2, child_1)
    child_3 = TreeNode(3, child_2)

    expected = [tree, child_1, child_2]

    result = child_3.ancestors()

    assert result == expected


def test_next_id():
    expected = [1, 2, 3]

    TreeNode._ID = 0    # reset the id counter
    result = []
    for i in range(3):
        result.append(TreeNode._next_id())

    assert result == expected


def test_dict2tree_none_dict_gives_just_a_node():
    expected = TreeNode('Root')
    result = TreeNode.dict2tree(None, None)

    assert result == expected


def test_dict2tree_none_parent_gives_tree_with_standard_root_value():
    expected = TreeNode('Root')
    result = TreeNode.dict2tree({}, None)

    assert result == expected


def test_dict2tree_with_none_input_on_two_entries_gives_tree_with_two_child():
    expected = TreeNode('Root')
    child_1 = TreeNode('value1: foo', expected)
    child_2 = TreeNode('value2: bar', expected)

    dictionary = {
        'value1': 'foo',
        'value2': 'bar'
    }

    result = TreeNode.dict2tree(dictionary, None)

    assert result == expected


def test_dict2tree_two_entries_appends_two_child_to_given_tree():
    expected = TreeNode()
    child_1 = TreeNode('value1: foo', expected)
    child_2 = TreeNode('value2: bar', expected)

    dictionary = {
        'value1': 'foo',
        'value2': 'bar'
    }

    result = TreeNode()
    result = TreeNode.dict2tree(dictionary, result)

    assert result == expected


def test_dict2tree_simple_dict():
    expected = TreeNode('Root')
    child_1 = TreeNode('value1: foo', expected)
    child_2 = TreeNode('value2: bar', expected)

    dictionary = {
        'value1': 'foo',
        'value2': 'bar'
    }

    result = TreeNode.dict2tree(dictionary, None)

    assert result == expected


def test_dict2tree_simple_dict_with_integers():
    expected = TreeNode('Root')
    child_1 = TreeNode('value1: 1', expected)
    child_2 = TreeNode('value2: 2', expected)

    dictionary = {
        'value1': 1,
        'value2': 2
    }

    result = TreeNode.dict2tree(dictionary, None)

    assert result == expected


def test_dict2tree_dict_with_list():
    expected = TreeNode('Root')
    child_1 = TreeNode('list', expected)
    child_intermediate = TreeNode(0, child_1)
    child_1_1 = TreeNode('value: foo', child_intermediate)

    dictionary = {
        'list': [{'value': 'foo'}]
    }

    result = TreeNode.dict2tree(dictionary, None)

    assert result == expected


def test_dict2tree_list_of_list():
    expected = TreeNode('Root')
    child_1 = TreeNode('list', expected)
    child_intermediate = TreeNode(0, child_1)
    child_1_1 = TreeNode('value: foo', child_intermediate)

    dictionary = {
        'list': [[{'value': 'foo'}]]
    }

    result = TreeNode.dict2tree(dictionary, None)

    assert result == expected


def test_dict2tree_dict_with_dict():
    expected = TreeNode('Root')
    child_1 = TreeNode('dict1', expected)
    child_2 = TreeNode('dict2', child_1)
    child_3 = TreeNode('value: foo', child_2)

    dictionary = {
        'dict1': {
            'dict2': {
                'value': 'foo'
            }
        }
    }

    result = TreeNode.dict2tree(dictionary, None)

    assert result == expected


def test_improve_parent_node_title():
    expected = "Great Title!"

    root = TreeNode(0)
    child = TreeNode('title', root)

    improve_parent('Great Title!', child)
    assert root.value == expected


def test_improve_parent_node_not_title():
    expected = "Great Title!"

    root = TreeNode('something')
    child = TreeNode('title', root)

    improve_parent('Great Title!', child)
    assert root.value != expected
