#!/bin/bash

pandoc -s -r markdown -w rst README.md -o README.rst
rm -rf dist/
python setup.py sdist
twine upload dist/*
