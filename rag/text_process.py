from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader,PyMuPDFLoader
from langchain_community.vectorstores import FAISS
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

class TextProcessor:
  def __init__(self):
    self.db = None
    self.embeddings = None

  # 仅支持txt、md、pdf、docx格式的文件
  def file_loader(self, file_path: str) -> str:
    try:
      suffix = file_path.split(".")[-1]
      if suffix not in ["txt", "md", "pdf", "docx"]:
        raise ValueError(f"不支持的文件格式: {suffix}")
      if(suffix == "txt" or suffix == "md"):
        loader = TextLoader(file_path, encoding="utf-8")
      elif(suffix == "pdf"):
        loader = PyMuPDFLoader(file_path)
        # loader = PyPDFLoader(file_path, mode="single")
      elif(suffix == "docx"):
        loader = Docx2txtLoader(file_path)
      else:
        raise ValueError(f"不支持的文件格式: {suffix}")
      content = loader.load()[0].page_content
      return content
    except Exception as e:
      raise ValueError(f"文件加载失败: {e}")

  # 文本清洗
  def clean_text(self, text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9\.,;:，。；：、 ]", "", text)
    return text.strip()
  
  
# 文本分片
  def text_splitter(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 150) -> list:
    text_split = RecursiveCharacterTextSplitter(
      chunk_size=chunk_size,
      chunk_overlap=chunk_overlap,
      # 优先按语义单位分割，而不是生硬地按字符数切割
      separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""],
    )
    return text_split.create_documents([text])

