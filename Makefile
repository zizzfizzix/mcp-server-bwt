install:
	chmod +x ./scripts/install.sh
	./scripts/install.sh

lint:
	. .venv/bin/activate; python -m mypy --strict mcp-server-bwt/
	. .venv/bin/activate; python -m ruff check mcp-server-bwt/

format:
	. .venv/bin/activate; python -m ruff format mcp-server-bwt/

test:
	. .venv/bin/activate; python -m pytest mcp-server-bwt \
		--doctest-modules \
		--junitxml=reports/test-results-$(shell cat .python-version).xml

.PHONY: build
build: clean
	. .venv/bin/activate; python -m build

deploy: install build

ship_it: build
	git push

start:
	uv run mcp-server-bwt/main.py

mcp_inspector:
	npx @modelcontextprotocol/inspector uv --directory ${PWD} run mcp-server-bwt/main.py

clean:
	rm -rf dist/ build/ reports/ *.egg-info/ *cache