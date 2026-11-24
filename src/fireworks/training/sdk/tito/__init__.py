"""Exact-token multi-turn rollout contracts and environment-local sidecar."""

from fireworks.training.sdk.tito._types import (
    TITOTurn,
    TITOError,
    TITORenderer,
    TITOCallRecord,
    TITOCallResult,
    TITOParseError,
    TITOPromptMode,
    TITOChatRequest,
    TITODistribution,
    TITOMetricSummary,
    TITOSegmentResult,
    TITOParsedAssistant,
    TITOResponseAttempt,
    TITOIncrementalPrompt,
    TITOMalformedToolCall,
    TrajectoryDriftPolicy,
    TITOTrajectoryArtifact,
    TITOTrajectoryEndpoint,
    TITOIncrementalRenderer,
    normalize_openai_tool_arguments,
)
from fireworks.training.sdk.tito._engine import TITOEventObserver
from fireworks.training.sdk.tito._sidecar import TITOSidecar
from fireworks.training.sdk.tito._failure_trace import TITOFailureTraceConfig, dump_tito_failure_trace
from fireworks.training.sdk.tito._phase_metrics import TITORolloutPhaseMetrics

__all__ = [
    "TITOCallRecord",
    "TITOCallResult",
    "TITOChatRequest",
    "TITODistribution",
    "TITOError",
    "TITOParseError",
    "TITOFailureTraceConfig",
    "dump_tito_failure_trace",
    "TITOEventObserver",
    "TITOIncrementalPrompt",
    "TITOIncrementalRenderer",
    "TITOMetricSummary",
    "TITOParsedAssistant",
    "TITOMalformedToolCall",
    "TITOPromptMode",
    "TITORenderer",
    "TITORolloutPhaseMetrics",
    "TITOResponseAttempt",
    "TITOSegmentResult",
    "TITOSidecar",
    "TITOTrajectoryEndpoint",
    "TITOTrajectoryArtifact",
    "TITOTurn",
    "TrajectoryDriftPolicy",
    "normalize_openai_tool_arguments",
]
