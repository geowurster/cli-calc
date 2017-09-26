"""Tests for ``pcalc``."""


import os

import click
from click.testing import CliRunner
import pytest

import pcalc


@pytest.fixture('function')
def invoke():
    """Return a function that pins ``click.testing.CliRunner().invoke()`` to
    ``pcalc.cli``.

    Returns
    -------
    function
    """
    
    def _invoke(cmd, input, args=None):

        """Calls ``click.testing.CliRunner().invoke()`` with ``pcalc.cli``,
        the given parameters, and returns the result.

        Parameter
        ---------
        cmd : str
            Subcommand name.
        input : list
            Values to convert to a block of text and pass to ``stdin``.
        args : list or None, optional
            Additional arguments for the subcommand.

        Returns
        -------
        click.testing.Result
        """

        # Convert float values to text block
        input = os.linesep.join(list(map(str, input)))

        if args is None:
            args = []
        else:
            args = list(args)

        return CliRunner().invoke(pcalc.cli, [cmd] + args, input=input)
    
    return _invoke


@pytest.mark.parametrize("cmd,input,expected", [
    ['min', (4, 2, 8, 1), 1],
    ['max', (4, 2, 8, 1), 8],
    ['mean', (0, 10), 5.0],
    ['median', (1, 2, 3), 2.0],
    ['median', (4, 3, 2, 1), 2.5],
    ['radd', (1, 2, 3), 6.0],
    ['rdiv', (100, 10, 2), 5.0],
    ['rmod', (7, -3), -2.0],
    ['rmul', (2, 2, 2), 8.0],
    ['sum', (1, 2, 3), 6.0],
    ['rsub', (1, 2, 3), -4],
    ['rpow', (2, 2, 2), 16]
])
def test_reducers(invoke, cmd, input, expected):

    """Commands that reduce input values to a single output value."""

    result = invoke(cmd, input)
    assert result.exit_code == 0
    assert float(result.output) == expected


@pytest.mark.parametrize("cmd", [
    'min', 'max', 'mean', 'median', 'mode', 'radd', 'rdiv', 'rmod', 'rmul',
    'sum', 'rsub'])
def test_reducers_single_value(invoke, cmd):

    """Reducers receiving a single value should prdduce only that value."""

    result = invoke(cmd, [-10])
    assert result.exit_code == 0
    assert float(result.output) == -10.0


@pytest.mark.parametrize("input,precision,func", [
    [[1.234567, 3.456789], '0', lambda x: int(round(x, 0))],
    [[1.234567, 3.456789], '1', lambda x: round(x, 1)]
])
def test_round(invoke, input, precision, func):

    """Check rounding to 0 and a specific precision."""

    result = invoke('round', input, args=[precision])
    assert result.exit_code == 0

    expected = map(float, result.output.strip().splitlines())
    expected = map(func, expected)
    expected = map(str, expected)
    expected = os.linesep.join(list(expected))
    assert result.output.strip() == expected.strip()


@pytest.mark.parametrize("cmd,input,args,expected", [
    ['sub', [1.23, -4.56, 6], ['3'], ['-1.77', '-7.56', '3.0']],
    ['add', [1.23, -4.56, 6], ['10'], ['11.23', '5.44', '16.0']],
    ['ceil', [-1.23, 4.0001], [], ['-1', '5']],
    ['floor', [-1.23, 4.0001], [], ['-2', '4']],
    ['div', [-1.23, 100, -000.1], ['3.21'], ['-0.38317001', '31.15264001', '-0.03115001']],
    ['mul', [1, 10, 100], ['--', '-1'], ['-1.0', '-10.0', '-100.0']],
    ['abs', [1, -2, -3.456], [], ['1.0', '2.0', '3.456']],
    ['pow', [1, 2, 4], ['2'], ['1.0', '4.0', '16.0']],
    ['mod', [7, 5], ['3'], ['1', '2']],
    ['eval', [1, 2, 3], ['(v * -1) + 0.1'], ['-0.9', '-1.9', '-2.9']],
    ['eval', [1, 2, 3], ["((v + 1) * 10) % 3"], ['2.0', '0.0', '1.0']]   # Referenced in CLI helped
])
def test_streaming(invoke, cmd, input, args, expected):

    """Commands that stream input values, transform, and emit."""

    result = invoke(cmd, input, args)
    assert result.exit_code == 0

    # Division is harder to check
    if cmd == 'div':
        expected = list(map(float, expected))
        actual = list(map(float, result.output.splitlines()))
        for e, a in zip(expected, actual):
            assert round(e - a, 5) <= 1e-05
    else:
        assert result.output.splitlines() == expected


def test_mode(invoke):
    result = invoke('mode', [1, 5, 8, 10, 10])
    assert result.exit_code == 0
    assert result.output.strip() == '10.0'


def test_mode_exception(invoke):
    result = invoke('mode', [1, 1, 2, 2])
    assert result.exit_code != 0
    assert 'multiple' in result.output.lower()


def test_mod_fmod(invoke):

    """The ``--fmod`` flag changes the output."""

    result = invoke('mod', ['7', '5'], ['3', '--fmod'])
    assert result.exit_code == 0
    assert result.output.splitlines() == ['1', '2']


def test_rmod_fmod(invoke):

    """The ``--fmod`` flag changes the output."""

    result = invoke('rmod', [7, -3], ['--fmod'])
    assert result.exit_code == 0
    assert result.output.strip() == '1'


@pytest.mark.parametrize("cmd", pcalc.cli.commands.keys())
def test_commands_no_data(invoke, cmd):

    """Commands that don't get any data should generally exit with an error
    code, however those that have a required positional argument will exit
    with a slightly different code.  This test is approximate but good enough.
    """
    result = invoke(cmd, [])
    assert result.exit_code != '0'
    if "stdin didn't" not in result.output.lower():
        assert 'missing argument' in result.output.lower()


def test_eval_scope():

    assert pcalc._GLOBAL_EVAL_SCOPE == {
        '__builtin__': None, '__builtins__': None}

    # Verify that most of the CLI commands have a corresponding function in
    # the eval scope
    scope_funcs = []
    commands = pcalc.cli.commands.keys()
    for cmd in commands:
        non_reduce = cmd[1:]
        if cmd.startswith('r') and non_reduce in commands:
            scope_funcs.append(non_reduce)
    scope_funcs.append('math')
    for func in scope_funcs:
        assert func in pcalc._LOCAL_EVAL_SCOPE


def test_evaluate():
    line = 1123456789

    # Expression does not produce int or float
    with pytest.raises(click.ClickException) as e:
        pcalc._evaluate("'word'", {}, {}, line=line)
    assert str(line) in str(e)

    # Expression references something not present in the scope
    with pytest.raises(click.ClickException) as e:
        pcalc._evaluate("whatever", {}, {}, line)
    assert "not present in the scope" in str(e) or "not defined" in str(e)


def test_eval_reduce(invoke):
    result = invoke('eval', [1, 2, 3], ['--reduce', "(a ** 2) + b"])
    assert result.exit_code == 0
    assert result.output.strip() == '12.0'


def test_bad_input(invoke):
    result = invoke('add', ['cannot cast to float'], ['1'])
    assert result.exit_code != 0
    assert 'cast value to float' in result.output


def test_whitespace_input(invoke):
    result = invoke('add', ['', ' ', 1, os.linesep], ['1'])
    assert result.exit_code == 0
    assert result.output.strip() == '2.0'
