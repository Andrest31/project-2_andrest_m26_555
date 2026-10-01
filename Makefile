install:
	poetry install

run:
	poetry run database

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	poetry run pip install dist/*.whl

lint:
	poetry run ruff check .