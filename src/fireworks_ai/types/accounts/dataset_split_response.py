# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["DatasetSplitResponse"]


class DatasetSplitResponse(BaseModel):
    chunk_dataset_names: Optional[List[str]] = FieldInfo(alias="chunkDatasetNames", default=None)

    chunks_created: Optional[int] = FieldInfo(alias="chunksCreated", default=None)

    total_examples: Optional[str] = FieldInfo(alias="totalExamples", default=None)
