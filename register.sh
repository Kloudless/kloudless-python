#!/bin/bash
set -euo pipefail
rm -rf dist/
# Make sure setuptools>=38.6.0, twine>=1.11.0 and wheel>= 0.31.0
# See https://stackoverflow.com/questions/26737222/pypi-description-markdown-doesnt-work
python setup.py sdist bdist_wheel --universal
twine upload dist/*
