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
	rm -f tags
	find src -name __pycache__ -type d -prune -exec rm -r {} ';'
	find tests -name __pycache__ -type d -prune -exec rm -r {} ';'
	find tests -name artifacts -type d -prune -exec rm -r {} ';'
.PHONY: clean

format fmt:
	black --line-length $(shell ./dev-bin/rl printenv BLACK_LINE_LENGTH) .
.PHONY: format fmt

test:
	./dev-bin/rl runtests tests/cases
.PHONY: test

push: test
	git remote | xargs -n1 git push
	git remote | xargs -n1 git push --tags
.PHONY: push

dist: $(shell find src) LICENSE pyproject.toml README.md setup.cfg
	rm -f dist/*
	python3 -m build

tags: $(shell find src)
	ctags $(shell find src/nextsong -iname "*.py")
