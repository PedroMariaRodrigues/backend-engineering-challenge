.PHONY: install test clean

# Install package
install: install-requirements
	pip install .

install-requirements:
	pip install -r requirements.txt

# Run tests
test: install-requirements
	pytest -v

# Clean up
clean:
	rm -rf *.egg-info build/ dist/ __pycache__/ .pytest_cache/
	rm -f output.json