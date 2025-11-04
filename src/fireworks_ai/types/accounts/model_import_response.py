# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ModelImportResponse", "Error", "ErrorDetail", "Metadata", "Response"]


class ErrorDetail(BaseModel):
    type: Optional[str] = FieldInfo(alias="@type", default=None)
    """
    A URL/resource name that uniquely identifies the type of the serialized protocol
    buffer message. This string must contain at least one "/" character. The last
    segment of the URL's path must represent the fully qualified name of the type
    (as in `path/google.protobuf.Duration`). The name should be in a canonical form
    (e.g., leading "." is not accepted).

    In practice, teams usually precompile into the binary all types that they expect
    it to use in the context of Any. However, for URLs which use the scheme `http`,
    `https`, or no scheme, one can optionally set up a type server that maps type
    URLs to message definitions as follows:

    - If no scheme is provided, `https` is assumed.
    - An HTTP GET on the URL must yield a [google.protobuf.Type][] value in binary
      format, or produce an error.
    - Applications are allowed to cache lookup results based on the URL, or have
      them precompiled into a binary to avoid any lookup. Therefore, binary
      compatibility needs to be preserved on changes to types. (Use versioned type
      names to manage breaking changes.)

    Note: this functionality is not currently available in the official protobuf
    release, and it is not used for type URLs beginning with type.googleapis.com.

    Schemes other than `http`, `https` (or the empty scheme) might be used with
    implementation specific semantics.
    """

    if TYPE_CHECKING:
        # Some versions of Pydantic <2.8.0 have a bug and don’t allow assigning a
        # value to this field, so for compatibility we avoid doing it at runtime.
        __pydantic_extra__: Dict[str, object] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]

        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...
    else:
        __pydantic_extra__: Dict[str, object]


class Error(BaseModel):
    code: Optional[int] = None
    """
    The status code, which should be an enum value of
    [google.rpc.Code][google.rpc.Code].
    """

    details: Optional[List[ErrorDetail]] = None
    """A list of messages that carry the error details.

    There is a common set of message types for APIs to use.
    """

    message: Optional[str] = None
    """A developer-facing error message, which should be in English.

    Any user-facing error message should be localized and sent in the
    [google.rpc.Status.details][google.rpc.Status.details] field, or localized by
    the client.
    """


class Metadata(BaseModel):
    type: Optional[str] = FieldInfo(alias="@type", default=None)
    """
    A URL/resource name that uniquely identifies the type of the serialized protocol
    buffer message. This string must contain at least one "/" character. The last
    segment of the URL's path must represent the fully qualified name of the type
    (as in `path/google.protobuf.Duration`). The name should be in a canonical form
    (e.g., leading "." is not accepted).

    In practice, teams usually precompile into the binary all types that they expect
    it to use in the context of Any. However, for URLs which use the scheme `http`,
    `https`, or no scheme, one can optionally set up a type server that maps type
    URLs to message definitions as follows:

    - If no scheme is provided, `https` is assumed.
    - An HTTP GET on the URL must yield a [google.protobuf.Type][] value in binary
      format, or produce an error.
    - Applications are allowed to cache lookup results based on the URL, or have
      them precompiled into a binary to avoid any lookup. Therefore, binary
      compatibility needs to be preserved on changes to types. (Use versioned type
      names to manage breaking changes.)

    Note: this functionality is not currently available in the official protobuf
    release, and it is not used for type URLs beginning with type.googleapis.com.

    Schemes other than `http`, `https` (or the empty scheme) might be used with
    implementation specific semantics.
    """

    if TYPE_CHECKING:
        # Some versions of Pydantic <2.8.0 have a bug and don’t allow assigning a
        # value to this field, so for compatibility we avoid doing it at runtime.
        __pydantic_extra__: Dict[str, object] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]

        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...
    else:
        __pydantic_extra__: Dict[str, object]


class Response(BaseModel):
    type: Optional[str] = FieldInfo(alias="@type", default=None)
    """
    A URL/resource name that uniquely identifies the type of the serialized protocol
    buffer message. This string must contain at least one "/" character. The last
    segment of the URL's path must represent the fully qualified name of the type
    (as in `path/google.protobuf.Duration`). The name should be in a canonical form
    (e.g., leading "." is not accepted).

    In practice, teams usually precompile into the binary all types that they expect
    it to use in the context of Any. However, for URLs which use the scheme `http`,
    `https`, or no scheme, one can optionally set up a type server that maps type
    URLs to message definitions as follows:

    - If no scheme is provided, `https` is assumed.
    - An HTTP GET on the URL must yield a [google.protobuf.Type][] value in binary
      format, or produce an error.
    - Applications are allowed to cache lookup results based on the URL, or have
      them precompiled into a binary to avoid any lookup. Therefore, binary
      compatibility needs to be preserved on changes to types. (Use versioned type
      names to manage breaking changes.)

    Note: this functionality is not currently available in the official protobuf
    release, and it is not used for type URLs beginning with type.googleapis.com.

    Schemes other than `http`, `https` (or the empty scheme) might be used with
    implementation specific semantics.
    """

    if TYPE_CHECKING:
        # Some versions of Pydantic <2.8.0 have a bug and don’t allow assigning a
        # value to this field, so for compatibility we avoid doing it at runtime.
        __pydantic_extra__: Dict[str, object] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]

        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...
    else:
        __pydantic_extra__: Dict[str, object]


class ModelImportResponse(BaseModel):
    done: Optional[bool] = None
    """
    If the value is `false`, it means the operation is still in progress. If `true`,
    the operation is completed, and either `error` or `response` is available.
    """

    error: Optional[Error] = None
    """The error result of the operation in case of failure or cancellation."""

    metadata: Optional[Metadata] = None
    """Service-specific metadata associated with the operation.

    It typically contains progress information and common metadata such as create
    time. Some services might not provide such metadata. Any method that returns a
    long-running operation should document the metadata type, if any.
    """

    name: Optional[str] = None
    """
    The server-assigned name, which is only unique within the same service that
    originally returns it. If you use the default HTTP mapping, the `name` should be
    a resource name ending with `operations/{unique_id}`.
    """

    response: Optional[Response] = None
    """The normal, successful response of the operation.

    If the original method returns no data on success, such as `Delete`, the
    response is `google.protobuf.Empty`. If the original method is standard
    `Get`/`Create`/`Update`, the response should be the resource. For other methods,
    the response should have the type `XxxResponse`, where `Xxx` is the original
    method name. For example, if the original method name is `TakeSnapshot()`, the
    inferred response type is `TakeSnapshotResponse`.
    """
