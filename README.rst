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
Recently, I (Dirkjan Ochtman) was interested in playing with RELAX NG Compact
and started making further updates. I asked Hartmut for maintainership on PyPI
and received it. While I cannot promise many updates, I should be responsive to
bug reports and (especially!) pull requests.

.. _David Mertz: http://www.gnosis.cx/publish/
.. _on his site: http://www.gnosis.cx/download/relax/
.. _Hartmut Goebel: http://www.goebel-consult.de/
.. _Dustin J. Mitchell: http://code.v.igoro.us/
.. _Timmy Zhu: https://github.com/nattofriends

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
