from env_utils import DOUBAO_API_KEY, DOUBAO_BASE_URL, DOUBAO_MODEL, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
  temperature=0,
  # api_key=DEEPSEEK_API_KEY,
  # base_url=DEEPSEEK_BASE_URL,
  # model=DEEPSEEK_MODEL,

  api_key = DOUBAO_API_KEY,
  base_url = DOUBAO_BASE_URL,
  model = DOUBAO_MODEL,
  streaming=True,
  verbose=True  # 打开调试模式
)
