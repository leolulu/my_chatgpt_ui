class Prompt:
    ID = "id"
    PROMPT = "prompt"

    def __init__(self, id: int, prompt: str) -> None:
        self.id = id
        self.prompt = prompt

    @property
    def value(self):
        return {Prompt.ID: self.id, Prompt.PROMPT: self.prompt}
