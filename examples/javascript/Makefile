ARGS := ""
BUILDDIR := build
CWD := $(shell pwd)
SOURCEDIR := docs
SPHINXOPTS :=
SPHINXPROJ := sooty

.PHONY: all
all: clean

.PHONY: install
install: env

.PHONY: uninstall
uninstall:
	-@rm -rf env >/dev/null || true

.PHONY: reinstall
reinstall: uninstall install

env:
	@virtualenv env
	@env/bin/pip3 install -r requirements.txt

.PHONY: freeze
freeze:
	@env/bin/pip3 freeze > ./requirements.txt

.PHONY: build
build: env clean html man latexpdf

dist: clean install
	@env/bin/python3 setup.py sdist
	@env/bin/python3 setup.py bdist_wheel

.PHONY: publish
publish: dist
	@twine upload dist/*

.PHONY: link
link: install
	@pip3 install -e .

.PHONY: unlink
unlink: install
	@rm -r $(shell find . -name '*.egg-info')

.PHONY: clean
clean:
	-@rm -rf */__pycache__ */*/__pycache__ README.rst dist build \
		example/.tmp *.egg-info >/dev/null || true

.PHONY: serve
serve: env clean html
	@cd $(SOURCEDIR)/$(BUILDDIR)/html && $(CWD)/env/bin/python3 -m http.server

.PHONY: help
help:
	@$(SPHINXBUILD) -M help $(SOURCEDIR) $(BUILDDIR) $(SPHINXOPTS) $(O)

.PHONY: Makefile
%: Makefile
	@cd $(SOURCEDIR) && sphinx-build -M $@ ./ $(BUILDDIR) $(SPHINXOPTS) $(O)
