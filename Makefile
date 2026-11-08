.PHONY: verify-env format lint test

verify-env:
	@echo "== build context =="
	@python3 -V; id -un; hostname; pwd
	@echo "== dependency install verification (documented in CONTRIBUTING.md) =="
	@python3 -m pip install --no-cache-dir --disable-pip-version-check -r requirements.txt || true
	@pip install --no-cache-dir --no-build-isolation --no-deps -e . || true
	@echo "== done =="

format:
	@bash scripts/format

lint:
	@bash scripts/lint

test:
	@bash scripts/test
