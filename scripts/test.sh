#!/usr/bin/env bash

set -e

pytest --cov=nanopub --cov-report=term-missing:skip-covered ${@}
