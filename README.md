![Build Status](https://github.com/fair-workflows/nanopub/workflows/Python%20application/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/fair-workflows/nanopub/badge.svg?branch=main)](https://coveralls.io/github/fair-workflows/nanopub?branch=main)
[![PyPI version](https://badge.fury.io/py/nanopub.svg)](https://badge.fury.io/py/nanopub)
[![fair-software.eu](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B-yellow)](https://fair-software.eu)


# nanopub
The nanopub python library provides a client for searching, publishing and modifying nanopublications.

# Setup
Install using pip:
```
pip install nanopub
```

To publish to the nanopub server you need to setup RSA keys. This allows the nanopub server to identify you.
```
make_nanopub_keys
```
