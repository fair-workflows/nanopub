#!/usr/bin/env bash

set -e
set -x

pytest -s --cov=nanopub --cov=tests --cov-report=term-missing:skip-covered tests ${@}
