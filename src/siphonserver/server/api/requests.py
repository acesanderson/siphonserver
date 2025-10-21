"""
ConduitRequest,
BatchRequest,
SyntheticDataRequest,
"""

from conduit.request.request import Request as ConduitRequest
from conduit.embeddings.chroma_batch import ChromaBatch
from siphon.context.context_classes import ContextUnion
from pydantic import BaseModel, Field, model_validator
from typing import Any


class BatchRequest(ConduitRequest):
    """
    BatchRequest extends ConduitRequest to allow for multiple prompt strings or input variables.
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
    prompt_str: str | None = Field(
        default=None, description="Single prompt string for the request."
    )

    @model_validator(mode="after")
    def _exactly_one(
        self,
    ):
        has_prompts = bool(self.prompt_strings)
        has_vars = bool(self.input_variables_list)
        if has_prompts == has_vars:
            raise ValueError(
                "Provide exactly one of 'prompt_strings' or 'input_variables_list'."
            )
        # If input_variables_list is provided, prompt_str should have a value
        if has_vars and not self.prompt_str:
            raise ValueError(
                "If 'input_variables_list' is provided, 'prompt_str' must also be provided."
            )
        return self


class SyntheticDataRequest(BaseModel):
    context: ContextUnion
    model: str = "gemini2.5"

    @model_validator(mode="before")
    @classmethod
    def deserialize_context(cls, data):
        if isinstance(data, dict) and "context" in data:
            context_data = data["context"]
            if isinstance(context_data, dict):
                # Reconstruct the right context class
                from siphon.context.context_classes import ContextClasses

                sourcetype_value = context_data.get("sourcetype")

                for context_class in ContextClasses:
                    if (
                        context_class.__name__.replace("Context", "")
                        == sourcetype_value
                    ):
                        data["context"] = context_class.model_validate(context_data)
                        break
        return data


class EmbeddingsRequest(BaseModel):
    model: str = Field(
        ...,
        description="The embedding model to use for generating embeddings.",
    )
    batch: ChromaBatch = Field(
        ...,
        description="Batch of documents to generate embeddings for.",
    )


Requests = {
    "ConduitRequest": ConduitRequest,
    "BatchRequest": BatchRequest,
    "SiphonSyntheticDataRequest": SyntheticDataRequest,
    "EmbeddingsRequest": EmbeddingsRequest,
}
