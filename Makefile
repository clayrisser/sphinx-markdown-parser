.POSIX:
export ROOTDIR ?= $(eval ROOTDIR := $(shell git rev-parse --show-toplevel))$(ROOTDIR)
include $(ROOTDIR)/make.mk

.DEFAULT_GOAL := build

ASDF_VERSION ?= v0.18.0
.PHONY: prepare prepare/asdf prepare/cloc
prepare: sudo
	@command -v asdf >/dev/null 2>&1 || $(MAKE) prepare/asdf
	@command -v cloc >/dev/null 2>&1 || $(MAKE) prepare/cloc
	@awk '!/^#/ && NF {print $$1}' .tool-versions | \
		while read t; do asdf plugin add "$$t" 2>/dev/null || true; done
	@rcfile=$$(mktemp); \
		{ asdf install 2>&1; echo $$? >$$rcfile; } | grep --line-buffered -v 'is already installed' || true; \
		rc=$$(cat $$rcfile); rm -f $$rcfile; exit $$rc
	@$(UV) sync
prepare/asdf:
	@command -v brew >/dev/null 2>&1 && brew install asdf || { \
		o=$$(uname | tr A-Z a-z); a=$$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/'); \
		curl -fsSL "https://github.com/asdf-vm/asdf/releases/download/$(ASDF_VERSION)/asdf-$(ASDF_VERSION)-$$o-$$a.tar.gz" \
			| $(SUDO) tar -xz -C /usr/local/bin asdf; \
	}
prepare/cloc:
	@$(PKG_INSTALL) cloc

.PHONY: configure
configure:
	@for cmd in asdf $(UV) $(CLOC); do \
		command -v $$cmd >/dev/null 2>&1 || { echo "$$cmd is missing, run \`make prepare\`"; exit 1; }; \
	done

.PHONY: build
build: configure
	@$(UV) build

COV_ARGS ?= --cov=sphinx_markdown_parser --cov-report=term --cov-report=xml:coverage.xml

.PHONY: test
test: configure
	@$(PYTEST) tests/unit tests/integration $(COV_ARGS)

.PHONY: test/unit
test/unit: configure
	@$(PYTEST) tests/unit $(COV_ARGS)

.PHONY: test/integration
test/integration: configure
	@$(PYTEST) tests/integration $(COV_ARGS)

.PHONY: test/e2e
test/e2e: configure
	@$(PYTEST) tests/e2e

.PHONY: format
format: configure
	@$(BLACK) .

.PHONY: lint
lint: configure
	@$(BLACK) --check .
	@$(BASEDPYRIGHT)

.PHONY: count
count: configure
	@$(CLOC) $$($(GIT) ls-files)

.PHONY: docs docs/%
docs: FORCE
	@$(MAKE) -C docs
docs/%: FORCE
	@$(MAKE) -C docs $*

.PHONY: publish
publish: build
	@$(UV) publish

.PHONY: clean
clean:
	@rm -rf dist coverage.xml .pytest_cache .coverage docs/_build
	@rm -rf $(MAKEDIR)

.PHONY: purge
purge: clean
	@$(GIT) clean -fxd
