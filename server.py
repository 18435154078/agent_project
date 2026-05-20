from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from langchain.agents import create_agent, AgentState
from langchain_core.messages import SystemMessage, ChatMessage
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langgraph.store.memory import InMemoryStore  # 核心存储
from langgraph.checkpoint.memory import InMemorySaver  # 会话管理

from langchain_core.tools import BaseTool,tool
from uvicorn import run
from model import llm
from typing import List
import asyncio

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

    self.tools = []
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
      checkpointer=self.checkpointer,
      # debug=True
    )
    self.agent = agent

  def chat(self, message: str, thread_id: str = "user123"):
    res = self.agent.invoke({"messages": [("user", message)]}, config={"configurable": {"thread_id": thread_id}})
    print(res)
    return res['messages'][-1].content

  async def chat_stream(self, message: str, websocket: WebSocket):
    res = self.agent.stream({
      "messages": [{'role': 'user', 'content': message}]
    }, config={"configurable": {"thread_id": "user123"}}, stream_mode="messages")

    for chunk in res:
      content = chunk[0].content
      if(content != ""):
        print(content)
        await websocket.send_text(content)
        await asyncio.sleep(0.05)


master = Master()

@app.get("/")
async def root():
  return {"message": "Hello World"}

@app.post("/chat")
async def chat(message: str):
  return master.chat(message)

@app.websocket("/chat_stream")
async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()
  while True:
    try:
      # 流式输出
      message =  await websocket.receive_text()
      
      print('开始流式输出')
      await master.chat_stream(message, websocket)

    except WebSocketDisconnect:
      print("Client disconnected")
      break


if __name__ == "__main__":
  run(app, host="0.0.0.0", port=8000)
