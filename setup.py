#!/usr/bin/env python

from setuptools import setup, find_packages
import re

def read(fname):
    contents = ''
    with open(fname) as f:
        contents = f.read()
    return contents

def version():
    text = read('kloudless/version.py')
    matches = re.findall("('|\")(\S+)('|\")", text)
    return matches[0][1]

install_requires=[
    'requests>=1.0',
    'python-dateutil',
    ]
setup(
    name='kloudless',
    packages=find_packages(),
    include_package_data=True,
    author='Kloudless',
    author_email='hello@kloudless.com',
    version=version(),
    description = "Python library for the Kloudless API",
    long_description=read('README.md'),
    url='https://developers.kloudless.com/',
    install_requires=install_requires,
    license='MIT',
    classifiers=[
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        ],
    package_data={'': ['LICENSE']},
    zip_safe=False,
    )
