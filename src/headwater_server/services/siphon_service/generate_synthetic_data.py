from headwater_api.classes import SyntheticDataRequest, SyntheticData


def generate_synthetic_data(
    request: SyntheticDataRequest,
) -> SyntheticData:
    """
    Generate synthetic data based on the provided request.
    This function simulates the generation of synthetic data such as titles, summaries, and descriptions.
    """
    context = request.context
    model = request.model
    server_side = True

    # Run your existing sync function in a thread pool
    synthetic_data = SyntheticData.from_context(
        context=context, cloud=False, model_str=model, server_side=server_side
    )
    return synthetic_data
