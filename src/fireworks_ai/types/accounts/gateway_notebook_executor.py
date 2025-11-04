# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GatewayNotebookExecutor"]


class GatewayNotebookExecutor(BaseModel):
    notebook_filename: str = FieldInfo(alias="notebookFilename")
    """Path to a notebook file to be executed."""
