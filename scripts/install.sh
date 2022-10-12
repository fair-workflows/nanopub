#!/usr/bin/env bash

set -e
set -x

echo "Make sure you use a virtual environment when working in development"
echo "python -m venv .venv"
echo "source .venv/bin/activate"

pip install -e ".[dev,test,doc]"

pre-commit install