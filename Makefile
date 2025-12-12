test:
	pytest

unit_test:
	pytest -m "not performance"

perf_test:
	pytest -m "performance"

coverage:
	coverage run -m pytest
	coverage report

lint:
	ruff check .

doc:
	pdoc3 --html --output-dir docs src
