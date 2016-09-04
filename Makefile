test:
	PYTHONPATH=. pytest -q --ignore env test/*

.PHONY: test
