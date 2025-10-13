#!/usr/bin/env python3
"""
模块管理CLI工具
"""
import asyncio
import sys
import logging
from pathlib import Path
import click

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.modules import registry
from app.modules.core import CoreModule
from app.modules.items import ItemsModule
from app.modules.tradingview import TradingViewModule
from app.modules.migration_manager import migration_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """模块管理CLI工具"""
    pass


@click.command()
def list_modules():
    """列出所有模块"""
    # 临时注册模块以获取信息
    registry.register_module("core", CoreModule())
    registry.register_module("items", ItemsModule())
    registry.register_module("tradingview", TradingViewModule())
    
    modules = registry.list_modules()
    
    click.echo("模块列表:")
    click.echo("-" * 50)
    for name, info in modules.items():
        status = "✅ 启用" if info['enabled'] else "❌ 禁用"
        migration_status = "有迁移" if info['has_migration'] else "无迁移"
        click.echo(f"{name:12} | {status} | {info['models_count']} 个模型 | {migration_status}")


@click.command()
@click.argument('module_name')
def enable_module(module_name):
    """启用模块"""
    # 注册所有模块
    registry.register_module("core", CoreModule())
    registry.register_module("items", ItemsModule())
    registry.register_module("tradingview", TradingViewModule())
    
    if registry.enable_module(module_name):
        click.echo(f"✅ 模块 {module_name} 已启用")
    else:
        click.echo(f"❌ 模块 {module_name} 启用失败")


@click.command()
@click.argument('module_name')
def disable_module(module_name):
    """禁用模块"""
    # 注册所有模块
    registry.register_module("core", CoreModule())
    registry.register_module("items", ItemsModule())
    registry.register_module("tradingview", TradingViewModule())
    
    if registry.disable_module(module_name):
        click.echo(f"✅ 模块 {module_name} 已禁用")
    else:
        click.echo(f"❌ 模块 {module_name} 禁用失败")


@click.command()
def migration_status():
    """查看迁移状态"""
    status = migration_manager.get_migration_status()
    
    click.echo("迁移状态:")
    click.echo("-" * 60)
    for module_name, info in status.items():
        click.echo(f"模块: {module_name}")
        click.echo(f"  已应用: {info['applied_count']} 个")
        click.echo(f"  待应用: {info['pending_count']} 个")
        if info['pending_migrations']:
            click.echo(f"  待应用迁移: {', '.join(info['pending_migrations'])}")
        click.echo()


@click.command()
@click.argument('module_name')
def migrate(module_name):
    """运行模块迁移"""
    if migration_manager.migrate_module(module_name):
        click.echo(f"✅ 模块 {module_name} 迁移完成")
    else:
        click.echo(f"❌ 模块 {module_name} 迁移失败")


@click.command()
def migrate_all():
    """运行所有模块迁移"""
    modules = ["core", "items", "tradingview"]
    results = migration_manager.migrate_all_modules(modules)
    
    for module_name, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        click.echo(f"{module_name}: {status}")


@click.command()
@click.argument('module_name')
@click.argument('migration_name')
def create_migration(module_name, migration_name):
    """创建新的迁移文件"""
    file_path = migration_manager.create_migration_file(module_name, migration_name)
    click.echo(f"✅ 迁移文件已创建: {file_path}")


@click.command()
@click.argument('module_name')
def test_module(module_name):
    """测试模块功能"""
    # 注册模块
    if module_name == "core":
        module = CoreModule()
    elif module_name == "items":
        module = ItemsModule()
    elif module_name == "tradingview":
        module = TradingViewModule()
    else:
        click.echo(f"❌ 未知模块: {module_name}")
        return
    
    registry.register_module(module_name, module)
    
    info = registry.get_module_info(module_name)
    if info:
        click.echo(f"✅ 模块 {module_name} 测试通过")
        click.echo(f"  路由数量: {len(info['router'].routes)}")
        click.echo(f"  模型数量: {len(info['models'])}")
        click.echo(f"  迁移路径: {info['migration_path']}")
    else:
        click.echo(f"❌ 模块 {module_name} 测试失败")


# 注册命令
cli.add_command(list_modules)
cli.add_command(enable_module)
cli.add_command(disable_module)
cli.add_command(migration_status)
cli.add_command(migrate)
cli.add_command(migrate_all)
cli.add_command(create_migration)
cli.add_command(test_module)


if __name__ == "__main__":
    cli()
