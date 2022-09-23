# Development and contribution

## 📥 Install for development

Clone the repository and go in the project folder:

```bash
git clone https://github.com/fair-workflows/nanopub
cd nanopub
```

To install the project for development you can either use [`venv`](https://docs.python.org/3/library/venv.html) to create a virtual environment yourself, or use [`hatch`](https://hatch.pypa.io) to automatically handle virtual environments for you.

## 🐣 Development with Hatch

### Install hatch

Install [Hatch](https://hatch.pypa.io), this will automatically handle virtual environments and make sure all dependencies are installed when you run a script in the project:

```bash
pip install hatch
```

Optionally you can improve `hatch` terminal completion, see the [official documentation](https://hatch.pypa.io/latest/cli/about/#tab-completion) for more details. For ZSH you can run these commands:

```bash
_HATCH_COMPLETE=zsh_source hatch > ~/.hatch-complete.zsh
echo ". ~/.hatch-complete.zsh" >> ~/.zshrc
```

### Test

Run the tests locally:

```bash
hatch run test
```

### Generate docs

```bash
hatch run docs
```

### Format and lint

<!-- The code will be automatically formatted when you commit your changes using `pre-commit`. But you can also run the script to format the code yourself: -->

Run the script to format the code using isort and autoflake:

```bash
hatch run format
```

Or check the code for errors with flake and mypy:

```bash
hatch run lint
```

## 🐍 Development with venv

If you don't want to install `hatch` you can also directly use `venv` and `pip`

### Install with venv

Create the virtual environment in the project folder :

```bash
python3 -m venv .venv
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Install all dependencies required for development:

```bash
pip install -e ".[dev,doc,test]"
```

<!-- You can also enable automated formatting of the code at each commit:

```bash
pre-commit install
``` -->


### Test

Run the tests locally:

```bash
./scripts/test.sh
```

### Generate docs

```bash
./scripts/docs-build.sh
```

### Format and lint

The code will be automatically formatted when you commit your changes using `pre-commit`. But you can also run the script to format the code yourself:

```bash
./scripts/format.sh
```

Or check the code for errors:

```bash
./scripts/lint.sh
```


<!-- ## 🏷️ Publish a new release

[![Publish to PyPI](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/publish.yml/badge.svg)](https://github.com/MaastrichtU-IDS/fair-test/actions/workflows/publish.yml)

1. Increment the `__version__` in `fair_test/__init__.py`
2. Push to GitHub
3. Create a new release on GitHub
4. A GitHub Action workflow will automatically publish the new version to PyPI -->

<!--

## 🐣 Hatch development workflow

Install [Hatch](https://hatch.pypa.io), this will automatically handle virtual environments and make sure all dependencies are installed when you run a script in the project:

```bash
pip install hatch
```

??? note "Optionally you can improve `hatch` terminal completion"

    See the [official documentation](https://hatch.pypa.io/latest/cli/about/#tab-completion) for more details. For ZSH you can run these commands:

    ```bash
    _HATCH_COMPLETE=zsh_source hatch > ~/.hatch-complete.zsh
    echo ". ~/.hatch-complete.zsh" >> ~/.zshrc
    ```

Deploy the FAIR test API defined in the `example` folder to test your changes:

```bash
hatch run dev
```

Format the code automatically:

```bash
hatch run format
```

Automatically check the code for errors:

```bash
hatch run lint
```

Serve the docs locally:

```bash
hatch run docs
```

Run the tests:

```bash
hatch run test
```
-->
