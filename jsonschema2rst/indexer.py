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
This module helps creating indexes contents and files for restructured-text
parsed files..
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

from jsonschema2rst.rst_utils import NL2, TAB, make_title
from jsonschema2rst.rst_writer import (JSON_EXTENSION, NL, YML_EXTENSION,
                                       change_extension)

INDEX_FILE_NAME = 'index.rst'


INDEX_HEADER = '''
.. toctree::
\t:titlesonly:
'''


MASTER_INDEX_TITLE = "Schemas Documentation"


def index(input_path):
    """
    Create the content of an index page, listing all files in the given path.
    Sub folders are not visited.

    Args:
        input_path(string): the path where all files to convert are located.

    Returns:
         string: the index page content.
    """
    content = make_title(os.path.basename(input_path), 0)
    content += INDEX_HEADER

    processed_files = []

    for file_name in sorted(os.listdir(input_path)):
        if file_name.endswith(YML_EXTENSION) or \
                file_name.endswith(JSON_EXTENSION):
            # remove the extension
            abs_name = change_extension(file_name, '')
            if abs_name not in processed_files:
                content += NL + TAB + change_extension(file_name, '')
                processed_files.append(abs_name)

    return content


def create_master_index(root_path):
    """
    Create the main index containing inner indexes. It searches for every
    ``index.rst`` in all sub folders and add it to its toctree. The list of
    all indexes files found is written in a new
    ``index.rst``

    Args:
        root_path(string): the starting path from which recursively searches
            indexes.
    """
    content = make_title(MASTER_INDEX_TITLE, 0)
    content += INDEX_HEADER + NL

    files = os.walk(root_path)

    for input_file in files:
        root, dirs, files = input_file

        rel_path = os.path.relpath(root, root_path)

        files.sort()

        for name in files:
            if "__pycache__" in rel_path:
                continue

            if (rel_path == ".") ^ (name == INDEX_FILE_NAME):
                content += TAB \
                        + os.path.join(rel_path, change_extension(name, '')) \
                        + NL2

    write_index_file(root_path, content)


def write_index_file(out_path, content):
    """
    Create a new file called ``INDEX_FILE_NAME`` in the given path, and writes
    the ``content`` in it.

    Args:
        out_path(string): the path were the index file will be created
        content(string): the file content to write down.
    """
    with open(os.path.join(out_path, INDEX_FILE_NAME), 'w') as index_page:
        index_page.write(content)
