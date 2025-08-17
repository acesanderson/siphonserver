from SiphonServer.server.api.requests import SyntheticDataRequest
from Siphon.data.SyntheticData import SyntheticData


def generate_synthetic_data(request: SyntheticDataRequest) -> SyntheticData:
    """
    Generate synthetic data based on the provided request.
    This function simulates the generation of synthetic data such as titles, summaries, and descriptions.
    """
    context = request.context
    model = request.model
    # Currently only handles text
    synthetic_data = SyntheticData.from_context(context=context, model_str=model)
    return synthetic_data
