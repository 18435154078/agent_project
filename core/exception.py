from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from schemas.response import ApiResponse

# 全局异常捕获
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(
            content=ApiResponse(
                code=exc.status_code,
                msg=exc.detail,
                data=None
            ).model_dump(),
            status_code=exc.status_code
        )
    
    # 服务器未知错误
    return JSONResponse(
        content=ApiResponse(
            code=500,
            msg=f"服务器异常：{str(exc)}",
            data=None
        ).model_dump(),
        status_code=500
    )