all: usage

.PHONY: usage dist

usage:
	@echo "Targets" >&2
	@echo "  dist - make source distribution under dist/" >&2

dist:
	python setup.py sdist
