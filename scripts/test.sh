#!/usr/bin/env bash

set -e
set -x

pytest -s --cov=nanopub --cov-report=term-missing:skip-covered tests ${@}
