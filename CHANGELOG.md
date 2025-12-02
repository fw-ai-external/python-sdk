# Changelog

## 1.0.0-alpha.1 (2025-12-02)

Full Changelog: [v0.0.1...v1.0.0-alpha.1](https://github.com/fw-ai-external/python-sdk/compare/v0.0.1...v1.0.0-alpha.1)

### Features

* Add documentation about streaming usage in generated README for Python SDK ([25bbecc](https://github.com/fw-ai-external/python-sdk/commit/25bbecca2a3623f7890e91b61d0fba0991f360c1))
* Add DPO Job REST API to docs + SDK ([556a15c](https://github.com/fw-ai-external/python-sdk/commit/556a15c268996b230440a7c5983f585e658ba745))
* Add GetBillingSummary to REST API + SDK ([f818671](https://github.com/fw-ai-external/python-sdk/commit/f81867100b13d463c3365994b3765a788ee3821f))
* add secrets REST APIs to docs + SDK ([8f43098](https://github.com/fw-ai-external/python-sdk/commit/8f4309898ae6f0c186500f7022c9921e0f8741c5))
* add shared models deployed_model / deployed_model_ref ([8cee0c5](https://github.com/fw-ai-external/python-sdk/commit/8cee0c5823f2d6717a75513743e6f0268fab995f))
* **api:** api update ([8719875](https://github.com/fw-ai-external/python-sdk/commit/87198753f559f94e6ec4271ea18e89eb5ff0282e))
* **api:** api update ([93d7d7a](https://github.com/fw-ai-external/python-sdk/commit/93d7d7a49ed1d243e5c40f4a012b1f7af635e916))
* **api:** api update ([3b8eb54](https://github.com/fw-ai-external/python-sdk/commit/3b8eb54d48cf18860e9f511b6284f4b80915a59e))
* **api:** api update ([ce0f8d1](https://github.com/fw-ai-external/python-sdk/commit/ce0f8d1d6fa91311307ec25b866502f5b4071c90))
* **api:** api update ([8c7147e](https://github.com/fw-ai-external/python-sdk/commit/8c7147e33cb08df91dad91af93bd58c6a0434d29))
* **api:** manual updates ([e4ff837](https://github.com/fw-ai-external/python-sdk/commit/e4ff837ab72241ab686d71dfe9f7cb31bf3c1398))
* **client:** use aiohttp as default with 1000 connection pool size ([7dc10ac](https://github.com/fw-ai-external/python-sdk/commit/7dc10acc5a66b6f1ea13e03a7f585f1e34f63565))
* Ensure ordering between Docs / SDK is the same ([3aad15c](https://github.com/fw-ai-external/python-sdk/commit/3aad15c5fe2206ccfe9f126cdb2c03cbeb2864c1))
* Export OpenAPI from Text Completion ([271c181](https://github.com/fw-ai-external/python-sdk/commit/271c18114f964f90376e581afca70b8816829b38))
* Generate SDKs from stainless using OpenAPI specs ([1c69ee2](https://github.com/fw-ai-external/python-sdk/commit/1c69ee295a8fa16d734d44960848685ec66cf816))
* Publish Python SDK: 1.0.0-alpha.1 ([7fa189b](https://github.com/fw-ai-external/python-sdk/commit/7fa189b687acc70357b80f8b67aec09c027f33c5))


### Bug Fixes

* compat with Python 3.14 ([f896c0b](https://github.com/fw-ai-external/python-sdk/commit/f896c0b99b0bf48b194b813e74dac19aac4d2d24))
* **compat:** update signatures of `model_dump` and `model_dump_json` for Pydantic v1 ([e7405ba](https://github.com/fw-ai-external/python-sdk/commit/e7405ba9ff2308eddb61f9fcc5e04822f51aa369))
* ensure streams are always closed ([1cb89c3](https://github.com/fw-ai-external/python-sdk/commit/1cb89c3ba17fb255cf1e21a26c8954eded33e4b2))
* properly close aiohttp connector when AsyncFireworks client is garbage collected ([f079210](https://github.com/fw-ai-external/python-sdk/commit/f079210d10d251394cee7f0d2ba5d14550869fa7))
* **tests:** use httpx client in tests for respx_mock compatibility ([62e6f21](https://github.com/fw-ai-external/python-sdk/commit/62e6f21ef0e51b60551c0639600a6c3d07e5e341))


### Chores

* add Python 3.14 classifier and testing ([5436aef](https://github.com/fw-ai-external/python-sdk/commit/5436aefe9f3483f9551a8537da1c9e3c014bbb76))
* **deps:** mypy 1.18.1 has a regression, pin to 1.17 ([695f55f](https://github.com/fw-ai-external/python-sdk/commit/695f55fedacbee84e60f53a0cd001dbc028b8971))
* **package:** drop Python 3.8 support ([76b2ede](https://github.com/fw-ai-external/python-sdk/commit/76b2ede6c409f753f6c70e869198d7512dc0c12a))
* update SDK settings ([b649187](https://github.com/fw-ai-external/python-sdk/commit/b64918770170505b03e37fa1b344d9b1a56839b5))


### Documentation

* **readme:** add documentation for reasoning_content in thinking models ([8de75aa](https://github.com/fw-ai-external/python-sdk/commit/8de75aa9070ca695e0a832177536d387971073d0))
* **readme:** update HTTP client documentation to reflect aiohttp as default for async ([e0591ce](https://github.com/fw-ai-external/python-sdk/commit/e0591ce5d9cbbdad1afd7d2f56191f67137942c1))
