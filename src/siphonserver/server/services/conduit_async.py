from siphonserver.server.api.requests import BatchRequest  # your class
from conduit.conduit.async_conduit import AsyncConduit
from conduit.model.model_async import ModelAsync
from conduit.prompt.prompt import Prompt
from conduit.progress.verbosity import Verbosity
from conduit.result.result import ConduitResult
from functools import partial
import asyncio
from concurrent.futures import ThreadPoolExecutor


async def conduit_async_service(
    batch: BatchRequest,
) -> list[ConduitResult]:
    """
    Normalize BatchRequest into a list of query_async coroutines and execute them.
    """
    model_str = batch.model
    prompt_str = batch.prompt_str
    input_variables_list = batch.input_variables_list
    prompt_strings = batch.prompt_strings
    model = ModelAsync(model_str)
    if prompt_str and input_variables_list:
        prompt = Prompt(prompt_str)
        conduit = AsyncConduit(model=model, prompt=prompt)
        func_for_executor = partial(
            conduit.run,
            input_variables_list=input_variables_list,
            verbose=Verbosity.PROGRESS,
        )
    elif prompt_strings:
        conduit = AsyncConduit(model=model)
        func_for_executor = partial(
            conduit.run,
            prompt_strings=prompt_strings,
            verbose=Verbosity.PROGRESS,
        )
    else:
        raise ValueError(
            "BatchRequest must contain either 'prompt_str' with 'input_variables_list' or 'prompt_strings'."
        )
    assert func_for_executor is not None, "Function for executor should not be None"
    # Run the following in a thread pool to avoid blocking the event loop
    ## conduit.run(input_variables_list=input_variables_list, verbosity=Verbosity.PROGRESS)
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        results = await loop.run_in_executor(
            executor,
            func_for_executor,
        )

    return results
