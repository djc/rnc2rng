RELAX NG Compact to RELAX NG conversion library
===============================================

.. image:: https://travis-ci.org/djc/rnc2rng.svg?branch=master
   :target: https://travis-ci.org/djc/rnc2rng
.. image:: https://img.shields.io/coveralls/djc/rnc2rng.svg?branch=master
   :target: https://coveralls.io/r/djc/rnc2rng?branch=master

Is what it says on the tin. Dependencies:

- Python 2.x (tested mostly with 2.7 so far)
- Python 3.x (currently untested)

Feedback welcome on `GitHub`_.

.. _GitHub: https://github.com/djc/rnc2rng

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

All of the code is released into the Public Domain, unless indicated otherwise
within the file (this is true for PLY's lex.py distributed with this package).
