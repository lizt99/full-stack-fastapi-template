# RST AI Core - Docker 打包和发布指南
# Docker Build & Deploy Guide

**版本**: 1.0  
**项目**: FastAPI + React 全栈模块化应用  
**目标**: 完整的Docker容器化、构建、发布和部署流程  

---

## 🎯 概述 (Overview)

本项目采用现代化的容器化架构，支持多环境部署：
- **开发环境**: 本地开发，热重载，调试友好
- **生产环境**: 优化构建，反向代理，HTTPS支持
- **多阶段部署**: 支持staging和production环境

### 🏗️ 架构组件
```yaml
服务组件:
  - Frontend: React + Vite + Nginx (多阶段构建)
  - Backend: FastAPI + uv + Python 3.10
  - Database: PostgreSQL 17
  - Proxy: Traefik (反向代理 + HTTPS)
  - Admin: Adminer (数据库管理)
  - Email-dev: MailCatcher (开发环境邮件测试)
```

---

## 🔧 环境准备 (Prerequisites)

### 📦 必需软件
```bash
# 检查Docker和Docker Compose版本
docker --version          # >= 24.0.0
docker compose version    # >= 2.20.0

# 检查系统资源
docker system df          # 查看Docker磁盘使用
docker system info        # 查看Docker系统信息
```

### 🔑 环境变量配置
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

**关键环境变量说明**:
```yaml
# 基础配置
ENVIRONMENT=local|staging|production    # 部署环境
DOMAIN=your-domain.com                  # 域名配置
STACK_NAME=rst-ai-core                  # Docker Compose堆栈名称

# Docker镜像配置
DOCKER_IMAGE_BACKEND=rst-ai-core/backend    # 后端镜像名
DOCKER_IMAGE_FRONTEND=rst-ai-core/frontend  # 前端镜像名
TAG=latest                                   # 镜像标签

# 应用配置
SECRET_KEY=your-secret-key              # JWT密钥
FIRST_SUPERUSER=admin@example.com       # 管理员邮箱
FIRST_SUPERUSER_PASSWORD=admin123       # 管理员密码

# 数据库配置
POSTGRES_SERVER=db                      # 数据库服务器
POSTGRES_USER=postgres                  # 数据库用户
POSTGRES_PASSWORD=your-db-password      # 数据库密码
POSTGRES_DB=rst_ai_core                 # 数据库名称

# 前端配置
FRONTEND_HOST=http://localhost:5173     # 前端访问地址
BACKEND_CORS_ORIGINS=["http://localhost:5173","https://localhost:5173"] # CORS配置
```

---

## 🏠 本地开发环境 (Local Development)

### 🚀 快速启动
```bash
# 1. 启动开发环境
docker compose up -d

# 2. 查看服务状态
docker compose ps

# 3. 查看日志
docker compose logs -f backend   # 后端日志
docker compose logs -f frontend  # 前端日志
```

### 🔍 开发环境特性
```yaml
开发环境配置:
  热重载: 
    - 后端: FastAPI --reload 模式
    - 前端: Vite dev server，自动刷新
    
  端口映射:
    - Frontend: http://localhost:5173
    - Backend: http://localhost:8000
    - Database: localhost:5432
    - Adminer: http://localhost:8080
    - MailCatcher: http://localhost:1080
    - Traefik Dashboard: http://localhost:8090
    
  文件同步:
    - 后端代码变更自动同步到容器
    - 前端通过Vite dev server提供服务
    - 数据库数据持久化
```

### 🛠️ 开发调试命令
```bash
# 进入后端容器调试
docker compose exec backend bash

# 进入数据库容器
docker compose exec db psql -U postgres -d rst_ai_core

# 重启特定服务
docker compose restart backend

# 重新构建并启动
docker compose up --build -d

# 查看资源使用
docker compose top
```

---

## 🏭 生产环境构建 (Production Build)

### 📦 构建准备
```bash
# 1. 确保环境变量正确
export TAG=v1.0.0
export ENVIRONMENT=production
export FRONTEND_ENV=production

# 2. 清理之前的构建
docker system prune -f
docker volume prune -f
```

