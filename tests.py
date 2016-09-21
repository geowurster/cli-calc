"""Tests for ``pcalc``."""


import os

from click.testing import CliRunner
import pytest

import pcalc


@pytest.fixture('function')
def runner():
    return CliRunner()


@pytest.mark.parametrize("cmd,input,expected", [
    ['mean', (0, 10), 5.0],
    ['median', (1, 2, 3), 2.0],
    ['median', (4, 3, 2, 1), 2.5],
    ['radd', (1, 2, 3), 6.0],
    ['rdiv', (100, 10, 2), 5.0],
    ['rmod', (7, -3), 1.0],
    ['rmul', (2, 2, 2), 8.0],
    ['sum', (1, 2, 3), 6.0],
    ['rsub', (1, 2, 3), -4]
])
def test_reducers(runner, cmd, input, expected):

    """Commands that reduce input values to a single output value."""

    result = runner.invoke(
        pcalc.cli, [cmd], input=os.linesep.join(map(str, input)))
    assert result.exit_code == 0
    assert float(result.output) == expected


@pytest.mark.parametrize("cmd", [
    'mean', 'median', 'median', 'radd', 'rdiv', 'rmod', 'rmul', 'sum', 'rsub'])
def test_reducers_single_value(runner, cmd):

    """Reducers receiving a single value should prdduce only that value."""

    result = runner.invoke(pcalc.cli, [cmd], input='-10{}'.format(os.linesep))
    assert result.exit_code == 0
    assert float(result.output) == -10.0


def test_pow(runner):
    pass


def test_add(runner):
    pass


def test_ceil(runner):
    pass


def test_div(runner):
    pass


def test_floor(runner):
    pass


def test_mod(runner):
    pass


def test_mode(runner):
    pass


def test_mul(runner):
    pass


def test_round(runner):
    pass


def test_sub(runner):
    pass
