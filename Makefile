.PHONY: all develop test lint clean doc format build
.PHONY: clean clean-test coverage dist docs install lint lint/flake8

# The package name
PKG=pywire


all: build test lint

#
# Build
#
build:
	python src/prescrypt/tools/gen_stdlibjs.py


#
# Setup
#

## Install development dependencies and pre-commit hook (env must be already activated)
develop: activate-pre-commit configure-git

activate-pre-commit:
	@echo "--> Activating pre-commit hook"
	pre-commit install

configure-git:
	@echo "--> Configuring git"
	git config branch.autosetuprebase always


#
# testing & checking
#

## Run python tests fast
test:
	@echo "--> Running Python tests in random order"
	pytest

## Run python tests fast
test-fast:
	@echo "--> Running Python tests"
	pytest --ff -x
	@echo ""

## Run python tests with coverage
test-cov:
	@echo "--> Running Python tests with coverage"
	pytest --cov prescrypt --cov-config=pyproject.toml

## Lint / check typing
lint:
	ruff check


#
# Formatting
#

## Format / beautify code
format:
	ruff format src tests/a_unit tests/b_integration

#
# Everything else
#
.PHONY: help clean clean-test tidy update-deps publish

help:
	@inv help-make

## Cleanup repository
clean: clean-test
	rm -f **/*.pyc
	find . -type d -empty -delete
	rm -rf *.egg-info *.egg .coverage .eggs .cache .mypy_cache .pyre \
		.pytest_cache .pytest .DS_Store  docs/_build docs/cache docs/tmp \
		dist build pip-wheel-metadata junit-*.xml htmlcov coverage.xml \
		.ruff_cache
	cd demos && make clean

## Cleanup tests artifacts
clean-test: ## remove test and coverage artifacts
	rm -fr .tox/ .nox/
	rm -f .coverage
	rm -fr htmlcov/
	find . -name .pytest_cache -exec rm -fr {} +
	rm -f tests/*/programs/*.js

## Cleanup harder
tidy: clean
	rm -rf .nox
	rm -rf node_modules
	rm -rf instance

## Update dependencies
update-deps:
	uv sync --all-groups --all-extras -U
	pre-commit autoupdate

## Publish to PyPI
publish: clean
	git push --tags
	uv build
	twine upload dist/*
