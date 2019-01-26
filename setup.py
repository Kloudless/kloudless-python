#!/usr/bin/env python

from setuptools import setup, find_packages
import re
import os
from os.path import join as opj

curdir = os.path.dirname(os.path.realpath(__file__))


def read(fname):
    with open(fname) as f:
        contents = f.read()
    return contents


package_name = 'kloudless'


def version():
    text = read(opj(curdir, package_name, 'version.py'))
    matches = re.findall(r"('|\")(\S+)('|\")", text)
    return matches[0][1]


def long_description():
    return read(opj(curdir, 'README.md'))


install_requires = [
    'requests>=1.0',
    'python-dateutil',
    'six'
]

if __name__ == '__main__':
    setup(
        name=package_name,
        packages=find_packages(),
        author='Kloudless',
        author_email='hello@kloudless.com',
        version=version(),
        description="Python library for the Kloudless API",
        long_description=long_description(),
        long_description_content_type="text/markdown",
        url='https://github.com/kloudless/kloudless-python/',
        install_requires=install_requires,
        license='MIT',
        classifiers=[
            'Programming Language :: Python',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
        ],
        zip_safe=False,
        )
