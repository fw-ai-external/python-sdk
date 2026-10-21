# Training SDK compatibility with Tinker Cookbook

The native Fireworks training SDK owns its client, transport, futures, errors and
data types. It does not need Tinker installed. The compatibility baseline is the
previous Fireworks SDK's Tinker 0.23 method and JSON wire contract. It is not a
promise to implement every feature added to newer Tinker services.

Use `from fireworks.training import sdk` (or the equivalent native `tinker`
name) and construct native `sdk.Datum`,
`sdk.ModelInput`, `sdk.TensorData` and `sdk.AdamParams`. External recipes need
these imports and an explicit Fireworks service/publication configuration;
unchanged external SDK objects are not adapted. Returned objects and exceptions
belong to Fireworks. Catch `sdk.TrainingError` or the exported SDK API errors.
There is no external patch kit, global module alias or service replacement.

The maintained Fireworks cookbook uses native types and renderer helpers.
All installs and extras are independent of both external packages. SDFT is
maintained separately in the [Fireworks Tinker-Cookbook fork](https://github.com/fw-ai-external/tinker-cookbook). Familiar public
method names make external recipe adaptation possible; they do not promise
foreign class/exception identity or private upstream hooks.

## Supported client features

| Feature | Fireworks interface |
|---|---|
| Forward, backward, custom losses, optimizer, state save/load, sync and async futures | Existing `FiretitanTrainingClient` methods; JSON v1/v2 behavior preserved |
| Fireworks loss options | `loss_fn_config` passes supported backend options through; native schemas retain heterogeneous option values |
| Custom TIS/MIS using a completed policy forward | `forward_backward_custom(..., precomputed_forward=result)`; reuse requires identical data/order and unchanged policy weights. There is no `precomputed_logprobs` keyword on ordinary `forward_backward` |
| Routing replay and sampling references | Native `ModelInput` fields; no runtime patch needed |
| Dedicated LoRA publication | Save a sampler snapshot, then hot-load the deployment through the managed service |
| Dedicated full-parameter publication | FILE snapshots/hot-load, or capability-advertised RDMA `weight_sync`; these are different operations |
| Serverless LoRA publication | Save a session-scoped sampler snapshot and create a sampling client for its returned path |
| Standalone serverless sampling (no `create_model` slot) | On a service that has not created a model, `create_sampling_client(base_model=...)` and `create_sampling_client(model_path="<account>/<run_id>/<name>")` (a path from `save_weights_for_sampler`, even after its training session ended) bind their own sampler route. They create no training run and use no concurrent-run quota. A checkpoint is served from its run's trainer region. `model_path` may also name a live session's checkpoint (`accounts/<a>/trainingSessions/<ts>/checkpoints/<ckpt>`, prefixes optional) to use that session's route. A service that created a model keeps sampling through its own session |
| Picklable sampling client and sampler handles (Tinker multiprocessing pattern) | Like Tinker, a pickled `FiretitanSamplingClient` carries its connection state including the API key and headers, so workers need no environment of their own; each worker gets a fresh concurrency controller (a fixed limit carries over). `get_sampler_handle()` / `FiretitanSamplingClient.from_sampler_handle(handle, api_key=None)` pass a sampler without credentials; the receiving process uses `api_key` or `FIREWORKS_API_KEY` |
| Checkpoint resume | Keep the server-returned path and canonical control-plane restore reference; the Fireworks cookbook records logical names separately |

Choosing a publication path must respect the managed service and trainer
capabilities. A generic Tinker save-and-sample call cannot select all Fireworks
deployment, reference-trainer and weight-sync modes. The Fireworks cookbook's
`make_weight_sync` and SDK-managed service are the reference integration.

## Unsupported inherited operations

Tinker-only REST methods are not exposed:
training-run, session and sampler metadata; REST checkpoint listing and deletion;
archive, publication, TTL, audit logs and session project assignment. The trainer's
checkpoint list lacks Tinker's required timestamps and paths; the SDK does not
invent those fields. Use `TrainingClient.list_checkpoints()` or
`ServiceClient.list_checkpoints(job_id)` and `ServiceClient.promote_checkpoint()`.
Serverless `get_weights_info_by_tinker_path` returns real checkpoint metadata;
direct dedicated resume requires explicit configuration followed by `load_state`.
SDK-managed resume already has that configuration.

Training datums reject opaque image-asset pointers and DMel audio chunks; use
inline images or encoded text. Generic chunk DTOs do not establish trainer support.

Checkpoint `ttl_seconds`, project assignment, weights access tokens, state overwrite,
top-k prompt logprobs and the combined save-and-create-sampler operation are not
supported. Server-wide capabilities are queried only from a dedicated endpoint;
serverless clients use selected-model capabilities from model creation. No
metadata or successful deletion is synthesized for an unconnected service.

## Gaps and explicit workarounds

| Gap | Current behavior / clean workaround |
|---|---|
| Cross-entropy backward per-token logprobs | The backend may return aggregate loss without logprobs. The SDK adds response-token counts, not fabricated logprobs. Use the returned aggregate loss for training NLL where its normalization is known, or explicitly run `forward` for token-level metrics. That forward has extra GPU cost and must be at the intended policy version |
| `save_state(name)` retaining a persistent logical name | The SDK sends the requested name; dedicated trainer checkpoints may be stored as `step-N`. Do not rewrite the returned path to pretend the alias persisted. Use the cookbook checkpoint manifest and canonical restore reference. Persistent aliases and an authoritative save response need backend support |
| Renderer metadata from an arbitrary historical checkpoint | A schema field or current-session metadata is not durable historical metadata. Supply the renderer explicitly when resuming. Remote discovery requires the training-run API to return the stored `user_metadata` |
| Loading an initial checkpoint into a dedicated frozen reference | The external integration rejects this path. Correct DPO/KL semantics require the reference to contain the intended initial weights. Use a supported serverless reference flow or an explicitly provisioned/verified reference; do not silently substitute the base model |
| Dedicated SFT sampling evaluators / fixed base-model opponent | SDK deployment sampling exists, but the external recipes do not provision all required evaluator/opponent deployments. Configure a separate appropriate sampler in a client recipe. This needs orchestration work, not a trainer protocol change |
| Serverless KL penalty and periodically updated SDFT teacher | Rejected by the external integration; use a supported dedicated reference flow or a static teacher. No implicit fallback |
| Audio / newer model-specific chunk formats | Training accepts encoded text and inline images. DMel audio and opaque image pointers are rejected; generic DTO classes do not establish trainer support. Validate model, renderer and sampler support together |
| Newer sparse helper's `pad_value` argument | Tinker0.23 and the owned baseline helper omit zero entries only. The external decision recipe's nonzero-pad call is newer. Use a dense target tensor to preserve nonzero padding exactly, or validate a newer recipe/runtime integration separately |
| External recipe constructs `tinker.ServiceClient` directly | Pointing its URL at Fireworks is insufficient. Wire the Fireworks service and the correct trainer/deployment/session flow explicitly |
| Tinker class/exception identity, private holders, capture and provider hooks | Independent runtimes have different classes. Adapt the application boundary, including exception handlers and connection-pool enums; no global module aliasing |
| Protobuf requests | This migration preserves JSON requests. Binary result decoding is available where already negotiated. End-to-end protobuf requests require the subsequent SDK/gateway/trainer protocol change |

## External recipe coverage

Audited `fw-ai-external/tinker-cookbook` at staging commit
[`c2608f9`](https://github.com/fw-ai-external/tinker-cookbook/tree/c2608f9c907e21a980bf8feed47138656130a328)
and the stacked RL/distillation tip
[`5c20561`](https://github.com/fw-ai-external/tinker-cookbook/tree/5c20561988fd45ddf6086fcac9affa13ccf92616).
The latter contains the work in [PR 16](https://github.com/fw-ai-external/tinker-cookbook/pull/16)
and [PR 17](https://github.com/fw-ai-external/tinker-cookbook/pull/17).

SFT, DPO, math/code RL, basic RL, guess-number, on/off-policy distillation and
SDFT have Fireworks configuration paths in that stack. Twenty-questions and
text-arena are restricted to serverless. Other recipes need entrypoint/config
or auxiliary sampler adaptation; audio additionally needs backend model support.
Native unit tests and adapted-input checks do not establish live support for
every dataset, sandbox, renderer, model or publication topology. Prioritize the
maintained Fireworks cookbook recipes for supported training flows.
