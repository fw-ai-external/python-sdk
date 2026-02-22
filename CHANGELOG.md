# Changelog

## 1.0.0-alpha.28 (2026-02-22)

Full Changelog: [v1.0.0-alpha.27...v1.0.0-alpha.28](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.27...v1.0.0-alpha.28)

### Features

* add R3 routing matrix side-channel injection for official tinker compat ([f6b637b](https://github.com/fw-ai-external/python-sdk/commit/f6b637bd66a94501e7ff66ed671e2a8ff30f752a))
* default prompt_cache_max_len=0 to disable KV cache for verification ([e49ecfb](https://github.com/fw-ai-external/python-sdk/commit/e49ecfbf303eb27c41f69fb19728f8b44843a91c))
* default to greedy mode, add --stochastic flag, include dataset ([049c4e9](https://github.com/fw-ai-external/python-sdk/commit/049c4e9c8d187cb5459b55563b7e66a78fd8a3bc))
* port firetitan SDK and cookbook into fireworks.training ([7134d64](https://github.com/fw-ai-external/python-sdk/commit/7134d649fbd51e3c0bd2cfecadc27bd029f92df7))
* port SDK unit tests from train-firetitan-py ([dac3472](https://github.com/fw-ai-external/python-sdk/commit/dac347290670965c2878179ce2ffe55ff2060c87))
* Regenerate API Reference / Docs ([d97cb7a](https://github.com/fw-ai-external/python-sdk/commit/d97cb7ab0081236ff6bfa342c62943ad79499261))
* Regenerate OpenAPI specs and SDK (v4.24.80) ([ea622fd](https://github.com/fw-ai-external/python-sdk/commit/ea622fd7788900720de1990178b50d34c3da32b9))
* Service mode LoRA documentation ([32edbcd](https://github.com/fw-ai-external/python-sdk/commit/32edbcd89311e2c71acec9a1f795731dcd8eef48))


### Bug Fixes

* correct stale "Server tokenization" log label to "Client tokenization" ([5e6fdcc](https://github.com/fw-ai-external/python-sdk/commit/5e6fdccf57e080db5ef4ccd7990048967ead96b5))
* harden client-side tokenization migration ([7c586fd](https://github.com/fw-ai-external/python-sdk/commit/7c586fd4e0f0269914f7781b85faf2d394ee308f))
* **internal:** skip tests that depend on mock server ([2aa4aca](https://github.com/fw-ai-external/python-sdk/commit/2aa4acae0a3e58ca77eba14aff8ea0834948d29e))
* pass trust_remote_code=True to AutoTokenizer.from_pretrained ([7ae2b5d](https://github.com/fw-ai-external/python-sdk/commit/7ae2b5dc01525e09788d017a2e23ba986b58834e))
* remove sdk/cookbook from training __all__ to fix pyright error ([d185f6f](https://github.com/fw-ai-external/python-sdk/commit/d185f6f22461970e438e0008ee1b392de4ddd841))
* resolve all ruff lint errors in ported SDK/cookbook code ([5df914d](https://github.com/fw-ai-external/python-sdk/commit/5df914d85953cbfdfa0163fd7e5a7b3257852f2a))
* resolve e2e test issues found during test runs ([ed2ed28](https://github.com/fw-ai-external/python-sdk/commit/ed2ed286a2d7d6e0d87225fccaab81fdcb47af4d))
* use proper type annotation for __all__ to satisfy pyright and ruff ([71fb6bc](https://github.com/fw-ai-external/python-sdk/commit/71fb6bcd61b111e86396385fbc4916a72016958b))


### Chores

* **internal:** remove bad test ([4ad6fcf](https://github.com/fw-ai-external/python-sdk/commit/4ad6fcf7dfb730be13593e36ac7e793ecc79902d))
* **internal:** remove mock server code ([fbb2657](https://github.com/fw-ai-external/python-sdk/commit/fbb2657dc23c85bf6d472fd7ed08770fc68330db))
* move verify_logprobs.py and watch_trainer_pods.sh to fireworks repo ([ae3cf92](https://github.com/fw-ai-external/python-sdk/commit/ae3cf92b09d2fa31e5702f995c59c39a4a1039ad))
* remove --stochastic flag, keep greedy as the only default ([5502945](https://github.com/fw-ai-external/python-sdk/commit/5502945d3a8fdc23ea9b5d1b099e15e207a03881))
* remove redundant tinker_patch.py ([27b5521](https://github.com/fw-ai-external/python-sdk/commit/27b55213de1a65f07239c04a7068d455e6d38290))
* sanitize training code for public release ([36fc2ba](https://github.com/fw-ai-external/python-sdk/commit/36fc2ba78413facbccc1c208e3786ef7966c7e67))
* sanitize training docs/tests for public release ([ee1fdb7](https://github.com/fw-ai-external/python-sdk/commit/ee1fdb7076d6c43c4b3146e9cf42a8455a123fae))
* update mock server docs ([db18242](https://github.com/fw-ai-external/python-sdk/commit/db182427328916d87802bd1ba87b5415a9f963d7))


### Documentation

* add compact training readmes and fix lint imports ([12d7196](https://github.com/fw-ai-external/python-sdk/commit/12d7196247c46d6fec79a29811628ec6322e8719))


### Refactors

* clean up verify_logprobs and move to cookbook ([042c731](https://github.com/fw-ai-external/python-sdk/commit/042c731f574e2aa326952a9e744af60d640bbfa1))
* replace R3 side-channel with ModelInput monkey-patch ([53bed56](https://github.com/fw-ai-external/python-sdk/commit/53bed56f8e14e712bdd0e9c1a0d01935fcd5baee))

## 1.0.0-alpha.27 (2026-02-12)

Full Changelog: [v1.0.0-alpha.26...v1.0.0-alpha.27](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.26...v1.0.0-alpha.27)

### Features

* Add Anthropic-compatible Messages API documentation ([f696fa5](https://github.com/fw-ai-external/python-sdk/commit/f696fa543034ff2aacef3796660c69149ab42c55))
* Regenerate OpenAPI specs to add awsS3Config to DPO jobs ([432872b](https://github.com/fw-ai-external/python-sdk/commit/432872b62366b943a49b41298d44e669d4035525))


### Chores

* format all `api.md` files ([41f570a](https://github.com/fw-ai-external/python-sdk/commit/41f570afba601f67136aadcf36f526abee3f0ae1))
* **internal:** bump dependencies ([aa63566](https://github.com/fw-ai-external/python-sdk/commit/aa6356683cc2fdb6e24f0acf710d44d32007f2f4))
* **internal:** fix lint error on Python 3.14 ([9f67e71](https://github.com/fw-ai-external/python-sdk/commit/9f67e7107cfef0c10984ea1bad0fb67d03e62288))

## 1.0.0-alpha.26 (2026-01-30)

Full Changelog: [v1.0.0-alpha.25...v1.0.0-alpha.26](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.25...v1.0.0-alpha.26)

### Features

* **client:** add custom JSON encoder for extended type support ([38fabde](https://github.com/fw-ai-external/python-sdk/commit/38fabde3f36a5d7eb776eadea985db488cff586a))
* update API reference / SDK ([127a473](https://github.com/fw-ai-external/python-sdk/commit/127a4730a682feffa241cf8a63bbce6e436c6e21))

## 1.0.0-alpha.25 (2026-01-27)

Full Changelog: [v1.0.0-alpha.24...v1.0.0-alpha.25](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.24...v1.0.0-alpha.25)

### Features

* update API reference ([9f7626c](https://github.com/fw-ai-external/python-sdk/commit/9f7626cb71374ec9c44d3f1de7ee44c22dd91126))

## 1.0.0-alpha.24 (2026-01-23)

Full Changelog: [v1.0.0-alpha.23...v1.0.0-alpha.24](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.23...v1.0.0-alpha.24)

### Chores

* **ci:** upgrade `actions/github-script` ([7869665](https://github.com/fw-ai-external/python-sdk/commit/7869665ddc977126a2bd375a046538b9b6cb66b5))

## 1.0.0-alpha.23 (2026-01-16)

Full Changelog: [v1.0.0-alpha.22...v1.0.0-alpha.23](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.22...v1.0.0-alpha.23)

### Features

* **validation:** add Pydantic models and validation for dataset rows in training workflow ([a4cbe9b](https://github.com/fw-ai-external/python-sdk/commit/a4cbe9b7d1eec031116d9960b21385071f5a6093))


### Chores

* **internal:** update `actions/checkout` version ([14881d2](https://github.com/fw-ai-external/python-sdk/commit/14881d22e04ec739d2ee20a9757dbeb9d1d84079))

## 1.0.0-alpha.22 (2026-01-13)

Full Changelog: [v1.0.0-alpha.21...v1.0.0-alpha.22](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.21...v1.0.0-alpha.22)

### Features

* Add model_kind and model_state schemas to stainless.yml ([67e6a8b](https://github.com/fw-ai-external/python-sdk/commit/67e6a8b67942c7be36a78a9308b725b137083c94))
* **client:** add support for binary request streaming ([d9e22fd](https://github.com/fw-ai-external/python-sdk/commit/d9e22fd467aeabe9fb6243353d74a5de5a5e33ad))


### Chores

* **internal:** codegen related update ([7fbd701](https://github.com/fw-ai-external/python-sdk/commit/7fbd701b46f7bc446bd295da4628e415e5f2e19c))

## 1.0.0-alpha.21 (2026-01-12)

Full Changelog: [v1.0.0-alpha.20...v1.0.0-alpha.21](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.20...v1.0.0-alpha.21)

### Features

* Regenerate SDK Docs ([5072494](https://github.com/fw-ai-external/python-sdk/commit/5072494385b4c5862aa3d281fe50a801ef3f4003))


### Chores

* **internal:** codegen related update ([5857d3e](https://github.com/fw-ai-external/python-sdk/commit/5857d3e64487426fc42c645e20099cdd83868b42))

## 1.0.0-alpha.20 (2025-12-23)

Full Changelog: [v1.0.0-alpha.19...v1.0.0-alpha.20](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.19...v1.0.0-alpha.20)

### Features

* Remove deprecated Evaluator fields ([be410eb](https://github.com/fw-ai-external/python-sdk/commit/be410ebe0b291ba2c726d0c716776d8d4da17f87))

## 1.0.0-alpha.19 (2025-12-22)

Full Changelog: [v1.0.0-alpha.18...v1.0.0-alpha.19](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.18...v1.0.0-alpha.19)

### Features

* Document GLM 4.7 / reasoning_history ([a7e17a6](https://github.com/fw-ai-external/python-sdk/commit/a7e17a6cde8649814d3bcacedcc6e175d1671116))

## 1.0.0-alpha.18 (2025-12-20)

Full Changelog: [v1.0.0-alpha.17...v1.0.0-alpha.18](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.17...v1.0.0-alpha.18)

## 1.0.0-alpha.17 (2025-12-20)

Full Changelog: [v1.0.0-alpha.16...v1.0.0-alpha.17](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.16...v1.0.0-alpha.17)

## 1.0.0-alpha.16 (2025-12-19)

Full Changelog: [v1.0.0-alpha.15...v1.0.0-alpha.16](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.15...v1.0.0-alpha.16)

### Features

* Add deployment shapes to sdk ([5156da6](https://github.com/fw-ai-external/python-sdk/commit/5156da6ed9bfaf6e58d2275480f2dd7dd7aaa9ce))

## 1.0.0-alpha.15 (2025-12-19)

Full Changelog: [v1.0.0-alpha.14...v1.0.0-alpha.15](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.14...v1.0.0-alpha.15)

### Features

* run "make" + add SDK generation guide ([10b9806](https://github.com/fw-ai-external/python-sdk/commit/10b9806dfd4efa78416b3443bb75b83cfd58f3e9))

## 1.0.0-alpha.14 (2025-12-19)

Full Changelog: [v1.0.0-alpha.13...v1.0.0-alpha.14](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.13...v1.0.0-alpha.14)

### Documentation

* add more examples ([b3b223c](https://github.com/fw-ai-external/python-sdk/commit/b3b223ce01c829f401b20902247962ee1de0de76))

## 1.0.0-alpha.13 (2025-12-18)

Full Changelog: [v1.0.0-alpha.12...v1.0.0-alpha.13](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.12...v1.0.0-alpha.13)

### Features

* Updated `stainless.yml` to include execute train step ([617aaf9](https://github.com/fw-ai-external/python-sdk/commit/617aaf92a5bc0acf43d7ec9a883409d248ff8d36))


### Chores

* **internal:** add `--fix` argument to lint script ([859cb4f](https://github.com/fw-ai-external/python-sdk/commit/859cb4f846f0d5f975df3eaa9d018457491fc0b9))

## 1.0.0-alpha.12 (2025-12-17)

Full Changelog: [v1.0.0-alpha.11...v1.0.0-alpha.12](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.11...v1.0.0-alpha.12)

### Bug Fixes

* use async_to_httpx_files in patch method ([5759d42](https://github.com/fw-ai-external/python-sdk/commit/5759d426884811343b4c50c67c8bde0481af9045))

## 1.0.0-alpha.11 (2025-12-16)

Full Changelog: [v1.0.0-alpha.10...v1.0.0-alpha.11](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.10...v1.0.0-alpha.11)

### Chores

* speedup initial import ([2736393](https://github.com/fw-ai-external/python-sdk/commit/2736393d2907825b2cf67e5f139753894663f77f))

## 1.0.0-alpha.10 (2025-12-16)

Full Changelog: [v1.0.0-alpha.9...v1.0.0-alpha.10](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.9...v1.0.0-alpha.10)

### Features

* Expose Create Evaluator method as part of Docs/SDK ([050063d](https://github.com/fw-ai-external/python-sdk/commit/050063d763bba40cd229f555e6f6bc22e8a0b7d8))


### Chores

* **internal:** add missing files argument to base client ([bcf1a7a](https://github.com/fw-ai-external/python-sdk/commit/bcf1a7a50280d5c7e3ec5492f6770b10e83526ca))

## 1.0.0-alpha.9 (2025-12-12)

Full Changelog: [v1.0.0-alpha.8...v1.0.0-alpha.9](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.8...v1.0.0-alpha.9)

## 1.0.0-alpha.8 (2025-12-12)

Full Changelog: [v1.0.0-alpha.7...v1.0.0-alpha.8](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.7...v1.0.0-alpha.8)

### Features

* add pagination ([d2ab4bc](https://github.com/fw-ai-external/python-sdk/commit/d2ab4bc3171b3ac6ae70207df83793b9dc90c49e))
* Automate SDK Pagination Config ([d098f72](https://github.com/fw-ai-external/python-sdk/commit/d098f72fc6f2099e627eb647a62770a76aadc7de))

## 1.0.0-alpha.7 (2025-12-10)

Full Changelog: [v1.0.0-alpha.6...v1.0.0-alpha.7](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.6...v1.0.0-alpha.7)

### Features

* Remove methods from SDK ([2d73091](https://github.com/fw-ai-external/python-sdk/commit/2d730913dbc2c1f05547d891256d62f5d9067015))

## 1.0.0-alpha.6 (2025-12-10)

Full Changelog: [v1.0.0-alpha.5...v1.0.0-alpha.6](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.5...v1.0.0-alpha.6)

### Features

* add evaluator job / evaluator CRUD APIs to API/SDK ([1f677b8](https://github.com/fw-ai-external/python-sdk/commit/1f677b87c8330c0c0e1d768319c15fbce5930f5d))

## 1.0.0-alpha.5 (2025-12-09)

Full Changelog: [v1.0.0-alpha.4...v1.0.0-alpha.5](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.4...v1.0.0-alpha.5)

### Features

* Update API/SDK ([c47e0fb](https://github.com/fw-ai-external/python-sdk/commit/c47e0fb7a18a05fd4c50d46bf024762f7c83ff00))


### Bug Fixes

* **types:** allow pyright to infer TypedDict types within SequenceNotStr ([211cefd](https://github.com/fw-ai-external/python-sdk/commit/211cefd338e16d81c8a40a1acf9e3399a0ebfbd0))


### Chores

* add missing docstrings ([ac5bf0c](https://github.com/fw-ai-external/python-sdk/commit/ac5bf0c1229ded12db30d75bffa3540c69280785))
* **docs:** use environment variables for authentication in code snippets ([1501b2f](https://github.com/fw-ai-external/python-sdk/commit/1501b2fc7f1320a1d4a41fc39e6fdb0bc4d795c6))
* update lockfile ([58d2c86](https://github.com/fw-ai-external/python-sdk/commit/58d2c86e5856bbc1f3550b6449502a5b302e5c6e))

## 1.0.0-alpha.4 (2025-12-03)

Full Changelog: [v1.0.0-alpha.3...v1.0.0-alpha.4](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.3...v1.0.0-alpha.4)

### Bug Fixes

* type errors in example file ([b707bb8](https://github.com/fw-ai-external/python-sdk/commit/b707bb818e8f05d01fa984f9f55a3fc3dd0d6498))


### Chores

* remove external reference comments from example file ([6538f6a](https://github.com/fw-ai-external/python-sdk/commit/6538f6a62fbec221dc35743220bf77bd0f86ab3c))


### Documentation

* add iterative reinforcement learning workflow example ([56850d7](https://github.com/fw-ai-external/python-sdk/commit/56850d7e7cf0bc813538c01c4d8243726ac6330f))

## 1.0.0-alpha.3 (2025-12-02)

Full Changelog: [v1.0.0-alpha.2...v1.0.0-alpha.3](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.2...v1.0.0-alpha.3)

### Features

* try send_as_path ([1c7ed63](https://github.com/fw-ai-external/python-sdk/commit/1c7ed63dac60bb88d70148e0142c496ff1c409c1))


### Documentation

* add account_id configuration section and update examples ([f1ca3af](https://github.com/fw-ai-external/python-sdk/commit/f1ca3af4a1f388a841cc36defdc780560f4d7587))

## 1.0.0-alpha.2 (2025-12-02)

Full Changelog: [v1.0.0-alpha.1...v1.0.0-alpha.2](https://github.com/fw-ai-external/python-sdk/compare/v1.0.0-alpha.1...v1.0.0-alpha.2)

### Documentation

* add dataset upload documentation with complete workflow examples ([821046d](https://github.com/fw-ai-external/python-sdk/commit/821046dc40cf1c9bf4c468bf5dd2ed02e21f6188))
* add link to Fireworks Dashboard for viewing datasets ([d69db06](https://github.com/fw-ai-external/python-sdk/commit/d69db060892d2f151e13316597d5fcb7afda5c75))
* improve examples to print meaningful response content ([f801de8](https://github.com/fw-ai-external/python-sdk/commit/f801de8187ef6a41136a3df23e1955bae1595d65))

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
