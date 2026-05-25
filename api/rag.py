from fastapi import APIRouter, UploadFile, File
from core.config import settings
import os
import uuid
from rag.knowledge_base_service import knowledge_base_service


router = APIRouter(tags=["文件上传"])

@router.post("/upload/file")
async def upload_file(file: UploadFile = File(...)):
    # 1. 用UUID生成唯一文件名，避免重名覆盖
    suffix = os.path.splitext(file.filename)[1]  # 获取原文件后缀
    file.filename = f"{uuid.uuid4().hex}{suffix}"
    file_location = os.path.join(settings.UPLOAD_DIR, file.filename)

    # 2. 保存文件到指定目录
    with open(file_location, "wb") as f:
      content = await file.read()
      f.write(content)

    try:
      # 3. 加载文件内容 -> 数据清洗 -> 分片 -> 存储向量数据库
      knowledge_base_service.upload_file(file_location)

      return {"code": 200, "msg": "文件上传并解析入库成功"}
    except Exception as e:
      return {"code": 500, "msg": str(e)}


