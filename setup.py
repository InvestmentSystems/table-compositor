# coding: utf-8

# Always prefer setuptools over distutils
from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path
import typing as tp

# https://packaging.python.org/distributing/
# to deploy:
# rm -r dist
# python setup.py sdist
# python setup.py bdist_wheel
# twine register dist/<wheel file>
# twine register dist/<tar file>
# twine upload dist/*

ROOT_DIR_FP = path.abspath(path.dirname(__file__))

def _get_requirements(file_name: str) -> tp.Iterator[str]:
    with open(path.join(ROOT_DIR_FP, file_name)) as f:
        for line in f:
            line = line.strip()
            if line:
                yield line

def get_install_requires() -> tp.Iterator[str]:
    yield from _get_requirements('requirements.txt')

def get_long_description():
    return '''
The table-compositor library provides the API to render data stored in table-like data structures. Currently the library supports rendering data available in a Panda’s DataFrames. The DataFrame layout is used as the table layout(including single and multi hierarchical columns/indices) by the library. The table layout is rendered directly on to an XLSX sheet or to a HTML page. Styling and layout attributes can be used to render colorful XLSX or HTML reports. The library also supports rendering of multiple dataframes into a single XLSX sheet or HTML page. The objective of the library is to be able to use the DataFrame as the API to configure the style and layout properties of the report. Callback functions are provided to customize all styling properties. The nice thing about the callback functions are that the style properties are set on cells indexed with index/column values available in the original dataframe used during rendering.

Code: https://github.com/InvestmentSystems/table-compositor

Docs: http://table-compositor.readthedocs.io

Packages: https://pypi.python.org/pypi/table-compositor

'''

setup(
    name='table-compositor',
    version='1.1.3',

    description='Library to render table-like data structure into XLSX and other formats.',
    long_description=get_long_description(),

    install_requires=list(get_install_requires()),

    url='https://github.com/InvestmentSystems/table-compositor',
    author='Guru Devanla',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        ],

    keywords='pandas excel writer table',
    packages=['table_compositor'],

)
