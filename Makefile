#!/usr/bin/make
#
all: run

.PHONY: buildout
buildout:
	virtualenv -p python2 .
	./bin/pip install -r requirements.txt
	bin/buildout

run: bin/instance
	bin/instance fg

test: bin/test
	rm -fr htmlcov
	bin/test

cleanall:
	rm -fr bin develop-eggs htmlcov include .installed.cfg lib .mr.developer.cfg parts downloads eggs pyvenv.cfg
