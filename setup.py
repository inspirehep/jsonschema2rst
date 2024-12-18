# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE-SCHEMAS.
# Copyright (C) 2016 CERN.
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

"""jsonschema2rst and related tools bundle."""

from setuptools import find_packages, setup

URL = 'https://github.com/inspirehep/jsonschema2rst'
readme = open('README.rst').read()

tests_require = [
    "coverage>=4.0",
    "isort<5.0.0",
    "pytest-cache>=1.0",
    "pytest-cov>=1.8.0",
    "pytest-pep8>=1.0.6",
    "pytest<6.0.0",
    "mock>=2.0.0",
]

install_requires = [
    'pyyaml>=6.0,<7.0',
    'six',
]

setup_requires = [
    'autosemver==0.5.5',
]

extras_require = {
    'tests': tests_require,
}

setup(
    name='jsonschema2rst',
    author='CERN',
    author_email='admin@inspirehep.net',
    description='Parser for yaml/json schemas to rst',
    license='GPLv2',
    keywords='jsonschema yaml rst parser documentation',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    setup_requires=setup_requires,
    extras_require=extras_require,
    long_description=readme,
    url=URL,
    autosemver=True,
    package_data={'': ['CHANGELOG', 'AUTHORS', 'README.rst', 'resources/*']},
    include_package_data=True,
    entry_points={
          'console_scripts': [
              'jsonschema2rst = jsonschema2rst.parser_runner:cli'
          ]
      },
)
