#!/usr/bin/env bash

set -e
set -x

bash ./scripts/format.sh

bash ./scripts/lint.sh

bash ./scripts/test.sh
