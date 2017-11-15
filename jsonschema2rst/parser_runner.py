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
This module lets you execute ``jsonschema2rst`` parser recursively on a given
folder.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import os
import sys

from jsonschema2rst.indexer import create_master_index, index, write_index_file
from jsonschema2rst.parser import schema2rst
from jsonschema2rst.rst_writer import (JSON_EXTENSION, RST_EXTENSION,
                                       YML_EXTENSION, change_extension)


def run_parser(
    input_path,
    output_path,
    excluded_key="uniqueItems,additionalProperties,$schema",
    yaml_only=False,
):
    """
    This function copies the needed resources into the ``output_path``,
    runs the ``jsonschema2rst`` recursively on ``input_path`` parsing all yaml
    schemas, and create an index listing and linking all those files.

    Args:
        input_path(string): the folder where yaml schemas are located.

        output_path(string): the folder where all resources and
            restructured-text generated files will be placed. Note that,
            if the folder already exists, it is deleted, otherwise a new one
            is created.

        excluded_key(string): csv containing schema's keywords to ignore

    Raises:
        OSError: if ``output_path``is not accessible (Permission denied)
    """

    if not os.path.exists(input_path):
        raise IOError('Wrong path: {}. Program will exit'.format(input_path))

    output_path = os.path.abspath(output_path)
    input_files = os.walk(input_path)

    processed_files = []

    for input_file in input_files:
        root, dirs, files = input_file

        # create, if not exists, the sub folder where rst file will be written
        output_folder = _get_output_folder(output_path, input_path, root)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # write it on the FS this sub-folder content's index
        index_content = index(root)
        write_index_file(output_folder, index_content)

        for name in files:

            if (
                name.endswith(YML_EXTENSION) or
                (not yaml_only and name.endswith(JSON_EXTENSION))
            ):

                # check if a file with same name has been already parsed
                abs_name = change_extension(name, '')
                if abs_name in processed_files:
                    continue

                file_name = os.path.join(root, name)

                with open(file_name) as schema:
                    rst_content = schema2rst(schema, excluded_key)

                    output = os.path.join(output_folder, _get_rst_name(name))

                    with open(output, 'wb') as rst_out:
                        rst_out.write(rst_content.encode('utf-8'))

                processed_files.append(abs_name)
                print(abs_name.ljust(40) + 'OK')

    create_master_index(output_path)
    print('Index created.\n')


def _get_rst_name(name):
    return change_extension(name, RST_EXTENSION)


def _get_output_folder(out_dir, input_root, current_path):
    path_diff = os.path.relpath(current_path, input_root)
    return os.path.join(out_dir, path_diff)


def cli(arguments=None):

    cli_parser = argparse.ArgumentParser(description=run_parser.__doc__)

    cli_parser.add_argument('schemas_folder',
                            help='The folder where schemas are placed.')

    cli_parser.add_argument('rst_output_folder',
                            help='The folder where RST files will be written.')

    cli_parser.add_argument('--excluded-key',
                            help='List of keywords in, csv format, that will '
                                 'be excluded from  the schema parsing '
                                 'process. By default, its value is '
                                 'uniqueItems,additionalProperties,$schema.',
                            default='uniqueItems,'
                                    'additionalProperties,'
                                    '$schema'
                            )

    args = cli_parser.parse_args(arguments)

    src = args.schemas_folder
    out = args.rst_output_folder
    excluded_key = args.excluded_key

    run_parser(src, out, excluded_key)


if __name__ == '__main__':
    cli(sys.argv[1:])
