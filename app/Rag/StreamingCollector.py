from langchain_classic .callbacks.base import BaseCallbackHandler
from langchain_core.messages import AIMessage

class StreamingCollector(BaseCallbackHandler):
    def __init__(self):
        self.buffer = ""

    def on_llm_new_token(self, token, **kwargs):
        self.buffer += token

    def get_ai_message(self):
        return AIMessage(content=self.buffer)
