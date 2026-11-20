RELAX NG Compact to RELAX NG conversion library
===============================================

.. image:: https://github.com/jombr/rnc2rng/actions/workflows/ci.yml/badge.svg?branch=main
   :target: https://github.com/jombr/rnc2rng/actions/workflows/ci.yml
.. image:: https://coveralls.io/repos/jombr/rnc2rng/badge.svg?branch=main&service=github
   :target: https://coveralls.io/github/jombr/rnc2rng?branch=main

Converts RELAX NG schemata in Compact syntax (`rnc`) to the equivalent schema
in the XML-based default RELAX NG syntax. Dependencies:

- Python 3 (CI tests 3.11, 3.12, 3.13, 3.14, 3.15)
- `rply`_

Older Python versions are not currently tested.

Feedback welcome on `GitHub`_.

.. _GitHub: https://github.com/jombr/rnc2rng
.. _rply: https://pypi.python.org/pypi/rply

History
-------

rnc2rng was originally written by `David Mertz`_ in 2003 and published as part
of a collection of files around RELAX NG `on his site`_ into the Public Domain.
`Hartmut Goebel`_ published it as a package on PyPI to make it easier to access.
It was mirrored on GitHub by `Dustin J. Mitchell`_ in 2010 after he fixed some
bugs. `Timmy Zhu`_ forked his repository and contributed further enhancements.
`Dirkjan Ochtman`_ later made further updates and took over maintainership on
PyPI from Hartmut Goebel. I began contributing in 2024, and Dirkjan later asked
if I was interested in taking over maintainership. I received PyPI maintainership
on November 17, 2026.

I intend to keep the project up to date by testing supported Python versions,
modernizing the code, and implementing remaining parts of the RELAX NG standard.
I'll also try to be responsive to issues and pull requests.

.. _David Mertz: http://www.gnosis.cx/publish/
.. _on his site: http://www.gnosis.cx/download/relax/
.. _Hartmut Goebel: http://www.goebel-consult.de/
.. _Dustin J. Mitchell: http://code.v.igoro.us/
.. _Timmy Zhu: https://github.com/nattofriends
.. _Dirkjan Ochtman: https://dirkjan.ochtman.nl/

How to install
--------------

The usual should work:

.. code-block:: shell

   $ sudo pip install .

Getting started
---------------

.. code-block:: shell

   $ python -m rnc2rng test.rnc > test.rng

License
-------

All of the code is released under MIT License.
