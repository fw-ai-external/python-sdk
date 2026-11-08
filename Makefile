.PHONY: verify-env format lint test

verify-env:
	@chmod +x ./bin/verify-env 2>/dev/null || true
	@./bin/verify-env

format:
	@bash scripts/format

lint:
	@bash scripts/lint

test:
	@bash scripts/test
