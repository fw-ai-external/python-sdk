# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo
from .provider_param import ProviderParam

__all__ = ["AssertionParam", "CodeAssertion", "CodeAssertionOptions", "LlmAssertion", "LlmAssertionEvaluateOptions"]


class CodeAssertionOptions(TypedDict, total=False):
    env_vars: Annotated[Dict[str, str], PropertyInfo(alias="envVars")]

    memory_limit_mb: Annotated[int, PropertyInfo(alias="memoryLimitMb")]

    timeout_ms: Annotated[int, PropertyInfo(alias="timeoutMs")]


class CodeAssertion(TypedDict, total=False):
    code: Required[str]

    language: Required[str]

    expected_output: Annotated[str, PropertyInfo(alias="expectedOutput")]

    options: CodeAssertionOptions


class LlmAssertionEvaluateOptions(TypedDict, total=False):
    delay: int

    max_concurrency: Annotated[int, PropertyInfo(alias="maxConcurrency")]

    repeat: int


class LlmAssertion(TypedDict, total=False):
    prompts: Required[SequenceNotStr[str]]

    providers: Required[Iterable[ProviderParam]]

    evaluate_options: Annotated[LlmAssertionEvaluateOptions, PropertyInfo(alias="evaluateOptions")]

    llm_evaluator_prompt: Annotated[str, PropertyInfo(alias="llmEvaluatorPrompt")]


class AssertionParam(TypedDict, total=False):
    assertion_type: Required[
        Annotated[
            Literal["ASSERTION_TYPE_UNSPECIFIED", "ASSERTION_TYPE_LLM", "ASSERTION_TYPE_CODE"],
            PropertyInfo(alias="assertionType"),
        ]
    ]

    code_assertion: Annotated[CodeAssertion, PropertyInfo(alias="codeAssertion")]

    llm_assertion: Annotated[LlmAssertion, PropertyInfo(alias="llmAssertion")]

    metric_name: Annotated[str, PropertyInfo(alias="metricName")]
