from fastapi import FastAPI
from langserve import add_routes
from langchain_core.prompts import PromptTemplate
from langchain.agents import create_agent
from langchain_core.tools import BaseTool
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from typing import List
import uvicorn
from model import llm

app = FastAPI()

@tool
def search(query: str) -> str:
  """搜索"""
  return f"搜索结果：{query}"

class Master:
  # 单例
  instance = None
  system_prompt: SystemMessage
  tools: List[BaseTool]
  store: InMemoryStore
  def __init__(self):

    self.tools = [search]
    self.store = InMemoryStore()
    self.checkpointer = InMemorySaver()
    self.system_prompt = SystemMessage(content='你是一个专业的但是脾气又很暴躁的助手，经常讲粗话，请简要回答用户问题。')
    self.initAgent()

  def __new__(cls):
      if not hasattr(cls, 'instance') or cls.instance is None:
          cls.instance = super().__new__(cls)
      return cls.instance
  
  def initAgent(self):
    agent= create_agent(
      model=llm,
      system_prompt=self.system_prompt,
      tools=self.tools,
      store=self.store,
      # checkpointer=self.checkpointer,
      # debug=True
    )
    self.agent = agent


master = Master()
add_routes(
  app, 
  master.agent, 
  path='/chat', 
  enabled_endpoints=['invoke', 'stream']
)

# prompt = PromptTemplate.from_template("请简要回答用户问题。")
# add_routes(
#   app, 
#   prompt | llm,
#   path='/chat',
#   enabled_endpoints=['invoke', 'stream'],  # 只开启invoke和stream
#   include_schema=False,  # 关闭 input/output/config schema 接口
#   include_playground=False,  # 关闭 /chat/playground 调试页
# )

if __name__ == "__main__":
  uvicorn.run(app, host="127.0.0.1", port=8000)