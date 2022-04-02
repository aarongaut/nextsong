VERSION = $(shell dev-bin/rl python -c 'from nextsong import __version__ as v; print(v, end="")')

all: dist
.PHONY: all

install: dist
	python3 -m pip install --force-reinstall dist/nextsong-$(VERSION)-py3-none-any.whl
.PHONY: install

publish: test dist
	python3 -m twine upload dist/*
.PHONY: publish
.NOTPARALLEL: publish

clean:
	rm -rf dist
	rm -rf src/*.egg-info
	find src -name __pycache__ -type d -prune -exec rm -r {} ';'
	find tests -name __pycache__ -type d -prune -exec rm -r {} ';'
	find tests -name artifacts -type d -prune -exec rm -r {} ';'
.PHONY: clean

format fmt:
	black .
.PHONY: format fmt

test:
	./dev-bin/rl runtests tests/cases
.PHONY: test

push: test
	git remote | xargs -n1 git push

dist: $(shell find src) LICENSE pyproject.toml README.md setup.cfg
	rm -f dist/*
	python3 -m build

