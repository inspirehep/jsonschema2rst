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

from jsonschema2rst.rst_writer import change_extension


def test_change_extension():
    expected = 'foobar.yml'
    result = change_extension('foobar.json', '.yml')
    assert result == expected


def test_change_extension_harder():
    expected = 'foobar.yml.yml'
    result = change_extension('foobar.yml.json', '.yml')
    assert result == expected


def test_change_extension_remove_ext():
    expected = 'foobar'
    result = change_extension('foobar.txt', '')
    assert result == expected


def test_change_extension_no_ext():
    expected = 'foobar.txt'
    result = change_extension('foobar', '.txt')
    assert result == expected
