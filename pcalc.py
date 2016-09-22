"""Basic math operations for Unix pipes."""


from __future__ import division

from collections import Counter
import itertools as it
import math
import operator as op
import sys

import click


if sys.version_info.major == 2:  # pragma: no cover
    map = it.imap
    filter = it.ifilter
else:  # pragma: no cover
    from functools import reduce


__version__ = '1.0'
__author__ = 'Kevin Wurster'
__email__ = 'wursterk@gmail.com'
__source__ = 'https://github.com/geowurster/pcalc'
__license__ = '''
New BSD License

Copyright (c) 2016, Kevin D. Wurster
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* The names of pcalc or its contributors may not be used to endorse or
  promote products derived from this software without specific prior written
  permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''


def _values():
    """Read values from ``stdin`` and cast to ``float``."""
    stream = click.get_text_stream('stdin')
    stream = filter(op.methodcaller('strip'), stream)
    stream = filter(None, stream)
    stream = map(float, stream)

    try:
        first = next(stream)
    except StopIteration:
        raise click.ClickException("stdin didn't get any data.")

    return it.chain([first], stream)


def _cb_fmod(ctx, param, value):

    """Click callback to translate the ``--fmod`` flag directly to a modulo
    function.
    """

    if value:
        func = math.fmod
    else:
        func = op.mod

    return lambda a, b: int(func(a, b))


constant_arg = click.argument('constant', type=click.FLOAT, required=True)
fmod_opt = click.option(
    '--fmod', 'mod_func', is_flag=True, callback=_cb_fmod,
    help="Use Python's 'math.fmod()' function, which is better suited for "
         "floats, instead of the modulo operator.  Causes output to be a "
         "float instead of integer.")


@click.group()
def cli():

    """Basic math operations for Unix pipes.

    When working with a negative positional argument: '$ pcalc mul -- -1'

    All commands read from 'stdin' and write to 'stdout'.  Most commands
    stream but a few (like median) hold all values in memory.  Empty or all
    whitespace lines are skipped.

    Some commands (typically prefixed with 'r') reduce all input values to a
    single value.  For instance, '$ pcalc add 3' adds 3 to all input values,
    but '$ pcalc radd' adds all the values together like:

    \b
        output = 0
        for v in values:
            output = output + v

    For the most part it doesn't matter, but this tool is implemented in
    Python with floating point division enabled when running in Python 2.
    """


@cli.command(name='sum')
def sum_():

    """Compute sum."""

    click.echo(reduce(op.add, _values()))


@cli.command(name='round')
@click.argument('precision', type=click.INT, required=True)
def round_(precision):

    """Round values.

    Precision 0 also casts to 'int'.
    """

    if precision == 0:
        def func(x, _):
            return int(round(x, 0))
    else:
        func = round

    for v in _values():
        click.echo(func(v, precision))


@cli.command()
def ceil():

    """Ceiling values."""

    for v in _values():
        click.echo(int(math.ceil(v)))  # Value not cast to int on Python 2


@cli.command()
def floor():

    """Floor values."""

    for v in _values():
        click.echo(int(math.floor(v)))  # Value not cast to int on Python 2


@cli.command()
@click.argument('denominator', type=click.FLOAT, required=True)
@fmod_opt
def mod(denominator, mod_func):

    """Modulo values by a single divisor.

    Output is dictated by the '--fmod' flag.
    """

    for v in _values():
        click.echo(mod_func(v, denominator))


@cli.command()
@fmod_opt
def rmod(mod_func):

    """Reduce by modulo.

    Output is dictated by the '--fmod' flag.
    """

    click.echo(reduce(mod_func, _values()))


@cli.command()
@constant_arg
def add(constant):

    """Add a constant to values."""

    for v in _values():
        click.echo(v + constant)


@cli.command()
@constant_arg
def sub(constant):

    """Subtract a constant from values."""

    for v in _values():
        click.echo(v - constant)


@cli.command()
@constant_arg
def mul(constant):

    """Multiply values by a constant."""

    for v in _values():
        click.echo(v * constant)


@cli.command()
@constant_arg
def div(constant):

    """Divide values by a constant.

    Floating point division.
    """

    for v in _values():
        click.echo(v / constant)


@cli.command()
def radd():

    """Reduce by addition."""

    click.echo(reduce(op.add, _values()))


@cli.command()
def rsub():
    """Reduce by subtraction."""

    click.echo(reduce(op.sub, _values()))


@cli.command()
def rmul():

    """Reduce by multiplication."""

    click.echo(reduce(op.mul, _values()))


@cli.command()
def rdiv():

    """Reduce by division."""

    click.echo(reduce(op.truediv, _values()))


@cli.command(name='abs')
def abs_():

    """Compute absolute value."""

    for v in _values():
        click.echo(abs(v))


@cli.command()
def median():

    """Compute median."""

    values = sorted(_values())
    if len(values) % 2:
        click.echo(values[int((len(values) - 1) / 2)])
    else:
        stop = int(len(values) / 2) + 1
        start = stop - 2
        middle = values[start:stop]
        click.echo(sum(middle) / 2)


@cli.command()
def mean():

    """Compute mean."""

    values = tuple(_values())
    click.echo(sum(values) / len(values))


@cli.command()
def mode():

    """Compute mode.

    Formatting multiple modes is a little ambiguous in the context of pcalc,
    so this condition triggers an error."""

    count = Counter(_values())

    # If the two most common elements have the same count then there are at
    # least 2 modes.
    if len(count) > 1 and len({c[-1] for c in count.most_common(2)}) == 1:
        raise click.ClickException("Multiple mode's - unsure how to format.")
    else:
        click.echo(count.most_common(1)[0][0])


@cli.command(name='pow')
@constant_arg
def pow_(constant):

    """Exponentiation of values by a constant."""

    for v in _values():
        click.echo(pow(v, constant))
