"""
Wrapper script for the various enrichment scripts. (title, description, summary)
"""

from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.data.SyntheticData import SyntheticData
from Siphon.enrich.generate_title import generate_title
from Siphon.enrich.generate_description import generate_description
from Siphon.enrich.generate_summary import generate_summary


def enrich_content(processed_content: ProcessedContent, model: str = "cogito:32b") -> SyntheticData:
    """
    Enrich the processed content with title, description, and summary.
    Returns a SyntheticData object containing all enrichments.
    """

    # Generate title
    print("Generating title...")
    try:
        title = generate_title(processed_content, model=model)
    except Exception as e:
        raise Exception(f"Failed to generate title: {e}")
    
    # Generate description
    print("Generating description...")
    try:
        description = generate_description(processed_content, model=model)
    except Exception as e:
        raise Exception(f"Failed to generate description: {e}")
    
    # Generate summary
    print("Generating summary...")
    try:
        summary = generate_summary(processed_content, model=model)
    except Exception as e:
        raise Exception(f"Failed to generate summary: {e}")

    # Create synthetic data object with all enrichments
    synthetic_data = SyntheticData(
        title=title,
        description=description,
        summary=summary,
        topics=[],
        entities=[],
    )

    return synthetic_data

    
if __name__ == "__main__":
    from Siphon.tests.fixtures.example_ProcessedContent import content
    syntheticdata = enrich_content(content)
    print(syntheticdata.model_dump_json(indent=2))
