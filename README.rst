RELAX NG Compact to RELAX NG conversion library
===============================================

.. image:: https://travis-ci.org/djc/rnc2rng.svg?branch=master
   :target: https://travis-ci.org/djc/rnc2rng
.. image:: https://coveralls.io/repos/djc/rnc2rng/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/djc/rnc2rng?branch=master

Converts RELAX NG schemata in Compact syntax (`rnc`) to the equivalent schema
in the XML-based default RELAX NG syntax. Dependencies:

- Python 2.x (tested with 2.6, 2.7)
- Python 3.x (tested with 3.3, 3.4, 3.5, 3.7, 3.8)
- `rply`_

Feedback welcome on `GitHub`_.

.. _GitHub: https://github.com/djc/rnc2rng
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

All of the code is released into the Public Domain.
