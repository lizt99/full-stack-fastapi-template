# RST AI Core - Docker 快速开始
# Docker Quick Start Guide

**⚡ 5分钟快速部署指南**

---

## 🚀 超快上手 (30秒)

```bash
# 1. 克隆项目
git clone <项目地址>
cd full-stack-fastapi-template

# 2. 一键启动开发环境
./scripts/docker-deploy.sh dev

# 3. 访问应用
# 前端: http://localhost:5173
# 后端: http://localhost:8000/docs
# 数据库: http://localhost:8080 (Adminer)
```

🎉 **完成！** 应用已在本地运行！

---

## 📦 核心命令

### 🛠️ 开发环境
```bash
# 启动开发环境 (热重载)
./scripts/docker-deploy.sh dev

# 查看服务状态
docker compose ps

# 查看日志
./scripts/docker-deploy.sh logs backend   # 后端日志
./scripts/docker-deploy.sh logs frontend  # 前端日志
```

### 🏭 生产环境
```bash
# 构建生产镜像
./scripts/docker-deploy.sh build

# 启动生产环境
./scripts/docker-deploy.sh start

# 健康检查
./scripts/docker-deploy.sh health
```

### 🔧 管理命令
```bash
# 停止服务
./scripts/docker-deploy.sh stop

# 重启服务
./scripts/docker-deploy.sh restart

# 清理资源
./scripts/docker-deploy.sh cleanup
```

---

## 🎯 快速访问地址

### 开发环境
- **前端应用**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **数据库管理**: http://localhost:8080
- **邮件测试**: http://localhost:1080
- **Traefik面板**: http://localhost:8090

### 默认登录
- **用户名**: admin@example.com
- **密码**: changethis (请在.env中修改)

---

## ⚙️ 环境配置

### 快速配置
```bash
# 复制环境模板
cp .env.example .env

# 编辑配置文件
vim .env
```

### 关键配置项
```env
# 应用配置
ENVIRONMENT=local                    # 环境: local/staging/production
DOMAIN=localhost                     # 域名配置
SECRET_KEY=your-secret-key          # JWT密钥 (必须修改)

# 管理员账户
FIRST_SUPERUSER=admin@example.com           # 管理员邮箱
FIRST_SUPERUSER_PASSWORD=your-password      # 管理员密码 (必须修改)

# 数据库配置
POSTGRES_PASSWORD=your-db-password   # 数据库密码 (必须修改)
POSTGRES_USER=postgres               # 数据库用户
POSTGRES_DB=rst_ai_core             # 数据库名称
```

---

## 🐛 故障排查

### 常见问题

#### 1. 端口被占用
```bash
# 检查端口占用
lsof -i :5173  # 前端端口
lsof -i :8000  # 后端端口

# 停止服务并重启
./scripts/docker-deploy.sh stop
./scripts/docker-deploy.sh dev
```

#### 2. 数据库连接失败
```bash
# 检查数据库状态
docker compose exec db pg_isready -U postgres

# 重新启动数据库
docker compose restart db
```

#### 3. 镜像构建失败
```bash
# 清理Docker缓存
./scripts/docker-deploy.sh cleanup

# 重新构建
./scripts/docker-deploy.sh build
```

#### 4. 权限问题
```bash
# 给脚本执行权限
chmod +x scripts/docker-deploy.sh

# 检查Docker权限
docker run hello-world
```

### 检查服务健康
```bash
# 运行健康检查
./scripts/docker-deploy.sh health

# 查看所有服务状态
docker compose ps

# 查看系统资源
docker stats --no-stream
```

---

## 🎁 生产部署

### 1. 构建生产镜像
```bash
# 设置版本标签
export TAG=v1.0.0

# 构建镜像
./scripts/docker-deploy.sh build
```

### 2. 推送到仓库
```bash
# 推送到Docker Hub
./scripts/docker-deploy.sh push

# 推送到私有仓库
./scripts/docker-deploy.sh push registry.your-company.com
```

### 3. 部署到服务器
```bash
# 配置生产环境变量
export ENVIRONMENT=production
export DOMAIN=your-domain.com

# 启动生产服务
./scripts/docker-deploy.sh start
```

---

## 📚 下一步

✅ **应用已运行** - 现在您可以：

1. **开发新功能** 
   - 参考 `MODULES_DEVELOPMENT_GUIDE.md`
   - 遵循 `.cursor/rules/rst-ai-core-modules-rules.mdc`

2. **添加新模块**
   - 使用 `PRODUCT_REQUIREMENTS_TEMPLATE.md` 录入需求
   - AI自动生成模块代码

3. **部署到生产**
   - 查看完整的 `DOCKER_BUILD_DEPLOY_GUIDE.md`
   - 配置CI/CD自动部署

4. **自定义配置**
   - 修改 `docker-compose.yml`
   - 调整 `.env` 环境变量

---

## 🆘 获取帮助

```bash
# 查看脚本帮助
./scripts/docker-deploy.sh help

# 查看完整文档
ls *.md                    # 查看所有文档
cat DOCKER_BUILD_DEPLOY_GUIDE.md  # 完整部署指南
```

### 相关文档
- 📖 **完整部署指南**: `DOCKER_BUILD_DEPLOY_GUIDE.md`
- 🏗️ **模块开发指南**: `MODULES_DEVELOPMENT_GUIDE.md`
- 📋 **需求文档模板**: `PRODUCT_REQUIREMENTS_TEMPLATE.md`
- ⚡ **项目部署**: `deployment.md`

---

**🎉 恭喜！您的RST AI Core应用现在已经在Docker中运行了！**

*享受现代化的模块化开发体验吧！* 🚀
