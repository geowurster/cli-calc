#!/usr/bin/env python


"""Setup script for ``pcalc``."""


import itertools as it
import os

from setuptools import setup


with open('README.rst') as f:
    readme = f.read().strip()


def parse_dunder_line(string):

    """Take a line like:

        "__version__ = '0.0.8'"

    and turn it into a tuple:

        ('__version__', '0.0.8')

    Not very fault tolerant.
    """

    # Split the line and remove outside quotes
    variable, value = (s.strip() for s in string.split('=')[:2])
    value = value[1:-1].strip()
    return variable, value


with open('pcalc.py') as f:
    dunders = dict(map(
        parse_dunder_line,
        filter(lambda l: l.strip().startswith('__'), f.readlines())))
    version = dunders['__version__']
    author = dunders['__author__']
    email = dunders['__email__']
    source = dunders['__source__']


extras_require = {
    'dev': [
        'pytest>=3',
        'pytest-cov',
        'coveralls',
    ],
}
extras_require['all'] = list(it.chain.from_iterable(extras_require.values()))


setup(
    name='pcalc',
    author=author,
    author_email=email,
    classifiers=[
        'Topic :: Utilities',
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Topic :: Text Processing',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    description="Basic math operations for Unix pipes.",
    include_package_data=True,
    install_requires=['click'],
    extras_require=extras_require,
    keywords='command line CLI math unix pipe',
    license="New BSD",
    long_description=readme,
    py_modules=['pcalc'],
    url=source,
    version=version,
    zip_safe=True,
    entry_points="""
        [console_scripts]
        pcalc=pcalc:cli
    """
)
