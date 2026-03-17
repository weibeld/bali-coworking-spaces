.PHONY: run run-interactive run-all help

# Variables
PYTHON = ./.venv/bin/python3
ORCHESTRATOR = ./orchestrator.py
CONFIG = ../config.yaml
# Use a shell variable for LIMIT, defaulting to 3
LIMIT ?= 3

help:
	@echo "Datapilot Engine Commands (run from 'engine' folder):"
	@echo "  make run             - Run with default settings (limit 3)"
	@echo "  make run-interactive - Run with interaction and full tracing (limit 3)"
	@echo "  make run-all         - Run for all discovered candidates"
	@echo ""
	@echo "Options:"
	@echo "  make run LIMIT=10    - Run with a custom limit"

run:
	$(PYTHON) $(ORCHESTRATOR) --limit $(LIMIT) --config $(CONFIG)

run-interactive:
	$(PYTHON) $(ORCHESTRATOR) --limit $(LIMIT) --interactive --config $(CONFIG)

run-all:
	$(PYTHON) $(ORCHESTRATOR) --limit 100 --config $(CONFIG)
