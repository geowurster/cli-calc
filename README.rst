pcalc
=====

Basic math operations for Unix pipes.


.. image:: https://travis-ci.org/geowurster/pcalc.svg?branch=master
    :target: https://travis-ci.org/geowurster/pcalc?branch=master

.. image:: https://coveralls.io/repos/geowurster/pcalc/badge.svg?branch=master
    :target: https://coveralls.io/r/geowurster/pcalc?branch=master


.. code-block:: console

    $ pcalc
    Usage: pcalc [OPTIONS] COMMAND [ARGS]...

      Basic math operations for Unix pipes.

      All commands read from 'stdin' and write to 'stdout'.  Most commands
      stream but a few (like median) hold all values in memory.

      Some commands (typically prefixed with 'r') reduce all input values to a
      single value.  For instance, '$ pcalc add 3' adds 3 to all input values,
      but '$ pcalc radd' adds all the values together like:

          output = 0
          for v in values:
              output = output + v

      For the most part it doesn't matter, but this tool is implemented in
      Python with floating point division enabled when running in Python 2.

    Options:
      --help  Show this message and exit.

    Commands:
      abs     Compute absolute value.
      add     Add a constant to values.
      ceil    Ceiling values.
      div     Divide values by a constant.
      floor   Floor values.
      mean    Compute mean.
      median  Compute median.
      mod     Modulo values by a single divisor.
      mode    Compute mode.
      mul     Multiply values by a constant.
      pow     Exponentiation of values by a constant.
      radd    Reduce by addition.
      rdiv    Reduce by division.
      rmod    Reduce by modulo.
      rmul    Reduce by multiplication.
      round   Round values.
      rsub    Reduce by subtraction.
      sub     Subtract a constant from values.
      sum     Compute sum.


Developing
==========

.. code-block:: console

    $ git clone https://github.com/geowurster/pcalc.git
    $ cd tpcalc
    $ pip install -e .\[dev\]
    $ py.test --cov pcalc --cov-report term-missing


License
=======

See ``LICENSE.txt``


Changelog
=========

See ``CHANGES.md``
