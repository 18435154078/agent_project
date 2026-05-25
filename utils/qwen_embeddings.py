from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, ConfigDict
from typing import List
from openai import OpenAI


class CustomQwenEmbeddings(Embeddings, BaseModel):
    client: OpenAI
    model: str
    # 允许 pydantic 序列化非标准类型
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """直接发送纯文本，不做任何额外处理"""
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]