### 🔨 单独构建镜像
```bash
# 构建后端镜像
docker build -t rst-ai-core/backend:v1.0.0 ./backend

# 构建前端镜像
docker build -t rst-ai-core/frontend:v1.0.0 \
  --build-arg VITE_API_URL=https://api.your-domain.com \
  --build-arg NODE_ENV=production \
  ./frontend

# 验证镜像
docker images | grep rst-ai-core
```

### 🏗️ 使用脚本构建
```bash
# 使用项目提供的构建脚本
export TAG=v1.0.0
export FRONTEND_ENV=production

# 构建所有镜像
./scripts/build.sh

# 构建并推送到镜像仓库
./scripts/build-push.sh
```

### 🚀 生产环境启动
```bash
# 生产环境部署（不使用override文件）
docker compose -f docker-compose.yml up -d

# 检查健康状态
docker compose ps
docker compose logs backend | grep "health"

# 验证API可用性
curl http://localhost:8000/api/v1/utils/health-check/
```

---

## 📡 镜像发布 (Image Publishing)

### 🏪 Docker Hub发布
```bash
# 1. 登录Docker Hub
docker login

# 2. 标记镜像
docker tag rst-ai-core/backend:v1.0.0 yourusername/rst-ai-core-backend:v1.0.0
docker tag rst-ai-core/frontend:v1.0.0 yourusername/rst-ai-core-frontend:v1.0.0

# 3. 推送镜像
docker push yourusername/rst-ai-core-backend:v1.0.0
docker push yourusername/rst-ai-core-frontend:v1.0.0

# 4. 推送latest标签
docker tag rst-ai-core/backend:v1.0.0 yourusername/rst-ai-core-backend:latest
docker tag rst-ai-core/frontend:v1.0.0 yourusername/rst-ai-core-frontend:latest
docker push yourusername/rst-ai-core-backend:latest
docker push yourusername/rst-ai-core-frontend:latest
```

### 🏢 私有仓库发布
```bash
# 1. 登录私有仓库
docker login registry.your-company.com

# 2. 标记镜像
docker tag rst-ai-core/backend:v1.0.0 registry.your-company.com/rst-ai-core/backend:v1.0.0
docker tag rst-ai-core/frontend:v1.0.0 registry.your-company.com/rst-ai-core/frontend:v1.0.0

# 3. 推送镜像
docker push registry.your-company.com/rst-ai-core/backend:v1.0.0
docker push registry.your-company.com/rst-ai-core/frontend:v1.0.0
```

### 🎯 GitHub Container Registry发布
```bash
# 1. 创建Personal Access Token (Settings -> Developer settings -> Personal access tokens)
# 权限: write:packages, read:packages, delete:packages

# 2. 登录GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# 3. 标记镜像
docker tag rst-ai-core/backend:v1.0.0 ghcr.io/yourusername/rst-ai-core-backend:v1.0.0
docker tag rst-ai-core/frontend:v1.0.0 ghcr.io/yourusername/rst-ai-core-frontend:v1.0.0

# 4. 推送镜像
docker push ghcr.io/yourusername/rst-ai-core-backend:v1.0.0
docker push ghcr.io/yourusername/rst-ai-core-frontend:v1.0.0
```

---

## 🌐 生产环境部署 (Production Deployment)

### 🔧 服务器准备
```bash
# 1. 安装Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. 创建应用目录
mkdir -p /opt/rst-ai-core
cd /opt/rst-ai-core

# 4. 上传项目文件
scp -r ./* user@your-server:/opt/rst-ai-core/
```

### 🌍 Traefik反向代理设置
```bash
# 1. 创建Traefik网络
docker network create traefik-public

# 2. 设置环境变量
export USERNAME=admin
export PASSWORD=your-traefik-password
export HASHED_PASSWORD=$(openssl passwd -apr1 $PASSWORD)
export DOMAIN=your-domain.com
export EMAIL=admin@your-domain.com

# 3. 启动Traefik
docker compose -f docker-compose.traefik.yml up -d

# 4. 验证Traefik
curl -u admin:your-traefik-password https://traefik.your-domain.com
```

