# Always prefer setuptools over distutils
from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path

# https://packaging.python.org/distributing/
# to deploy:
# rm -r dist
# python setup.py sdist
# python setup.py bdist_wheel
# twine register dist/<wheel file>
# twine register dist/<tar file>
# twine upload dist/*

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='table-compositor',
    version='1.0.1',

    description='Library to render table-like data structure into XLSX and other formats.',
    long_description=long_description,

    install_requires=['pandas', 'openpyxl'],

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
