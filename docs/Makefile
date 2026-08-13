.POSIX:
ROOTDIR ?= $(eval ROOTDIR := $(shell git rev-parse --show-toplevel))$(ROOTDIR)
include $(ROOTDIR)/make.mk

.DEFAULT_GOAL := build

.PHONY: build
build:
	@$(SPHINX_BUILD) -b html . _build/html

.PHONY: clean
clean:
	@rm -rf _build
