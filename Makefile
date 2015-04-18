clean: clean-build clean-pyc

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

doc:
	autodoc > docs/format.rst
	cd docs; make html

release: clean
	python setup.py sdist upload

lint:
	flake8 psas_packet
