# Lint the code
lint:
  uv run ruff check

# Format the code
format:
  uv run ruff check --fix
  uv run ruff format

# Run the server
run host="localhost":
  uv run uvicorn app.main:app --host {{host}} --reload

# Run tests
test: lint && cov
  uv run pytest -s -x --cov=app -vv

# Generate HTML coverage
cov:
  uv run coverage html
