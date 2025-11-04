# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .provider import Provider
from ..._models import BaseModel

__all__ = ["Assertion", "CodeAssertion", "CodeAssertionOptions", "LlmAssertion", "LlmAssertionEvaluateOptions"]


class CodeAssertionOptions(BaseModel):
    env_vars: Optional[Dict[str, str]] = FieldInfo(alias="envVars", default=None)

    memory_limit_mb: Optional[int] = FieldInfo(alias="memoryLimitMb", default=None)

    timeout_ms: Optional[int] = FieldInfo(alias="timeoutMs", default=None)


class CodeAssertion(BaseModel):
    code: str

    language: str

    expected_output: Optional[str] = FieldInfo(alias="expectedOutput", default=None)

    options: Optional[CodeAssertionOptions] = None


class LlmAssertionEvaluateOptions(BaseModel):
    delay: Optional[int] = None

    max_concurrency: Optional[int] = FieldInfo(alias="maxConcurrency", default=None)

    repeat: Optional[int] = None


class LlmAssertion(BaseModel):
    prompts: List[str]

    providers: List[Provider]

    evaluate_options: Optional[LlmAssertionEvaluateOptions] = FieldInfo(alias="evaluateOptions", default=None)

    llm_evaluator_prompt: Optional[str] = FieldInfo(alias="llmEvaluatorPrompt", default=None)


class Assertion(BaseModel):
    assertion_type: Literal["ASSERTION_TYPE_UNSPECIFIED", "ASSERTION_TYPE_LLM", "ASSERTION_TYPE_CODE"] = FieldInfo(
        alias="assertionType"
    )

    code_assertion: Optional[CodeAssertion] = FieldInfo(alias="codeAssertion", default=None)

    llm_assertion: Optional[LlmAssertion] = FieldInfo(alias="llmAssertion", default=None)

    metric_name: Optional[str] = FieldInfo(alias="metricName", default=None)
