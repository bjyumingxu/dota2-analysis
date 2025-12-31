"""FastAPI应用入口文件."""

import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

# 必须先导入日志配置，这样日志系统才会初始化
import src.core.logging  # noqa: F401

from src.core.config import settings
from src.api.v1.router import api_router, lifespan

# 在日志配置加载后获取logger
logger = logging.getLogger("src")

# 请求日志中间件
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        # 使用print和logger双重输出，确保能看到
        print(f"📥 收到请求: {request.method} {request.url.path}")
        logger.info(f"📥 收到请求: {request.method} {request.url.path}")
        logger.info(f"   查询参数: {dict(request.query_params)}")
        logger.info(f"   完整URL: {request.url}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            print(f"📤 响应: {response.status_code} (耗时: {process_time:.2f}秒)")
            logger.info(f"📤 响应: {response.status_code} (耗时: {process_time:.2f}秒)")
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"❌ 请求处理出错: {e} (耗时: {process_time:.2f}秒)", exc_info=True)
            raise

app = FastAPI(
    title="Dota2战绩分析API",
    description="提供Dota2玩家战绩数据分析服务",
    version="0.1.0",
    lifespan=lifespan,
)

# 添加请求日志中间件（最先添加，这样能记录所有请求）
app.add_middleware(LoggingMiddleware)

# 配置CORS，允许前端跨域访问
cors_origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api")

# 确保日志配置已加载
import src.core.logging  # noqa: F401

# 重新获取logger（确保使用正确的配置）
logger = logging.getLogger("src")
logger.info("🚀 FastAPI应用启动完成，日志系统已初始化")


@app.get("/")
async def root():
    """根路径."""
    return {"message": "Dota2战绩分析API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """健康检查."""
    print("💚 健康检查被调用 - print输出")
    logger.info("💚 健康检查被调用 - logger输出")
    return {"status": "ok"}

