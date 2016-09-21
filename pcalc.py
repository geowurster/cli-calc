"""Basic math operations for Unix pipes."""


from __future__ import division

from collections import Counter
import itertools as it
import math
import operator as op
import sys

import click


if sys.version_info.major == 2:
    map = it.imap
    filter = it.ifilter
else:
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
    return map(float, click.get_text_stream('stdin'))


constant_arg = click.argument('constant', type=click.FLOAT, required=True)


@click.group()
def cli():

    """Basic math operations for Unix pipes.

    All commands read from 'stdin' and write to 'stdout'.  Most commands
    stream but a few (like median) hold all values in memory.

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
        def func(x):
            return int(round(x, 0))
    else:
        func = round

    for v in _values():
        click.echo(func(v, precision))


@cli.command()
def ceil():

    """Ceiling values."""

    for v in _values():
        click.echo(math.ceil(v))


@cli.command()
def floor():

    """Floor values."""

    for v in _values():
        click.echo(math.floor(v))


@cli.command()
@click.argument('divisor', type=click.FLOAT, required=True)
def mod(divisor):

    """Modulo values by a single divisor.

    Result has the same sign as the divisor.  Uses Python's 'math.fmod()'.
    """

    for v in _values():
        click.echo(math.fmod(v, divisor))


@cli.command()
def rmod():

    """Reduce by modulo.

    Result has the same sign as the divisor.  Uses Python's 'math.fmod()'.
    """

    click.echo(reduce(math.fmod, _values()))


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
def abs_(values):

    """Compute absolute value."""

    for v in values:
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

    mode = Counter(_values()).most_common()
    if len(mode) == 1:
        click.echo(mode[0][0])
    else:
        raise click.Abort("Multiple mode's - unsure how to format.")


@cli.command(name='pow')
@constant_arg
def pow_(constant):

    """Exponentiation of values by a constant."""

    for v in _values():
        click.echo(pow(v, constant))


if __name__ == '__main__':
    cli()
