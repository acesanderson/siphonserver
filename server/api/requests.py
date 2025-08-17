"""
ChainRequest,
BatchRequest,
SyntheticDataRequest,
"""

from Chain.request.request import Request as ChainRequest
from Siphon.data.Context import Context
from Siphon.context.context_classes import ContextUnion
from pydantic import BaseModel, Field, model_validator


class BatchRequest(ChainRequest):
    """
    BatchRequest extends ChainRequest to allow for multiple prompt strings or input variables.
    This is useful for processing multiple requests in a single API call.
    """

    prompt_strings: list[str] = Field(
        default_factory=list,
        description="List of prompt strings for each request. Prompt strings should be fully rendered.",
    )
    input_variables_list: list[dict[str, str]] = Field(
        default_factory=list,
        description="List of input variables for each request. Each dict should match the model's input schema.",
    )

    @model_validator(mode="after")
    def _exactly_one(
        self,
    ):  # for dataclass-style it’s self; for BaseModel it’s self in v2
        has_prompts = bool(self.prompt_strings)
        has_vars = bool(self.input_variables_list)
        if has_prompts == has_vars:
            raise ValueError(
                "Provide exactly one of 'prompt_strings' or 'input_variables_list'."
            )
        return self


class SyntheticDataRequest(BaseModel):
    context: ContextUnion  # Has all the content + metadata
    model: str = "gemini2.5"  # Model selection


Requests = {
    "ChainRequest": ChainRequest,
    "BatchRequest": BatchRequest,
    "SiphonSyntheticDataRequest": SyntheticDataRequest,
}
