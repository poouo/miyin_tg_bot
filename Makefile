PYTHON ?= python3

.PHONY: run install lint

install:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

run:
	$(PYTHON) -m apps.runner.main

