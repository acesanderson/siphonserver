from typing import Optional
from collections.abc import Iterable
import asyncio
from SiphonServer.server.api.requests import BatchRequest  # your class
from Chain.model.model_async import ModelAsync
from Chain.parser.parser import Parser
from Chain.chain.chain import Prompt
from Chain.progress.verbosity import Verbosity
from Chain.result.result import ChainResult
from Chain.result.error import ChainError


async def chain_async_service(
    model: ModelAsync,
    batch: BatchRequest,
    *,
    prompt: Optional[Prompt] = None,  # required if using input_variables_list
    parser: Optional[Parser] = None,
    max_concurrency: Optional[int] = None,
    cache: bool = True,
    verbose: Verbosity = Verbosity.SILENT,
    print_response: bool = False,
) -> list[ChainResult]:
    """
    Normalize BatchRequest into a list of query_async coroutines and execute them.
    Preserves order; maps unexpected exceptions to ChainError.
    """
    raise NotImplementedError(
        "This function is not implemented in this context. Please implement it in your application."
    )
    # # 1) Normalize to prompt strings
    # if batch.prompt_strings:
    #     prompts: Iterable[str] = batch.prompt_strings
    # else:
    #     if prompt is None:
    #         raise ValueError(
    #             "BatchRequest contains input_variables_list but no Prompt was provided."
    #         )
    #     prompts = (
    #         prompt.render(input_variables=iv) for iv in batch.input_variables_list
    #     )
    #
    # # 2) Build coroutines with optional concurrency control
    # sem = asyncio.Semaphore(max_concurrency) if max_concurrency else None
    #
    # async def call(q: str) -> ChainResult:
    #     async def _invoke():
    #         return await model.query_async(
    #             query_input=q,
    #             response_model=(parser.pydantic_model if parser else None),
    #             cache=cache,
    #             verbose=verbose,
    #             print_response=print_response,
    #         )
    #
    #     if sem:
    #         async with sem:
    #             return await _invoke()
    #     return await _invoke()
    #
    # coros = [call(q) for q in prompts]
    #
    # # 3) Run and coerce unexpected exceptions to ChainError
    # results = await asyncio.gather(*coros, return_exceptions=True)
    # out: list[ChainResult] = []
    # for r in results:
    #     if isinstance(r, Exception):
    #         out.append(
    #             ChainError.from_exception(
    #                 r, code="async_batch_error", category="server"
    #             )
    #         )
    #     else:
    #         out.append(r)
    # return out
