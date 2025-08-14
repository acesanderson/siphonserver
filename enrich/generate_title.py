from pathlib import Path
from Chain import Model, Prompt, Chain
from Siphon.data.ProcessedContent import ProcessedContent

dir_path = Path(__file__).parent
prompts_dir = dir_path.parent / "prompts"
title_prompt_file = prompts_dir / "enrich_title.jinja2"

def generate_title(processed_content: ProcessedContent, model: str = "llama3.3:latest") -> str:
    # Get attributes from processed content
    uri = processed_content.uri
    llm_context = processed_content.llm_context
    input_variables = {"uri": uri, "llm_context": llm_context}
    # Build our chain
    prompt = Prompt(title_prompt_file.read_text())
    model_obj = Model(model)
    chain = Chain(prompt=prompt, model = model_obj)
    response = chain.run(input_variables=input_variables)
    # Return the generated title
    return str(response.content)

