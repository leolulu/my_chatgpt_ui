from datetime import datetime
import openai


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
        self.add_system_msg(
            f"You are ChatGPT, a large language model trained by OpenAI.\nKnowledge cutoff: 2021-09\nCurrent date: [{datetime.now().strftime('%Y-%m')}]"
        )
        self.add_user_msg(f"你接下来的回答，都尽量采用markdown的格式进行回答，应该这样的可读性更好，尽可能多用用markdown的列表、表格等高级特性")
        self.add_assistant_msg(f"收到，我会尽可能多用markdown的高级格式进行回答")

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

    def ask(self, question, model="gpt-3.5-turbo-16k-0613"):
        self.add_user_msg(question)
        response = self.openai.ChatCompletion.create(model=model, messages=self.messages)
        answer = response["choices"][0]["message"]["content"]  # type: ignore
        usage = response["usage"]  # type: ignore
        self.add_assistant_msg(answer)
        return (answer, usage)
