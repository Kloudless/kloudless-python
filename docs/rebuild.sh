#!/usr/bin/env bash
set -euo pipefail
pandoc -s -r markdown -w rst ../README.md -o source/readme.rst
make html
