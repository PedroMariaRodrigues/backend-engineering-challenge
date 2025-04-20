.PHONY: install test clean

# Install package
install: install-requirements
	pip install .

install-requirements:
	pip install -r requirements.txt

# Run tests
test: install-requirements test-coverage

test-coverage:
	pytest --cov=src --cov-report=term-missing --cov-report=lcov:./coverage/lcov.info
	
# Clean up
clean:
	rm -rf *.egg-info src/unbabel_cli.egg-info/ build/ dist/ __pycache__/ src/__pycache__/ .pytest_cache/ coverage/
	rm -f output.json .coverage