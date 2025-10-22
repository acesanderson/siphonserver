from mentor.curator.curate import CurateAsync
from siphonserver.server.api.requests import CuratorRequest
from siphonserver.server.api.responses import CuratorResponse, CuratorResult


async def curate_service(request: CuratorRequest) -> CuratorResponse:
    """
    Process a CuratorRequest and return the curation results.
    """
    results = await CurateAsync(**request.model_dump())
    result_objs = []
    for res in results:
        result_objs.append(CuratorResult(id=res[0], score=res[1]))
    response = CuratorResponse(results=result_objs)
    return response
