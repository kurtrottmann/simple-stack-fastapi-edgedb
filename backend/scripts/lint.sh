#!/usr/bin/env bash

mypy app
black app --check
isort --check-only app
flake8 --max-line-length 88 --exclude .git,__pycache__,__init__.py,.mypy_cache,.pytest_cache,venv
