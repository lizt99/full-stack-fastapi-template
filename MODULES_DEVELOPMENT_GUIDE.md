# 模块开发指南

## 📋 必读文档

在开始任何模块开发工作之前，**必须仔细阅读**以下核心规范文档：

### 🚨 主要规范文件
- **[rst-ai-core-modules-rules.mdc](./.cursor/rules/rst-ai-core-modules-rules.mdc)** - **严格的模块开发规范** ⚠️ **强制遵守**

### 📚 参考文档
- [API测试总结](./backend/API_TEST_SUMMARY.md) - API测试实现指南
- [测试问题修复](./backend/TESTING_ISSUES_FIXES.md) - 常见问题解决方案
- [模块化架构文档](./backend/MODULAR_ARCHITECTURE.md) - 架构设计说明

---

## 🚀 快速开始

### 1. 检查规范文件
```bash
# 查看完整规范 (715行详细规则)
cat .cursor/rules/rst-ai-core-modules-rules.mdc

# 或在IDE中打开查看
code .cursor/rules/rst-ai-core-modules-rules.mdc
```

### 2. 运行现有测试
```bash
cd backend
# 运行核心测试套件
python run_tests.py --core

# 运行指定模块测试
python run_tests.py --module tradingview
```

### 3. 检查现有模块示例
```bash
# 查看已实现的模块结构
tree backend/app/modules/

# 参考TradingView模块实现
ls -la backend/app/modules/tradingview/
```

---

## 🎯 开发新模块的步骤

### Phase 1: 规划和设计
1. [ ] **阅读完整规范文档** (`.cursor/rules/rst-ai-core-modules-rules.mdc`)
2. [ ] 确定模块名称和功能范围
3. [ ] 分析依赖关系
4. [ ] 设计数据模型

### Phase 2: 结构创建
```bash
# 创建模块目录结构
mkdir -p backend/app/modules/{module_name}
mkdir -p backend/app/modules/{module_name}/migrations
touch backend/app/modules/{module_name}/__init__.py
touch backend/app/modules/{module_name}/module.py
touch backend/app/modules/{module_name}/models.py
```

### Phase 3: 实现开发
1. [ ] 实现数据模型 (`models.py`)
2. [ ] 实现模块类 (`module.py`)
3. [ ] 创建数据库迁移文件
4. [ ] 注册模块到配置

### Phase 4: 测试开发
```bash
# 创建测试文件
mkdir -p backend/tests/utils
mkdir -p backend/tests/api/routes
touch backend/tests/utils/{module_name}.py
touch backend/tests/api/routes/test_{module_name}.py
```

### Phase 5: 验证和文档
1. [ ] 运行完整测试套件
2. [ ] 编写模块文档
3. [ ] 更新API文档

---

## ⚠️ 关键注意事项

### 🚨 严格禁止的操作
1. **绕过模块系统** - 不得直接导入其他模块内部组件
2. **跳过权限检查** - 所有数据操作必须验证权限
3. **忽略测试** - 每个模块必须有完整测试覆盖
4. **硬编码配置** - 不得在代码中硬编码配置值

### ✅ 必须遵守的标准
1. **使用UUID主键** - 所有数据表必须使用UUID作为主键
2. **实现CRUD接口** - 继承CRUDModule或实现标准CRUD端点
3. **编写完整测试** - 至少包含7个基本测试用例
4. **提供完整文档** - 包含API文档和使用示例

---

## 🛠️ 开发工具

### 测试运行脚本
```bash
# 核心功能测试
python run_tests.py --core

# 所有测试(包括可能失败的)
python run_tests.py --full

# 指定模块测试
python run_tests.py --module {module_name}

# 已验证的测试套件
python run_tests.py --working
```

### 代码质量检查
```bash
# 运行代码检查
cd backend
python -m flake8 app/modules/{module_name}/
python -m mypy app/modules/{module_name}/

# 格式化代码
python -m black app/modules/{module_name}/
python -m isort app/modules/{module_name}/
```

---

## 📞 获取帮助

### 🔍 问题诊断
1. **查看规范文档**: `.cursor/rules/rst-ai-core-modules-rules.mdc` 包含所有详细规则
2. **参考现有模块**: 查看 `tradingview` 模块作为最佳实践示例
3. **运行测试验证**: 使用 `run_tests.py` 验证实现正确性

### 📚 学习资源
- **现有模块示例**: `backend/app/modules/tradingview/`
- **测试示例**: `backend/tests/api/routes/test_tradingview.py`
- **架构文档**: `backend/MODULAR_ARCHITECTURE.md`

### 🏗️ 最佳实践
1. **先看规范，再动手** - 详细阅读规范文档避免返工
2. **参考现有模块** - TradingView模块是完整的实现示例
3. **测试驱动开发** - 先写测试，后写实现
4. **文档同步更新** - 代码变更时同步更新文档

---

## 📈 成功指标

### ✅ 模块开发完成标准
- [ ] 所有单元测试通过 (100%)
- [ ] API集成测试通过
- [ ] 代码覆盖率 >= 80%
- [ ] 规范检查通过
- [ ] 文档完整

### 🎯 质量检查清单
- [ ] 目录结构符合规范
- [ ] 命名约定正确
- [ ] 数据模型标准化
- [ ] API接口统一
- [ ] 权限控制到位
- [ ] 测试覆盖完整
- [ ] 文档齐全

---

**⚠️ 重要提醒**: 
- 规范文档 `.cursor/rules/rst-ai-core-modules-rules.mdc` 是**强制性**的开发标准
- 所有模块开发必须严格遵守这些规则
- 违反规范的代码将不被接受

**📖 开始开发前，请务必完整阅读规范文档！**
