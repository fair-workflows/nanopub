#!/usr/bin/env bash

set -e

cd docs
make html
python3 -m webbrowser _build/html/index.html