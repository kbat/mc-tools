PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest
PHITS_TEST_WORKERS ?= 8

.PHONY: test

test:
	@test -n "$$PHITSPATH" || (echo "PHITSPATH must point to the PHITS installation" >&2; exit 2)
	PHITS_TEST_WORKERS=$(PHITS_TEST_WORKERS) $(PYTEST) -q test_angel2root.py
