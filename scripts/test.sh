#!/usr/bin/env bash

set -e
set -x

# bash ./scripts/lint.sh

pytest -s --cov=nanopub --cov-report=term-missing:skip-covered ${@}
