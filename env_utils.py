import os
from dotenv import load_dotenv

load_dotenv()

DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
DOUBAO_BASE_URL = os.getenv("DOUBAO_BASE_URL")
DOUBAO_MODEL = os.getenv("DOUBAO_MODEL")


DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL")



