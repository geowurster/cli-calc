"""Basic math operations for Unix pipes."""


from __future__ import division

from collections import Counter
import itertools as it
import math
import operator as op
import sys

import click


if sys.version_info.major == 2:  # pragma: no cover
    numeric_types = (int, float, long)
    map = it.imap
    filter = it.ifilter

    def _echo(*args, **kwargs):  # pragma: no cover
        """Python 2 does not properly handle broken pipes, which usually means
        that the next command in the chain did not completely consume its stdin.
        Catch that condition and do nothing.
        """
        
        try:
            click.echo(*args, **kwargs)
        except IOError as e:
            if 'broken pipe' in e.lower():
                pass
            else:
                raise e

else:  # pragma: no cover
    from functools import reduce
    _echo = click.echo
    numeric_types = (int, float)


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


def _cast_float(v):
    try:
        return float(v)
    except ValueError:
        raise click.ClickException(
            "Could not cast value to float: {}".format(v))


def _values():
    """Read values from ``stdin`` and cast to ``float``."""
    stream = click.get_text_stream('stdin')
    stream = filter(op.methodcaller('strip'), stream)
    stream = filter(None, stream)
    stream = map(_cast_float, stream)

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


# Re-usable click arguments/options
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

    _echo(reduce(op.add, _values()))


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
        _echo(func(v, precision))


@cli.command()
def ceil():

    """Ceiling values."""

    for v in _values():
        _echo(int(math.ceil(v)))  # Value not cast to int on Python 2


@cli.command()
def floor():

    """Floor values."""

    for v in _values():
        _echo(int(math.floor(v)))  # Value not cast to int on Python 2


@cli.command()
@click.argument('denominator', type=click.FLOAT, required=True)
@fmod_opt
def mod(denominator, mod_func):

    """Modulo values by a single divisor.

    Output is dictated by the '--fmod' flag.
    """

    for v in _values():
        _echo(mod_func(v, denominator))


@cli.command()
@fmod_opt
def rmod(mod_func):

    """Reduce by modulo.

    Output is dictated by the '--fmod' flag.
    """

    _echo(reduce(mod_func, _values()))


@cli.command()
@constant_arg
def add(constant):

    """Add a constant to values."""

    for v in _values():
        _echo(v + constant)


@cli.command()
@constant_arg
def sub(constant):

    """Subtract a constant from values."""

    for v in _values():
        _echo(v - constant)


@cli.command()
@constant_arg
def mul(constant):

    """Multiply values by a constant."""

    for v in _values():
        _echo(v * constant)


@cli.command()
@constant_arg
def div(constant):

    """Divide values by a constant.

    Floating point division.
    """

    for v in _values():
        _echo(v / constant)


@cli.command()
def radd():

    """Reduce by addition."""

    _echo(reduce(op.add, _values()))


@cli.command()
def rsub():
    """Reduce by subtraction."""

    _echo(reduce(op.sub, _values()))


@cli.command()
def rmul():

    """Reduce by multiplication."""

    _echo(reduce(op.mul, _values()))


@cli.command()
def rdiv():

    """Reduce by division."""

    _echo(reduce(op.truediv, _values()))


@cli.command(name='abs')
def abs_():

    """Compute absolute value."""

    for v in _values():
        _echo(abs(v))


@cli.command(name='min')
def min_():

    """Compute min."""

    _echo(min(_values()))


@cli.command(name='max')
def max_():

    """Compute max."""

    _echo(max(_values()))


@cli.command()
def median():

    """Compute median."""

    values = sorted(_values())
    if len(values) % 2:
        _echo(values[int((len(values) - 1) / 2)])
    else:
        stop = int(len(values) / 2) + 1
        start = stop - 2
        middle = values[start:stop]
        _echo(sum(middle) / 2)


@cli.command()
def mean():

    """Compute mean."""

    values = tuple(_values())
    _echo(sum(values) / len(values))


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
        _echo(count.most_common(1)[0][0])


@cli.command(name='pow')
@constant_arg
def pow_(constant):

    """Exponentiation of values by a constant."""

    for v in _values():
        _echo(pow(v, constant))


@cli.command()
def rpow():

    """Reduce by pow."""

    _echo(reduce(pow, _values()))


