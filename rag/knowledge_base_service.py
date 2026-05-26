from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import LLMChainExtractor
from langchain_community.vectorstores import FAISS
from fastapi.responses import StreamingResponse
from openai import OpenAI
from typing import List
import os
import json
from rag.prompt import prompt
from core.config import settings
from model import llm
from core.logger import logger
from utils.qwen_embeddings import CustomQwenEmbeddings
from memory.redis_conn import save_message, get_history
from rag.text_process import TextProcessor


class KnowledgeBaseService:
  _prompt: ChatPromptTemplate
  _embeddings: OpenAI
  _llm: OpenAI
  _db: FAISS
  _text_processor: TextProcessor

  def __new__(cls):
    # 单例模式，确保全局只有一个RAGRService实例，避免重复加载向量数据库
    if not hasattr(cls, "_instance"):
      cls._instance = super(KnowledgeBaseService, cls).__new__(cls)
      cls._instance._prompt = prompt
      cls._instance._llm = llm
      cls._instance._text_processor = TextProcessor()
      cls._instance._init_embeddings()
      cls._instance._init_db()
    return cls._instance

  def _init_embeddings(self):
    client = OpenAI(
      api_key=settings.QWEN_API_KEY,
      base_url=settings.QWEN_BASE_URL
    )
    self._embeddings = CustomQwenEmbeddings(
      client=client,
      model=settings.QWEN_EMBEDDING_MODEL
    )

  def _init_db(self):
    if os.path.exists(settings.CHROMA_DB_DIR):
      try:
        self._db = FAISS.load_local(
          settings.CHROMA_DB_DIR,
          self._embeddings,
          allow_dangerous_deserialization=True
        )
      except Exception as e:
        logger.error(f"加载向量数据库时发生错误: {e}")
        self._db = None
    else:
      self._db = None

  # 向量数据库存储
  def _add_chunks_to_db(self, chunks: list):
    try:
      if self._db == None:
        self._db = self._db.from_documents(chunks, self._embeddings)
      else:
        self._db = self._db.add_documents(chunks)
      self._db.save_local(settings.CHROMA_DB_DIR)
    except Exception as e:
      raise logger.error(f"存储向量数据库时发生错误: {e}")  


  def upload_file(self, file_path: str):  # 整个流程：加载文件 -> 文本清洗 -> 文本分片 -> 存储向量数据库
    # 文档加载
    content = self._text_processor.file_loader(file_path)
    logger.info(f"文件 {file_path} 加载成功，内容长度: {len(content)}")
    # 文档清洗
    content = self._text_processor.clean_text(content)
    logger.info(f"文件 {file_path} 清洗成功，内容长度: {len(content)}")

    # 文档分片
    chunks = self._text_processor.text_splitter(content)
    # ✅ 给每个分片加上元数据
    file_name = os.path.basename(file_path)
    for i, chunk in enumerate(chunks):
      chunk.metadata = {"file_name": file_name, "chunk_index": i, "chunk_length": len(chunk.page_content), "total_chunks": len(chunks)}

    logger.info(f"文件 {file_path} 分片成功，分片数量: {len(chunks)}")

    # 向量数据库存储
    self._add_chunks_to_db(chunks)
    logger.info(f"文件 {file_path} 存储向量数据库成功")


  def _prepare_prompt(self, question: str, session_id: str) -> str:

    # 1. 从向量数据库获取相关文档
    base_retriever  = self._db.as_retriever(
      search_type="mmr",
      search_kwargs={"k": 1, "fetch_k": 20, "score_threshold": 0.7}
    )

    # 上下文压缩检索
    retriever = ContextualCompressionRetriever(
        base_compressor=LLMChainExtractor.from_llm(self._llm),
        base_retriever=base_retriever
    )

    # 获取历史对话
    save_message(session_id, "user", question)
    # 保存用户消息到Redis
    messages = get_history(session_id)
    history = []
    for line in reversed(messages):
      role, content = line.split(":", 1)
      if role == "user":
        history.append(HumanMessage(content=content))
      elif role == "assistant":
        history.append(AIMessage(content=content))

    docs = retriever.invoke(question)
    context = '\n\n'.join([doc.page_content for doc in docs])
    
    # 2. 构造提示词，调用大模型
    return self._prompt.format(context=context, question=question, history=history)


  def chat(self, question: str, session_id: str):
    if self._db == None:
      return {
        "code": 500,
        "msg": "向量数据库未初始化，请先上传文件进行知识库构建"
      }
    prepare_prompt = self._prepare_prompt(question, session_id)
    print(prepare_prompt)
    response = self._llm.invoke(prepare_prompt)
    content = response.content
    save_message(session_id, "assistant", content)
    return content
  
  def chat_stream(self, question: str, session_id: str):
    if self._db == None:
      return {
        "code": 500,
        "msg": "向量数据库未初始化，请先上传文件进行知识库构建"
      }
    prepare_prompt = self._prepare_prompt(question, session_id)
    # 3. 流式返回
    async def generate():
        response_content = ""
        async for chunk in self._llm.astream(prepare_prompt):
            if chunk.content:
                response_content += chunk.content
                yield f"data: {json.dumps({'content': chunk.content}, ensure_ascii=False)}\n\n"
        # 保存AI回复到Redis
        save_message(session_id, "assistant", response_content)
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

knowledge_base_service = KnowledgeBaseService()
