.PHONY: lint typecheck test smoke-test

lint:
	ruff check . --fix
	ruff format .

typecheck:
	mypy --strict services/ shared/

# Example: make test SERVICE=auth
test:
	@if [ -z "$(SERVICE)" ]; then \
		echo "Usage: make test SERVICE=<service_name>"; \
		exit 1; \
	fi
	pytest services/$(SERVICE)/

smoke-test:
	pytest infra/docker/tests/test_compose_boot.py -v