def _evaluate(expression, local_scope, global_scope, line):

    """Wrap ``eval()`` to validate output and raise better errors.  The
     ``line`` argument is used to provide some context on failure.

    Parameters
    ----------
    expression : str
        For ``eval()``.
    local_scope : dict
        For ``eval()``.
    global_scope : dict
        For ``eval()``.
    line : int
        Used to provide context when raising an exception.

    Raises
    ------
    click.ClickException

    Returns
    -------
    int or float
        From ``eval()``.
    """

    try:
        result = eval(expression, local_scope, global_scope)

        # Make sure we only
        if isinstance(result, numeric_types):
            return result
        else:
            raise click.ClickException(
                "Expression failed when processing line {} - output must "
                "be an int or float, not {}: {}".format(line, type(result), result))

    # Raise better errors when the expression evaluation fails
    except Exception as e:

        if isinstance(e, (TypeError, NameError)):
            msg = str(e).lower()
            if ('nonetype' in msg and 'object is not subscriptable' in msg) \
                    or 'not defined' in msg:
                raise click.ClickException(
                    "Expression attempted to access an object not present in "
                    "the scope.")
        raise click.ClickException(str(e))


# Easier to test out here
_GLOBAL_EVAL_SCOPE = {
    '__builtin__': None,
    '__builtins__': None,
}
_LOCAL_EVAL_SCOPE = _GLOBAL_EVAL_SCOPE.copy()
_LOCAL_EVAL_SCOPE.update(
    abs=op.abs,
    add=op.add,
    ceil=math.ceil,
    div=op.truediv,
    floor=math.floor,
    fmod=math.fmod,
    math=math,
    mod=op.mod,
    mul=op.mul,
    pow=op.pow,
    round=round,
    sub=op.sub)


@cli.command(name='eval')
@click.argument('expression')
@click.option(
    '--reduce', 'reduce_vals', is_flag=True,
    help="Expression is a reduce function.  The same scope is available, but "
         "the expression must reduce values 'a' and 'b' to a single integer "
         "or float.")
def eval_(expression, reduce_vals):

    """Evaluate a Python expression.

    By default the expression is evaluated in a streaming manner against each
    input value, but the '--reduce' flag can be used to reduce all the input
    values to a single output.

    Uses Python's 'eval()' with a limited scope including all the non-reduce
    functions that are available in the CLI (supplied by the 'operator'
    module) and the standard Python operators.  In addition, the 'math' module
    is available and 'fmod' is directly available.  Expressions are generally
    easier to read and write if they stick to the builtin operators.

    All input values are float but the output can be integer or float.
    Floating point division is enabled when running in Python 2.  Expressions
    are like a 'lambda' in that they do not use the 'return' statement
    explicitly.

    Python developers are often advised not to use 'eval()' because it is a
    security risk, which is true, but only if unknown code is being passed
    to 'eval()' or if the user intentionally writes an expression to do
    something negative.  In reality it is absolutely a bad idea to 'eval()'
    unknown code, so don't do that, but its also a bad idea to intentionally
    write an expression to do something negative, so don't do that either!
    In this case 'eval()' provides a transparent way for users to do their
    own more complex math, so as long as you, the person reading this, doesn't
    do anything bad on purpose, you're find.  Don't freak out.  It's just like
    being dropped inside a for loop.

    When streaming each value is placed in the variable 'v', and when reducing
    variables 'a' and 'b' are available.

    Add 1 to each value, multiply by 10, and then modulo the result by 3:

    \b
        $ pcalc eval "((v + 1) * 10) % 3"

    Reduce values by squaring the first and adding the second:

    \b
        $ pcalc eval --reduce "(a ** 2) + b"
    """

    global_scope = _GLOBAL_EVAL_SCOPE.copy()
    local_scope = _LOCAL_EVAL_SCOPE.copy()

    # Normal streaming
    if not reduce_vals:

        for idx, v in enumerate(_values(), 1):
            local_scope.update(v=v)
            _echo(_evaluate(expression, local_scope, global_scope, line=idx))

    # Reduce operation, but eval()'s workflow doesn't match reduce()'s
    else:

        values = _values()

        # Initial 'a' value
        result = next(values)

        # Loop doesn't execute if we only get 1 line and we need idx
        # in this case to potentially raise a more helpful error
        for idx, v in enumerate(values, 1):

            local_scope.update(
                a=result,
                b=v)

            result = _evaluate(expression, local_scope, global_scope, idx)

        _echo(result)
