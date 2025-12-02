# Fireworks AI Python SDK API library

<!-- prettier-ignore -->
[![PyPI version](https://img.shields.io/pypi/v/fireworks-ai.svg?label=pypi%20(stable))](https://pypi.org/project/fireworks-ai/)

The Fireworks AI Python SDK library provides convenient access to the Fireworks REST API from any Python 3.9+
application. The library includes type definitions for all request params and response fields,
and offers both synchronous and asynchronous clients. The synchronous client uses [httpx](https://github.com/encode/httpx),
while the asynchronous client uses [aiohttp](https://github.com/aio-libs/aiohttp) by default for improved concurrency performance.

## Documentation

The REST API documentation can be found on [docs.fireworks.ai](https://docs.fireworks.ai/api-reference/introduction). The full API of this library can be found in [api.md](api.md).

## Installation

```sh
# install from PyPI
pip install --pre fireworks-ai
```

## Usage

The full API of this library can be found in [api.md](api.md).

```python
import os
from fireworks import Fireworks

client = Fireworks(
    api_key=os.environ.get("FIREWORKS_API_KEY"),  # This is the default and can be omitted
)

completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "How do LLMs work?",
        }
    ],
    model="accounts/fireworks/models/kimi-k2-instruct-0905",
)
print(completion.choices[0].message.content)
```

While you can provide an `api_key` keyword argument,
we recommend using [python-dotenv](https://pypi.org/project/python-dotenv/)
to add `FIREWORKS_API_KEY="My API Key"` to your `.env` file
so that your API Key is not stored in source control.

## Async usage

Simply import `AsyncFireworks` instead of `Fireworks` and use `await` with each API call:

```python
import os
import asyncio
from fireworks import AsyncFireworks

client = AsyncFireworks(
    api_key=os.environ.get("FIREWORKS_API_KEY"),  # This is the default and can be omitted
)


async def main() -> None:
    completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "How do LLMs work?",
            }
        ],
        model="accounts/fireworks/models/kimi-k2-instruct-0905",
    )
    print(completion.choices[0].message.content)


asyncio.run(main())
```

Functionality between the synchronous and asynchronous clients is otherwise identical.

## Streaming responses

We provide support for streaming responses using Server Side Events (SSE).

```python
from fireworks import Fireworks

client = Fireworks()

stream = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "How do LLMs work?",
        }
    ],
    model="accounts/fireworks/models/kimi-k2-instruct-0905",
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

The async client uses the exact same interface.

```python
from fireworks import AsyncFireworks

client = AsyncFireworks()

stream = await client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "How do LLMs work?",
        }
    ],
    model="accounts/fireworks/models/kimi-k2-instruct-0905",
    stream=True,
)
async for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Reasoning models

For thinking/reasoning models, the SDK provides access to the model's reasoning process through the `reasoning_content` field. This field contains the model's internal reasoning that would otherwise appear in `<think></think>` tags within the content field.

For supported reasoning models, the `reasoning_content` field is automatically populated as a separate field in the response.

### Basic usage

```python
from fireworks import Fireworks

client = Fireworks()

completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "What is 25 * 37?",
        }
    ],
    model="accounts/fireworks/models/<reasoning-model>",
)

# Access the reasoning content (thinking process)
for choice in completion.choices:
    if choice.message.reasoning_content:
        print("Reasoning:", choice.message.reasoning_content)
    print("Answer:", choice.message.content)
```

### Controlling reasoning effort

You can control the reasoning token length using the `reasoning_effort` parameter:

```python
completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Solve this step by step: If a train travels at 60 mph for 2.5 hours, how far does it go?",
        }
    ],
    model="accounts/fireworks/models/<reasoning-model>",
    reasoning_effort="high",  # Options: "none", "low", "medium", "high"
)
```

The `reasoning_effort` parameter accepts:
- `"none"` - Disable thinking
- `"low"` - Minimal reasoning tokens
- `"medium"` - Moderate reasoning tokens
- `"high"` - Maximum reasoning tokens
- An integer - Hard cutoff for reasoning token length (Fireworks-specific)

### Streaming with reasoning content

When streaming, the reasoning content is available in each chunk's delta:

```python
from fireworks import Fireworks

client = Fireworks()

stream = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "What is the square root of 144?",
        }
    ],
    model="accounts/fireworks/models/<reasoning-model>",
    stream=True,
)

reasoning_parts = []
content_parts = []

for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.reasoning_content:
        reasoning_parts.append(delta.reasoning_content)
    if delta.content:
        content_parts.append(delta.content)

print("Reasoning:", "".join(reasoning_parts))
print("Answer:", "".join(content_parts))
```

### Multi-turn conversations

When building multi-turn conversations with reasoning models, you can pass the assistant message directly to preserve the reasoning context:

```python
from fireworks import Fireworks

client = Fireworks()

# First turn
first_response = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "What is 15 + 27?",
        }
    ],
    model="accounts/fireworks/models/<reasoning-model>",
)

# Second turn - pass the previous assistant message directly
second_response = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "What is 15 + 27?",
        },
        first_response.choices[0].message,  # Includes role, content, reasoning_content, etc.
        {
            "role": "user",
            "content": "Now multiply that result by 2.",
        },
    ],
    model="accounts/fireworks/models/<reasoning-model>",
)

print(second_response.choices[0].message.content)
```

Passing the message object directly preserves the `reasoning_content` field, helping the model maintain context about its reasoning process across turns.

## Using types

Nested request parameters are [TypedDicts](https://docs.python.org/3/library/typing.html#typing.TypedDict). Responses are [Pydantic models](https://docs.pydantic.dev) which also provide helper methods for things like:

- Serializing back into JSON, `model.to_json()`
- Converting to a dictionary, `model.to_dict()`

Typed requests and responses provide autocomplete and documentation within your editor. If you would like to see type errors in VS Code to help catch bugs earlier, set `python.analysis.typeCheckingMode` to `basic`.

## Nested params

Nested parameters are dictionaries, typed using `TypedDict`, for example:

```python
from fireworks import Fireworks

client = Fireworks()

completion = client.chat.completions.create(
    messages=[{"role": "role"}],
    model="model",
    response_format={"type": "json_object"},
)
print(completion.response_format)
```

## File uploads

Request parameters that correspond to file uploads can be passed as `bytes`, or a [`PathLike`](https://docs.python.org/3/library/os.html#os.PathLike) instance or a tuple of `(filename, contents, media type)`.

```python
from pathlib import Path
from fireworks import Fireworks

client = Fireworks()

client.datasets.upload(
    dataset_id="dataset_id",
    account_id="account_id",
    file=Path("/path/to/file"),
)
```

The async client uses the exact same interface. If you pass a [`PathLike`](https://docs.python.org/3/library/os.html#os.PathLike) instance, the file contents will be read asynchronously automatically.

## Uploading datasets

The SDK provides two methods for uploading datasets to Fireworks, depending on file size.

### Option 1: Direct upload (files < 150MB) - Recommended

For files under 150MB, use the streamlined direct upload approach. This uses only SDK methods with no additional dependencies:

```python
import time
from pathlib import Path
from fireworks import Fireworks

client = Fireworks()

account_id = "your-account-id"
dataset_id = "my-dataset"
file_path = Path("/path/to/your-dataset.jsonl")

# Count lines in the dataset file (optional, for bookkeeping)
with open(file_path) as f:
    example_count = sum(1 for line in f if line.strip())

# Step 1: Create the dataset record
dataset = client.datasets.create(
    account_id=account_id,
    dataset_id=dataset_id,
    dataset={"exampleCount": str(example_count)},
)
print(f"Created dataset: {dataset.name}")

# Step 2: Upload the file
upload_response = client.datasets.upload(
    account_id=account_id,
    dataset_id=dataset_id,
    file=file_path,
)
print(f"Upload response: {upload_response}")

# Step 3: Poll until dataset is ready
while True:
    dataset = client.datasets.get(account_id=account_id, dataset_id=dataset_id)
    print(f"Dataset state: {dataset.state}")
    if dataset.state == "READY":
        print("Dataset is ready!")
        break
    elif dataset.state == "UPLOADING":
        time.sleep(2)
    else:
        raise Exception(f"Unexpected dataset state: {dataset.state}")
```

### Option 2: Signed URL upload (files > 150MB)

For larger files, use the signed URL approach. This requires an HTTP client (like `httpx` or `requests`) to upload to the signed URL:

```python
import time
from pathlib import Path
import httpx  # or use requests
from fireworks import Fireworks

client = Fireworks()

account_id = "your-account-id"
dataset_id = "my-large-dataset"
file_path = Path("/path/to/your-large-dataset.jsonl")
file_size = file_path.stat().st_size
file_name = file_path.name

# Count lines in the dataset file (optional, for bookkeeping)
with open(file_path) as f:
    example_count = sum(1 for line in f if line.strip())

# Step 1: Create the dataset record
dataset = client.datasets.create(
    account_id=account_id,
    dataset_id=dataset_id,
    dataset={"exampleCount": str(example_count)},
)
print(f"Created dataset: {dataset.name}")

# Step 2: Get signed upload URL
upload_endpoint = client.datasets.get_upload_endpoint(
    account_id=account_id,
    dataset_id=dataset_id,
    filename_to_size={file_name: str(file_size)},
)
signed_url = upload_endpoint.filename_to_signed_urls[file_name]
print(f"Got signed URL for upload")

# Step 3: Upload directly to the signed URL (requires external HTTP client)
with open(file_path, "rb") as f:
    file_content = f.read()

response = httpx.put(
    signed_url,
    content=file_content,
    headers={
        "Content-Type": "application/octet-stream",
        "x-goog-content-length-range": f"{file_size},{file_size}",
    },
)
response.raise_for_status()
print("File uploaded to signed URL")

# Step 4: Validate the upload
client.datasets.validate_upload(
    account_id=account_id,
    dataset_id=dataset_id,
    body={},
)
print("Upload validated")

# Step 5: Poll until dataset is ready
while True:
    dataset = client.datasets.get(account_id=account_id, dataset_id=dataset_id)
    print(f"Dataset state: {dataset.state}")
    if dataset.state == "READY":
        print("Dataset is ready!")
        break
    elif dataset.state == "UPLOADING":
        time.sleep(2)
    else:
        raise Exception(f"Unexpected dataset state: {dataset.state}")
```

> **Note:** The `httpx` library is already a dependency of the SDK, so no additional installation is needed.

### Dataset file format

Dataset files should be in JSONL format (JSON Lines), where each line is a valid JSON object. For chat-based fine-tuning, use the following format:

```json
{"messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Hello!"}, {"role": "assistant", "content": "Hi there! How can I help you today?"}]}
{"messages": [{"role": "user", "content": "What is 2+2?"}, {"role": "assistant", "content": "2+2 equals 4."}]}
```

### Managing datasets

You can view and manage your datasets in the [Fireworks Dashboard](https://app.fireworks.ai/dashboard/datasets).

```python
# List all datasets
datasets = client.datasets.list(account_id=account_id)
for ds in datasets.datasets:
    print(f"{ds.name}: {ds.state}")

# Get a specific dataset
dataset = client.datasets.get(account_id=account_id, dataset_id=dataset_id)

# Delete a dataset
client.datasets.delete(account_id=account_id, dataset_id=dataset_id)
```

## Handling errors

When the library is unable to connect to the API (for example, due to network connection problems or a timeout), a subclass of `fireworks.APIConnectionError` is raised.

When the API returns a non-success status code (that is, 4xx or 5xx
response), a subclass of `fireworks.APIStatusError` is raised, containing `status_code` and `response` properties.

All errors inherit from `fireworks.APIError`.

```python
import fireworks
from fireworks import Fireworks

client = Fireworks()

try:
    client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "How do LLMs work?",
            }
        ],
        model="accounts/fireworks/models/kimi-k2-instruct-0905",
    )
except fireworks.APIConnectionError as e:
    print("The server could not be reached")
    print(e.__cause__)  # an underlying Exception, likely raised within httpx.
except fireworks.RateLimitError as e:
    print("A 429 status code was received; we should back off a bit.")
except fireworks.APIStatusError as e:
    print("Another non-200-range status code was received")
    print(e.status_code)
    print(e.response)
```

Error codes are as follows:

| Status Code | Error Type                 |
| ----------- | -------------------------- |
| 400         | `BadRequestError`          |
| 401         | `AuthenticationError`      |
| 403         | `PermissionDeniedError`    |
| 404         | `NotFoundError`            |
| 422         | `UnprocessableEntityError` |
| 429         | `RateLimitError`           |
| >=500       | `InternalServerError`      |
| N/A         | `APIConnectionError`       |

### Retries

Certain errors are automatically retried 2 times by default, with a short exponential backoff.
Connection errors (for example, due to a network connectivity problem), 408 Request Timeout, 409 Conflict,
429 Rate Limit, and >=500 Internal errors are all retried by default.

You can use the `max_retries` option to configure or disable retry settings:

```python
from fireworks import Fireworks

# Configure the default for all requests:
client = Fireworks(
    # default is 2
    max_retries=0,
)

# Or, configure per-request:
client.with_options(max_retries=5).chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "How do LLMs work?",
        }
    ],
    model="accounts/fireworks/models/kimi-k2-instruct-0905",
)
```

### Timeouts

By default requests time out after 1 minute. You can configure this with a `timeout` option,
which accepts a float or an [`httpx.Timeout`](https://www.python-httpx.org/advanced/timeouts/#fine-tuning-the-configuration) object:

```python
from fireworks import Fireworks

# Configure the default for all requests:
client = Fireworks(
    # 20 seconds (default is 1 minute)
    timeout=20.0,
)

# More granular control:
client = Fireworks(
    timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0),
)

# Override per-request:
client.with_options(timeout=5.0).chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "How do LLMs work?",
        }
    ],
    model="accounts/fireworks/models/kimi-k2-instruct-0905",
)
```

On timeout, an `APITimeoutError` is thrown.

Note that requests that time out are [retried twice by default](#retries).

## Advanced

### Logging

We use the standard library [`logging`](https://docs.python.org/3/library/logging.html) module.

You can enable logging by setting the environment variable `FIREWORKS_LOG` to `info`.

```shell
$ export FIREWORKS_LOG=info
```

Or to `debug` for more verbose logging.

### How to tell whether `None` means `null` or missing

In an API response, a field may be explicitly `null`, or missing entirely; in either case, its value is `None` in this library. You can differentiate the two cases with `.model_fields_set`:

```py
if response.my_field is None:
  if 'my_field' not in response.model_fields_set:
    print('Got json like {}, without a "my_field" key present at all.')
  else:
    print('Got json like {"my_field": null}.')
```

### Accessing raw response data (e.g. headers)

The "raw" Response object can be accessed by prefixing `.with_raw_response.` to any HTTP method call, e.g.,

```py
from fireworks import Fireworks

client = Fireworks()
response = client.chat.completions.with_raw_response.create(
    messages=[{
        "role": "user",
        "content": "How do LLMs work?",
    }],
    model="accounts/fireworks/models/kimi-k2-instruct-0905",
)
print(response.headers.get('X-My-Header'))

completion = response.parse()  # get the object that `chat.completions.create()` would have returned
print(completion.id)
```

These methods return an [`APIResponse`](https://github.com/fw-ai-external/python-sdk/tree/main/src/fireworks/_response.py) object.

The async client returns an [`AsyncAPIResponse`](https://github.com/fw-ai-external/python-sdk/tree/main/src/fireworks/_response.py) with the same structure, the only difference being `await`able methods for reading the response content.

#### `.with_streaming_response`

The above interface eagerly reads the full response body when you make the request, which may not always be what you want.

To stream the response body, use `.with_streaming_response` instead, which requires a context manager and only reads the response body once you call `.read()`, `.text()`, `.json()`, `.iter_bytes()`, `.iter_text()`, `.iter_lines()` or `.parse()`. In the async client, these are async methods.

```python
with client.chat.completions.with_streaming_response.create(
    messages=[
        {
            "role": "user",
            "content": "How do LLMs work?",
        }
    ],
    model="accounts/fireworks/models/kimi-k2-instruct-0905",
) as response:
    print(response.headers.get("X-My-Header"))

    for line in response.iter_lines():
        print(line)
```

The context manager is required so that the response will reliably be closed.

### Making custom/undocumented requests

This library is typed for convenient access to the documented API.

If you need to access undocumented endpoints, params, or response properties, the library can still be used.

#### Undocumented endpoints

To make requests to undocumented endpoints, you can make requests using `client.get`, `client.post`, and other
http verbs. Options on the client will be respected (such as retries) when making this request.

```py
import httpx

response = client.post(
    "/foo",
    cast_to=httpx.Response,
    body={"my_param": True},
)

print(response.headers.get("x-foo"))
```

#### Undocumented request params

If you want to explicitly send an extra param, you can do so with the `extra_query`, `extra_body`, and `extra_headers` request
options.

#### Undocumented response properties

To access undocumented response properties, you can access the extra fields like `response.unknown_prop`. You
can also get all the extra fields on the Pydantic model as a dict with
[`response.model_extra`](https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_extra).

### Configuring the HTTP client

You can directly override the [httpx client](https://www.python-httpx.org/api/#client) to customize it for your use case, including:

- Support for [proxies](https://www.python-httpx.org/advanced/proxies/)
- Custom [transports](https://www.python-httpx.org/advanced/transports/)
- Additional [advanced](https://www.python-httpx.org/advanced/clients/) functionality

```python
import httpx
from fireworks import Fireworks, DefaultHttpxClient

client = Fireworks(
    # Or use the `FIREWORKS_BASE_URL` env var
    base_url="http://my.test.server.example.com:8083",
    http_client=DefaultHttpxClient(
        proxy="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

You can also customize the client on a per-request basis by using `with_options()`:

```python
client.with_options(http_client=DefaultHttpxClient(...))
```

### Managing HTTP resources

By default the library closes underlying HTTP connections whenever the client is [garbage collected](https://docs.python.org/3/reference/datamodel.html#object.__del__). You can manually close the client using the `.close()` method if desired, or with a context manager that closes when exiting.

```py
from fireworks import Fireworks

with Fireworks() as client:
  # make requests here
  ...

# HTTP client is now closed
```

## Versioning

This package generally follows [SemVer](https://semver.org/spec/v2.0.0.html) conventions, though certain backwards-incompatible changes may be released as minor versions:

1. Changes that only affect static types, without breaking runtime behavior.
2. Changes to library internals which are technically public but not intended or documented for external use. _(Please open a GitHub issue to let us know if you are relying on such internals.)_
3. Changes that we do not expect to impact the vast majority of users in practice.

We take backwards-compatibility seriously and work hard to ensure you can rely on a smooth upgrade experience.

We are keen for your feedback; please open an [issue](https://www.github.com/fw-ai-external/python-sdk/issues) with questions, bugs, or suggestions.

### Determining the installed version

If you've upgraded to the latest version but aren't seeing any new features you were expecting then your python environment is likely still using an older version.

You can determine the version that is being used at runtime with:

```py
import fireworks
print(fireworks.__version__)
```

## Requirements

Python 3.9 or higher.

## Contributing

See [the contributing documentation](./CONTRIBUTING.md).
