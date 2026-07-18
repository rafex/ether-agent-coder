.PHONY: check test smoke hooks-install clean

check:
	@./helpers/scripts/shell/secrets-check.sh

test:
	@./smoke-test/run.sh

smoke: test

hooks-install:
	@./helpers/scripts/shell/install-hooks.sh

clean:
	@find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name target -o -name node_modules \) -prune -exec rm -rf {} +
