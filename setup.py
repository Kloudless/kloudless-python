#!/usr/bin/env python

from setuptools import setup, find_packages
import kloudless

def read(fname):
    contents = ''
    with open(fname) as f:
        contents = f.read()
    return contents


install_requires=[
    'requests',
    'python-dateutil',
    ]
setup(
    name='kloudless',
    packages=find_packages(),
    include_package_data=True,
    author='Kloudless',
    author_email='hello@kloudless.com',
    version=kloudless.__version__,
    description = "Python library for Kloudless",
    long_description=read('README.md'),
    url='https://developers.kloudless.com/',
    install_requires=install_requires,
    license='MIT',
    classifiers=[
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "License :: OSI Approved :: MIT License",
        ],
    package_data={'': ['LICENSE']},
    zip_safe=False,
    entry_points=entry_points
    )
