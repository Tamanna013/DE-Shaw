.PHONY: migration migrate

migration:
	@if [ -z "$(name)" ]; then \
		echo "Error: name is required. Usage: make migration name=\"<name>\""; \
		exit 1; \
	fi
	alembic revision --autogenerate -m "$(name)"

migrate:
	alembic upgrade head
