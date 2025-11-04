# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["VersionListParams"]


class VersionListParams(TypedDict, total=False):
    account_id: Required[str]

    filter: str
    """
    Only deployment shape versions satisfying the provided filter (if specified)
    will be returned. See https://google.aip.dev/160 for the filter grammar.
    """

    order_by: Annotated[str, PropertyInfo(alias="orderBy")]
    """A comma-separated list of fields to order by.

    e.g. "foo,bar" The default sort order is ascending. To specify a descending
    order for a field, append a " desc" suffix. e.g. "foo desc,bar" Subfields are
    specified with a "." character. e.g. "foo.bar" If not specified, the default
    order is by "create_time".
    """

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]
    """The maximum number of deployment shape versions to return.

    The maximum page_size is 200, values above 200 will be coerced to 200. If
    unspecified, the default is 50.
    """

    page_token: Annotated[str, PropertyInfo(alias="pageToken")]
    """A page token, received from a previous ListDeploymentShapeVersions call.

    Provide this to retrieve the subsequent page. When paginating, all other
    parameters provided to ListDeploymentShapeVersions must match the call that
    provided the page token.
    """

    read_mask: Annotated[str, PropertyInfo(alias="readMask")]
    """The fields to be returned in the response.

    If empty or "\\**", all fields will be returned.
    """
