from pathlib import Path
from Chain import Model, Chain, Prompt, Verbosity

# Get all text files in the prompts directory
texts = Path.cwd() / "prompts"
texts = texts.glob("*.txt")
# Get available models
models = Model.models()["ollama"]
models.remove("gpt-oss:120b")  # too large and slow for our purposes


# Generate dataclasses
class Text:
    """
    A Pydantic model to represent a text file.
    """

    def __init__(self, path: Path):
        self.name: str = path.stem
        self.content: str = path.read_text(encoding="utf-8")
        self.wordcount: int = len(self.content.split())


text_objs = []
for text in texts:
    text_obj = Text(text)
    text_objs.append(text_obj)

# Sort text_objs by wordcount
text_objs.sort(key=lambda x: x.wordcount, reverse=True)


prompt_str = """
You are a research assistant. Your task is to read a text and then answer the question.

Here is the text:
<text>
{{content}}
</text>

Here is the question:

<question>
What is the magic number mentioned in the text? Return the number only, without any additional text or formatting.
</question>
"""


def query_text(text: Text, model_str: str) -> str:
    """
    Queries the text with a question and returns the answer.
    """
    model = Model(model_str)
    prompt = Prompt(prompt_str)
    chain = Chain(model=model, prompt=prompt)
    response = chain.run(
        input_variables={"content": text.content}, verbose=Verbosity.DETAILED
    )
    return str(response.content).strip()


if __name__ == "__main__":
    model_str = "llama3.1:latest"
    for model_str in models:
        print(f"Using model: {model_str}")
        for text in text_objs:
            try:
                print(f"Querying text: {text.name} (wordcount: {text.wordcount})")
                answer = query_text(text, model_str)
                print(f"\tAnswer: {answer}\n")
            except Exception as e:
                print(f"\tError: {e}\n")
                pass
