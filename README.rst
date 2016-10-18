|Build Status| |AppVeyor Build Status| |Coverage Status| |Code Health| |license|

socman
======

socman is a society membership and attendance tracking library for Python,
which tracks members in a SQLite3 database.

Planned Features
----------------
At present the main goal is to stabilise current functionality and refactor
existing code. Major targets for the first release (v0.1) are:

* [X] support OSX and Windows for automated testing
* [X] use py.test for testing
* [X] add functional tests using real database files
* [ ] simplify logic in MemberDatabase
* [ ] publish the library on PyPI

Longer term goals (for inclusion by version 1.0) include:

* tracking event metadata in text files
* CLI and GUI frontends with support for custom society branding

Installation
------------

This library is in development. Clone the repository if you want to try
it.  With version 0.2 the library will be made available via PyPI.

Maintainers
-----------

This repository is maintained by `Alex Thorne <https://alexthorne.net/>`
(`email <mailto:alex@alexthorne.net.>`). Please get in touch with feature
requests, bug reports, etc (and if you have any improvements please make
a pull request!)


.. |Build Status| image:: https://travis-ci.org/NullInfinity/socman.svg?branch=master
   :target: https://travis-ci.org/NullInfinity/socman
.. |AppVeyor Build Status| image:: https://ci.appveyor.com/api/projects/status/github/NullInfinity/socman?branch=master&svg=true
   :target: https://ci.appveyor.com/project/NullInfinity/socman
.. |Coverage Status| image:: https://coveralls.io/repos/github/NullInfinity/socman/badge.svg?branch=master
   :target: https://coveralls.io/github/NullInfinity/socman?branch=master
.. |Code Health| image:: https://landscape.io/github/NullInfinity/socman/master/landscape.svg?style=flat
   :target: https://landscape.io/github/NullInfinity/socman/master
.. |license| image:: https://img.shields.io/github/license/NullInfinity/socman.svg
   :target: https://github.com/NullInfinity/socman/blob/master/LICENSE.txt
