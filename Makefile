all: sdist bdist_wheel

sdist:
	python setup.py sdist

bdist_wheel:
	python setup.py bdist_wheel

upload_build:
	python -m twine upload --repository pypi dist/* --verbose

.PHONY : sdist bdist_wheel