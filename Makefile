install:
	chmod +x ./scripts/install.sh
	./scripts/install.sh

lint:
	. .venv/bin/activate; python -m mypy --strict mcp_server_bwt/
	. .venv/bin/activate; python -m ruff check mcp_server_bwt/

format:
	. .venv/bin/activate; python -m ruff format mcp_server_bwt/

test:
	. .venv/bin/activate; python -m pytest mcp_server_bwt \
		--doctest-modules \
		--junitxml=reports/test-results-$(shell cat .python-version).xml

.PHONY: build
build: clean
	. .venv/bin/activate; python -m build

deploy: install build

ship_it: build
	git push

start:
	uv run mcp_server_bwt/main.py

mcp_inspector:
	npx @modelcontextprotocol/inspector uv --directory ${PWD} run mcp_server_bwt/main.py

clean:
	rm -rf dist/ build/ reports/ *.egg-info/ *cache