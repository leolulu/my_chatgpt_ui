import openai
import tiktoken


class OpenAIEngine:
    def __init__(self) -> None:
        self.openai = openai
        self.reset_messages()

    def init_engine(self, api_key, proxy=None):
        self.openai.api_key = api_key
        if proxy:
            self.openai.proxy = proxy

    def reset_messages(self):
        self.messages = []

    def add_system_msg(self, content):
        self.messages.append(
            {"role": "system", "content": content},
        )

    def add_user_msg(self, content):
        self.messages.append(
            {"role": "user", "content": content},
        )

    def add_assistant_msg(self, content):
        self.messages.append(
            {"role": "assistant", "content": content},
        )

    def ask(self, question, model="gpt-3.5-turbo-0613"):
        encoding = tiktoken.encoding_for_model(model)
        num_tokens = len(encoding.encode(question))
        if num_tokens > 1024 * 4:
            model = "gpt-3.5-turbo-16k-0613"
        print(f"Token num: {num_tokens}, use model: {model}")
        self.add_user_msg(question)
        response = self.openai.ChatCompletion.create(
            model=model, messages=self.messages
        )
        answer = response["choices"][0]["message"]["content"]  # type: ignore
        usage = response["usage"]  # type: ignore
        self.add_assistant_msg(answer)
        return (answer, usage)
