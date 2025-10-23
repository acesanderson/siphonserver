from headwater_server.curator_service.curate import Curate

if __name__ == "__main__":
    # Test the Curate function
    query = "Introduction to Machine Learning"
    results = Curate(query, k=5, n_results=20, model_name="bge", cached=True)
    for title, score in results:
        print(f"{title}: {score:.4f}")
