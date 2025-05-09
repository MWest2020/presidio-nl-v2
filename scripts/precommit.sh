uv sync
uvx ruff check . --fix
uvx mypy --python-executable $(uv python find) src/api/