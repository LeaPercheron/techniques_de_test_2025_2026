test:
\tpytest

unit_test:
\tpytest -m "not performance"

perf_test:
\tpytest -m "performance"

coverage:
\tcoverage run -m pytest
\tcoverage report

lint:
\truff check .

doc:
\tpdoc3 --html --output-dir docs src
