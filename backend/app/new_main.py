"""
新的模块化主应用文件
"""
import logging
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.modules import registry
from app.modules.core import CoreModule
from app.modules.items import ItemsModule
from app.modules.tradingview import TradingViewModule
from app.modules.migration_manager import migration_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("正在启动模块化FastAPI应用...")
    
    # 注册所有模块
    await initialize_modules()
    
    # 运行模块迁移
    await run_module_migrations()
    
    logger.info("应用启动完成")
    
    yield
    
    # 关闭时执行
    logger.info("正在关闭应用...")


async def initialize_modules():
    """初始化并注册所有模块"""
    logger.info("开始注册模块...")
    
    # 始终注册核心模块
    core_module = CoreModule()
    registry.register_module("core", core_module)
    
    # 根据配置注册其他模块
    enabled_modules = getattr(settings, 'ENABLED_MODULES', ["core", "items", "tradingview"])
    
    if "items" in enabled_modules:
        items_module = ItemsModule()
        registry.register_module("items", items_module)
        logger.info("Items模块已注册")
    
    if "tradingview" in enabled_modules:
        tradingview_module = TradingViewModule()
        registry.register_module("tradingview", tradingview_module)
        logger.info("TradingView模块已注册")
    
    logger.info(f"共注册了 {len(registry.modules)} 个模块")


async def run_module_migrations():
    """运行所有启用模块的迁移"""
    logger.info("开始运行模块迁移...")
    
    enabled_modules = [name for name, module in registry.modules.items() if module['enabled']]
    
    # 按依赖顺序运行迁移：core -> items -> tradingview
    migration_order = ["core", "items", "tradingview"]
    
    for module_name in migration_order:
        if module_name in enabled_modules:
            success = migration_manager.migrate_module(module_name)
            if success:
                logger.info(f"模块 {module_name} 迁移完成")
            else:
                logger.error(f"模块 {module_name} 迁移失败")
                raise RuntimeError(f"模块 {module_name} 迁移失败")


# Sentry配置
if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan
)

# 设置CORS
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
async def startup_event():
    """启动事件 - 注册所有启用模块的路由"""
    logger.info("注册模块路由...")
    
    # 获取所有启用的路由并注册
    for router in registry.get_active_routers():
        app.include_router(router, prefix=settings.API_V1_STR)
    
    logger.info(f"路由注册完成，共注册 {len(registry.get_active_routers())} 个路由器")


@app.get("/")
async def root():
    """根路径"""
    return {"message": "模块化FastAPI应用运行正常"}


@app.get("/modules")
async def list_modules():
    """列出所有模块信息"""
    return registry.list_modules()


@app.get("/modules/{module_name}")
async def get_module_info(module_name: str):
    """获取特定模块信息"""
    info = registry.get_module_info(module_name)
    if not info:
        return {"error": "模块未找到"}
    return info


@app.get("/migrations/status")
async def migration_status():
    """获取迁移状态"""
    return migration_manager.get_migration_status()