### 🚀 应用部署
```bash
# 1. 设置生产环境变量
export ENVIRONMENT=production
export DOMAIN=your-domain.com
export STACK_NAME=rst-ai-core-prod
export TAG=v1.0.0

# 更新镜像配置
export DOCKER_IMAGE_BACKEND=yourusername/rst-ai-core-backend
export DOCKER_IMAGE_FRONTEND=yourusername/rst-ai-core-frontend

# 2. 部署应用
docker compose -f docker-compose.yml up -d

# 3. 验证部署
docker compose ps
docker compose logs backend
```

### 🔍 访问地址
```yaml
生产环境URL:
  前端: https://dashboard.your-domain.com
  后端API: https://api.your-domain.com
  API文档: https://api.your-domain.com/docs
  数据库管理: https://adminer.your-domain.com
  Traefik面板: https://traefik.your-domain.com
```

---

## 🤖 自动化部署 (Automated Deployment)

### 📋 GitHub Actions配置
项目已包含GitHub Actions工作流，支持自动化CI/CD:

```yaml
工作流程:
  1. 代码推送到master分支
  2. 自动构建Docker镜像
  3. 运行测试套件
  4. 推送镜像到容器仓库
  5. 部署到staging环境
  
  发布流程:
  1. 创建Release标签
  2. 自动构建生产镜像
  3. 部署到production环境
```

### 🔐 GitHub Secrets配置
在GitHub仓库的Settings > Secrets中配置:
```yaml
必需的Secrets:
  DOMAIN_PRODUCTION: your-domain.com
  DOMAIN_STAGING: staging.your-domain.com
  STACK_NAME_PRODUCTION: rst-ai-core-prod
  STACK_NAME_STAGING: rst-ai-core-stage
  SECRET_KEY: your-secret-key
  FIRST_SUPERUSER: admin@your-domain.com
  FIRST_SUPERUSER_PASSWORD: admin-password
  POSTGRES_PASSWORD: db-password
  EMAILS_FROM_EMAIL: noreply@your-domain.com
```

---

## 🔧 高级配置 (Advanced Configuration)

### ⚡ 性能优化
```yaml
生产环境优化:
  后端:
    - 多进程运行: --workers 4
    - 代码预编译: UV_COMPILE_BYTECODE=1
    - 健康检查: /api/v1/utils/health-check/
    
  前端:
    - 静态资源压缩
    - Nginx gzip压缩
    - 浏览器缓存策略
    
  数据库:
    - 连接池配置
    - 索引优化
    - 数据持久化
```

### 📊 监控和日志
```bash
# 查看资源使用
docker stats

# 查看容器日志
docker compose logs -f --tail=100 backend

# 检查健康状态
docker compose ps
curl https://api.your-domain.com/api/v1/utils/health-check/

# 数据库连接测试
docker compose exec backend python -c "
from app.core.db import engine
from sqlmodel import text, Session
with Session(engine) as session:
    result = session.exec(text('SELECT version()'))
    print(f'PostgreSQL: {result.first()}')
"
```

### 🛡️ 安全加固
```yaml
安全配置:
  HTTPS强制:
    - Traefik自动获取Let's Encrypt证书
    - HTTP自动跳转HTTPS
    
  访问控制:
    - 数据库不对外暴露
    - API通过Traefik反向代理
    - 管理工具HTTP Basic Auth保护
    
  数据保护:
    - 环境变量敏感信息
    - JWT token安全配置
    - CORS策略限制
```

---

## 🔍 故障排查 (Troubleshooting)

### 🚨 常见问题及解决方案

#### 1. 容器启动失败
```bash
# 检查容器状态
docker compose ps

# 查看错误日志
docker compose logs backend
docker compose logs frontend

# 检查环境变量
docker compose config

# 重新构建镜像
docker compose build --no-cache
```

#### 2. 数据库连接问题
```bash
# 检查数据库状态
docker compose exec db pg_isready -U postgres

# 查看数据库连接
docker compose exec backend python -c "
from app.core.db import engine
print(f'Database URL: {engine.url}')
"

# 重置数据库
docker compose down -v
docker compose up -d
```

