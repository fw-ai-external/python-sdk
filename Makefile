.PHONY: verify-env preflight

verify-env:
	@bash scripts/verify-env

preflight:
	@bash scripts/preflight

deps-provenance:
	@bash scripts/deps-provenance
