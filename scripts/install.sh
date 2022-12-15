#!/usr/bin/env bash

set -e

echo "Make sure you use a virtual environment when working in development:"
echo "python -m venv .venv"
echo "source .venv/bin/activate"
echo
read -p "Hit [Enter] to continue, or [Ctrl+C] to cancel" -n 1 -r
echo

pip install -e ".[dev,test,doc]"

pre-commit install
