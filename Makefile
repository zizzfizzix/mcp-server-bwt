.PHONY: install lint format test build deploy ship_it start mcp_inspector clean

# Git hooks (lefthook.yml) are installed only inside a git checkout, not in tarballs or deploy images.
install:
	uv sync
	if git rev-parse --git-dir >/dev/null 2>&1; then uv run lefthook install; fi

lint:
	uv run mypy --strict mcp_server_bwt/
	uv run ruff check --fix mcp_server_bwt/

format:
	uv run ruff format mcp_server_bwt/

test:
	BING_WEBMASTER_API_KEY=$${BING_WEBMASTER_API_KEY:-dummy} uv run pytest mcp_server_bwt \
		--doctest-modules \
		--junitxml=reports/test-results-$(shell cat .python-version).xml

build: clean
	uv build

deploy: install build

ship_it: build
	git push

start:
	uv run mcp_server_bwt/main.py

mcp_inspector:
	npx @modelcontextprotocol/inspector uv --directory ${PWD} run mcp_server_bwt/main.py

clean:
	rm -rf dist/ build/ reports/ *.egg-info/ *cache
