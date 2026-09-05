PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest
PHITS_TEST_WORKERS ?= $(shell nproc 2>/dev/null || getconf _NPROCESSORS_ONLN 2>/dev/null || echo 1)

.PHONY: test

test:
	@test -n "$$PHITSPATH" || (echo "PHITSPATH must point to the PHITS installation" >&2; exit 2)
	PHITS_TEST_WORKERS=$(PHITS_TEST_WORKERS) $(PYTEST) test_angel2root.py
