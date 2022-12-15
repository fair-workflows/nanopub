#!/usr/bin/env bash

set -e

isort nanopub tests --check-only
flake8 nanopub tests
mypy nanopub
# black nanopub tests --check
