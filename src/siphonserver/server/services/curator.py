from mentor.curator.curate import Curate
from siphonserver.server.api.requests import CuratorRequest


def curate_service(request: CuratorRequest) -> tuple:
    """
    Process a CuratorRequest and return the curation results.
    """
    results = Curate(**request.model_dump())
    return results


if __name__ == "__main__":
    sample_request = CuratorRequest(query_string="pivoting your career")
    response = curate_service(sample_request)
    print(response)
