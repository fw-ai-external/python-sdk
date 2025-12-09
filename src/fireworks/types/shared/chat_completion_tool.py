# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ChatCompletionTool", "Function"]


class Function(BaseModel):
    """Required for function tools."""

    name: str
    """The name of the function to be called.

    Must be a-z, A-Z, 0-9, or contain underscores and dashes, with a maximum length
    of 64.
    """

    description: Optional[str] = None
    """
    A description of what the function does, used by the model to choose when and
    how to call the function.
    """

    parameters: Optional[Dict[str, object]] = None
    """The parameters the function accepts, described as a JSON Schema object.

    The JSON Schema object should have the following structure:

    ```json
    {
      "type": "object",
      "required": ["param1", "param2"],
      "properties": {
        "param1": {
          "type": "string",
          "description": "..."
        },
        "param2": {
          "type": "number",
          "description": "..."
        }
      }
    }
    ```

    - The `type` field must be `"object"`.
    - The `required` field is an array of strings indicating which parameters are
      required.
    - The `properties` field is a map of property names to their definitions, where
      each property is an object with `type` (string) and `description` (string)
      fields.

    To describe a function that accepts no parameters, provide the value:

    ```json
    { "type": "object", "properties": {} }
    ```
    """

    strict: Optional[bool] = None


class ChatCompletionTool(BaseModel):
    type: Literal["function"]
    """The type of the tool. Currently, only `function` is supported."""

    function: Optional[Function] = None
    """Required for function tools."""
