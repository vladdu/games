# List the recipes
default:
    @just --list

# Set up the virtualenv with dependencies
sync:
    uv sync

# Play; extra args go to the game, e.g. `just play --game gomoku`
play *args:
    uv run games {{args}}

# Run the tests; pass a module to run just that, e.g. `just test tests.test_grid`
test *args:
    uv run python -m unittest -v {{args}}

# Lint
lint:
    uv run ruff check .

# Format
fmt:
    uv run ruff format .

# Lint and test
check: lint test

# Run the tests, skipping the slow ones (marked @slow in tests/)
test-fast *args:
    FAST=1 uv run python -m unittest {{args}}
