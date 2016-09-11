"""
test_db.py contains the functional tests involving a real database file.

Tests on socman should be run with `python -m pytest`. To run just these tests,
run `pytest tests/test_db.py`.


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
# pylint: disable=redefined-outer-name
import pytest
import sqlite3

import socman


@pytest.fixture
def db_file(tmpdir):
    """Create test DB file with sample entries."""
    db_path = os.path.join(tmpdir, 'test.db')
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    cursor.execute("""INSERT INTO users """
                   """(firstName,lastName,barcode,college,"""
                   """datejoined,created_at,updated_at,last_attended)""")

    conn.commit()
    conn.close()

    yield dp_path
