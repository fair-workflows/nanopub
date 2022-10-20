#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place nanopub tests --exclude=__init__.py
isort nanopub tests

pre-commit run --all-files || true

# black nanopub tests
