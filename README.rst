RELAX NG Compact to RELAX NG conversion library
===============================================

Is what it says on the tin. Dependencies:

- Python 2.x (tested mostly with 2.7 so far)
- Python 3.x (currently untested)

Feedback welcome on `GitHub`_.

.. GitHub: https://github.com/djc/rnc2rng

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
