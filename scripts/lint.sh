#!/usr/bin/env bash

set -e
set -x

isort nanopub tests --check-only
flake8 nanopub tests
mypy nanopub
