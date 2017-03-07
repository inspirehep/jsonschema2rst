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

import pytest

from jsonschema2rst.rst_utils import (bold, bullet, container, emphasize,
                                      explicit_link, kv_field, line, literal,
                                      make_title)


def test_emphasize_string():
    expected = '*foo* '
    result = emphasize('foo')
    assert result == expected


def test_emphasize_integer():
    expected = '*2* '
    result = emphasize('2')
    assert result == expected


def test_emphasize_bool():
    expected = '*True* '
    result = emphasize(True)
    assert result == expected


def test_emphasize_none():
    expected = '*None* '
    result = emphasize(None)
    assert result == expected


def test_explicit_link_equals_values():
    expected = '`foo <foo>`_'
    result = explicit_link('foo')
    assert result == expected


def test_explicit_link_different_values():
    expected = '`bar <foo>`_'
    result = explicit_link('foo', 'bar')
    assert result == expected


def test_explicit_link_integers():
    expected = '`1 <1>`_'
    result = explicit_link(1)
    assert result == expected


def test_explicit_link_bool():
    expected = '`True <True>`_'
    result = explicit_link(True)
    assert result == expected


def test_explicit_link_none():
    expected = '`None <None>`_'
    result = explicit_link(None)
    assert result == expected


def test_bold():
    expected = '**foo** '
    result = bold('foo')
    assert result == expected


def test_bold_integer():
    expected = '**1** '
    result = bold(1)
    assert result == expected


def test_bold_bool():
    expected = '**True** '
    result = bold(True)
    assert result == expected


def test_bold_none():
    expected = '**None** '
    result = bold(None)
    assert result == expected


def test_literal_one_value():
    expected = '``foo``'
    result = literal('foo')
    assert result == expected


def test_literal_list():
    expected = '``foo``, ``bar``'
    result = literal('foo, bar')
    assert result == expected


def test_literal_none():
    expected = ''
    result = literal(None)
    assert result == expected


def test_kv_field():
    expected = ':foo: ``bar``'
    result = kv_field('foo', 'bar')
    assert result == expected


def test_kv_field_with_bool():
    expected = ':True: ``False``'
    result = kv_field(True, False)
    assert result == expected


def test_kv_field_with_integers():
    expected = ':1: ``2``'
    result = kv_field(1, 2)
    assert result == expected


def test_kv_field_with_none():
    expected = ':None: ``None``'
    result = kv_field(None, None)
    assert result == expected


def test_kv_field_with_backtick():
    expected = ':Ref: :ref:`my_reference`'
    result = kv_field('Ref', ':ref:`my_reference`')
    assert result == expected


def test_bullet():
    expected = '- foo'
    result = bullet('foo')
    assert result == expected


def test_bullet_integers():
    expected = '- 12'
    result = bullet(12)
    assert result == expected


def test_bullet_bool():
    expected = '- True'
    result = bullet(True)
    assert result == expected


def test_bullet_none():
    expected = '- None'
    result = bullet(None)
    assert result == expected


def test_line_ok():
    expected = "======"
    result = line(0, 'foobar')
    assert result == expected


def test_line_big_level():
    expected = "......"
    result = line(999999999999999, 'foobar')
    assert result == expected


def test_line_negative_level():
    expected = "......"
    result = line(-3, 'foobar')
    assert result == expected


def test_container():
    expected = '.. container:: css_class\n\n foo bar'
    result = container('foo bar', 'css_class')
    assert result == expected


def test_container_null_value_expected_exception():
    with pytest.raises(TypeError):
        container(None, 'css_class')


def test_container_empty_string_expected_exception():
    with pytest.raises(TypeError):
        container('', 'css_class')


def test_container_null_css_():
    expected = '.. container:: \n\n foo'
    result = container('foo')
    assert result == expected


def test_container_empty_css_():
    expected = '.. container:: \n\n foo'
    result = container('foo', '')
    assert result == expected


def test_make_title():
    expected = 'foo\n==='
    result = make_title('foo', 0)
    assert result == expected