#### 3. 前后端通信问题
```bash
# 检查CORS配置
curl -H "Origin: https://dashboard.your-domain.com" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     https://api.your-domain.com/api/v1/utils/health-check/

# 检查API响应
curl https://api.your-domain.com/docs
```

#### 4. 镜像构建问题
```bash
# 清理Docker缓存
docker system prune -a -f

# 查看构建日志
docker build --no-cache --progress=plain -t test ./backend

# 检查依赖文件
docker run --rm -it rst-ai-core/backend:latest uv pip list
```

### 📋 健康检查清单
```yaml
部署前检查:
  - [ ] 环境变量配置正确
  - [ ] 域名DNS解析正确
  - [ ] Docker和Docker Compose版本兼容
  - [ ] 防火墙端口开放(80, 443)
  - [ ] SSL证书配置正确
  
部署后验证:
  - [ ] 所有容器状态healthy
  - [ ] API健康检查通过
  - [ ] 前端页面可访问
  - [ ] 数据库连接正常
  - [ ] 模块功能测试通过
```

---

## 📦 镜像管理 (Image Management)

### 🏷️ 版本标签策略
```bash
# 语义化版本
docker tag rst-ai-core/backend:latest rst-ai-core/backend:v1.0.0
docker tag rst-ai-core/backend:latest rst-ai-core/backend:v1.0
docker tag rst-ai-core/backend:latest rst-ai-core/backend:v1

# 环境标签
docker tag rst-ai-core/backend:v1.0.0 rst-ai-core/backend:staging
docker tag rst-ai-core/backend:v1.0.0 rst-ai-core/backend:production

# 日期标签
docker tag rst-ai-core/backend:latest rst-ai-core/backend:2024-10-13
```

### 🧹 镜像清理
```bash
# 清理未使用的镜像
docker image prune -f

# 清理构建缓存
docker builder prune -f

# 清理所有未使用资源
docker system prune -a -f

# 查看磁盘使用
docker system df
```

---

## 📚 参考资源 (References)

### 🔗 官方文档
- [Docker官方文档](https://docs.docker.com/)
- [Docker Compose文档](https://docs.docker.com/compose/)
- [Traefik文档](https://doc.traefik.io/traefik/)
- [FastAPI部署指南](https://fastapi.tiangolo.com/deployment/)

### 🛠️ 相关工具
- **容器管理**: Docker Desktop, Portainer
- **镜像扫描**: Trivy, Snyk
- **监控工具**: Prometheus + Grafana
- **日志管理**: ELK Stack, Loki

### 📋 项目文档
- `deployment.md` - 详细部署文档
- `MODULES_DEVELOPMENT_GUIDE.md` - 模块开发指南
- `.cursor/rules/rst-ai-core-modules-rules.mdc` - 开发规范

---

## 🎯 最佳实践总结

### ✅ 推荐做法
1. **分层构建** - 使用多阶段Docker构建优化镜像大小
2. **健康检查** - 为所有服务配置健康检查
3. **资源限制** - 设置容器CPU和内存限制
4. **日志管理** - 统一日志格式和收集策略
5. **安全扫描** - 定期扫描镜像漏洞
6. **备份策略** - 定期备份数据库和配置

### ❌ 避免陷阱
1. **root用户运行** - 避免使用root用户运行应用
2. **硬编码配置** - 使用环境变量管理配置
3. **大镜像** - 避免在镜像中包含不必要的文件
4. **缺少健康检查** - 确保所有服务都有健康检查
5. **忽略日志** - 重视日志收集和监控

---

**🎉 恭喜！您现在已经掌握了RST AI Core项目的完整Docker化流程！**

从本地开发到生产部署，从镜像构建到自动化CI/CD，这个指南涵盖了所有必要的步骤和最佳实践。

**📞 需要帮助？**
- 查看项目的 `deployment.md` 获取更详细的部署信息
- 参考 `MODULES_DEVELOPMENT_GUIDE.md` 了解模块开发流程
- 遵循 `.cursor/rules/rst-ai-core-modules-rules.mdc` 中的开发规范

---

*本指南基于 RST AI Core 模块化架构创建*  
*文档版本: 1.0*  
*最后更新: 2024-10-13*
