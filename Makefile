CFLAGS = -g -Wall

all: binary-slice

clean: clean-build clean-pyc
	-rm -f binary-slice

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +

test:
	python setup.py test

test-all:
	tox

release: clean
	python setup.py sdist upload

lint:
	flake8 psas_packet
