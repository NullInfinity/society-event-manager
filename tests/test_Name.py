"""
test_Name.py contains the automated tests for socman.Name.

Tests on socman should be run with `python -m pytest`. To run just these tests,
run `pytest tests/test_Name.py`.


The MIT License (MIT)

Copyright (c) 2016 Alexander Thorne

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import pytest

import socman


@pytest.mark.parametrize("name,expected", [
    # empty name
    (socman.Name(), {
        'names': [],
        'first': '',
        'middle': '',
        'last': '',
        'given': '',
        'full': ''
        }),
    # first and last name
    (socman.Name('Ted', 'Rogers'), {
        'names': ['Ted', 'Rogers'],
        'first':  'Ted',
        'middle': '',
        'last': 'Rogers',
        'given': 'Ted',
        'full': 'Ted Rogers'
        }),
    # last name only
    (socman.Name('Rogers'), {
        'names': ['Rogers'],
        'first': '',
        'middle': '',
        'last': 'Rogers',
        'given': '',
        'full': 'Rogers'
        }),
    # first name only
    (socman.Name('Ted', None), {
        'names': ['Ted', None],
        'first': 'Ted',
        'middle': '',
        'last': '',
        'given': 'Ted',
        'full': 'Ted'
        }),
    # middle name only
    (socman.Name(None, 'Bobson', None), {
        'names': [None, 'Bobson', None],
        'first': '',
        'middle': 'Bobson',
        'last': '',
        'given': 'Bobson',
        'full': 'Bobson'
        }),
    # first, middle, last
    (socman.Name('Ted', 'Bobson', 'Rogers'), {
        'names': ['Ted', 'Bobson', 'Rogers'],
        'first': 'Ted',
        'middle': 'Bobson',
        'last': 'Rogers',
        'given': 'Ted Bobson',
        'full': 'Ted Bobson Rogers'
        }),
    # first, middle, middle, last
    (socman.Name('Ted', 'Bobson', 'Rickerton', 'Rogers'), {
        'names': ['Ted', 'Bobson', 'Rickerton', 'Rogers'],
        'first': 'Ted',
        'middle': 'Bobson Rickerton',
        'last': 'Rogers',
        'given': 'Ted Bobson Rickerton',
        'full': 'Ted Bobson Rickerton Rogers'
        })
])
def test_name_strings(name, expected):
    assert name.names == expected['names']
    assert name.first() == expected['first']
    assert name.middle() == expected['middle']
    assert name.last() == expected['last']
    assert name.given() == expected['given']
    assert name.full() == expected['full']


@pytest.mark.parametrize("name", [
    socman.Name('Rogers'),
    socman.Name('Ted', 'Rogers'),
    socman.Name('Ted', None)
    ])
def test_name_true(name):
    assert name


@pytest.mark.parametrize("name", [
    socman.Name(),
    socman.Name(None),
    #TODO uncomment these (currently failing tests) and make them pass
    #socman.Name(''),
    #socman.Name('', ''),
    #socman.Name('', None)
    ])
def test_falsiness(name):
    assert not name


@pytest.mark.parametrize("name1,name2", [
    (socman.Name(), socman.Name()),
    (socman.Name('Rogers'), socman.Name('Rogers')),
    (socman.Name('Ted', 'Rogers'), socman.Name('Ted', 'Rogers')),
    (socman.Name('Ted', None), socman.Name('Ted', None))
    ])
def test_equality(name1, name2):
    assert name1 == name2


@pytest.mark.parametrize("name1,name2", [
    (socman.Name(), socman.Name('Rogers')),
    (socman.Name(), socman.Name('Ted', 'Rogers')),
    (socman.Name('Rogers'), socman.Name('Ted', 'Rogers')),
    (socman.Name('Elliot', None), socman.Name('Elliot')),
    (socman.Name('Ted', 'Rogers'), 4),
    (socman.Name('Ted', 'Rogers'), 'test')
    ])
def test_inequality(name1, name2):
    assert name1 != name2


def test_name_none():
    """If a name contains only None names it should be the same as an
    empty name."""
    assert socman.Name() == socman.Name(None)
    assert socman.Name() == socman.Name(None, None)


@pytest.mark.parametrize("sep", ['_', '.', 'sep', ' sep '])
def test_custom_separator(sep):
    name = socman.Name('Ted', 'Bobson', 'Rogers', sep=sep)

    assert name.given() == 'Ted' + sep + 'Bobson'
    assert name.full() == 'Ted' + sep + 'Bobson' + sep + 'Rogers'
