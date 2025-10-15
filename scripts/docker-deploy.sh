#!/bin/bash

# RST AI Core - Docker 部署脚本
# Docker Build & Deploy Script

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}===============================================${NC}"
    echo -e "${BLUE}🚀 $1${NC}"
    echo -e "${BLUE}===============================================${NC}"
    echo ""
}

# 检查必需的工具
check_prerequisites() {
    print_header "检查环境依赖"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装。请先安装 Docker。"
        exit 1
    fi
    
    if ! command -v docker compose &> /dev/null; then
        print_error "Docker Compose 未安装。请先安装 Docker Compose。"
        exit 1
    fi
    
    print_success "Docker 和 Docker Compose 已安装"
    print_info "Docker 版本: $(docker --version)"
    print_info "Docker Compose 版本: $(docker compose version)"
}

# 检查环境变量
check_environment() {
    print_header "检查环境配置"
    
    if [ ! -f ".env" ]; then
        print_warning ".env 文件不存在，正在创建默认配置..."
        cp .env.example .env 2>/dev/null || {
            print_warning "未找到 .env.example，创建基本配置..."
            cat > .env << EOF
ENVIRONMENT=local
DOMAIN=localhost
STACK_NAME=rst-ai-core
DOCKER_IMAGE_BACKEND=rst-ai-core/backend
DOCKER_IMAGE_FRONTEND=rst-ai-core/frontend
TAG=latest

SECRET_KEY=changethis
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis
POSTGRES_PASSWORD=changethis
POSTGRES_USER=postgres
POSTGRES_DB=rst_ai_core

FRONTEND_HOST=http://localhost:5173
BACKEND_CORS_ORIGINS=["http://localhost:5173","https://localhost:5173"]
EOF
        }
        print_warning "请编辑 .env 文件配置您的环境变量"
    fi
    
    # 加载环境变量
    export $(grep -v '^#' .env | xargs)
    
    print_success "环境配置已加载"
    print_info "环境: ${ENVIRONMENT:-local}"
    print_info "域名: ${DOMAIN:-localhost}"
    print_info "标签: ${TAG:-latest}"
}

# 构建镜像
build_images() {
    print_header "构建 Docker 镜像"
    
    # 设置默认值
    export TAG=${TAG:-latest}
    export FRONTEND_ENV=${FRONTEND_ENV:-production}
    
    print_info "开始构建镜像 (标签: $TAG)..."
    
    # 构建后端镜像
    print_info "构建后端镜像..."
    docker build -t ${DOCKER_IMAGE_BACKEND:-rst-ai-core/backend}:$TAG ./backend
    
    # 构建前端镜像
    print_info "构建前端镜像..."
    VITE_API_URL=${VITE_API_URL:-http://localhost:8000}
    docker build -t ${DOCKER_IMAGE_FRONTEND:-rst-ai-core/frontend}:$TAG \
        --build-arg VITE_API_URL=$VITE_API_URL \
        --build-arg NODE_ENV=$FRONTEND_ENV \
        ./frontend
    
    print_success "镜像构建完成！"
    
    # 显示构建的镜像
    print_info "构建的镜像:"
    docker images | grep -E "(rst-ai-core|${DOCKER_IMAGE_BACKEND##*/}|${DOCKER_IMAGE_FRONTEND##*/})" | head -10
}

# 启动服务
start_services() {
    local compose_file=${1:-docker-compose.yml}
    
    print_header "启动服务"
    
    if [ "$compose_file" = "docker-compose.yml" ]; then
        print_info "启动生产环境服务..."
        docker compose -f docker-compose.yml up -d
    else
        print_info "启动开发环境服务..."
        docker compose up -d
    fi
    
    print_success "服务启动完成！"
    
    # 等待服务启动
    print_info "等待服务健康检查..."
    sleep 10
    
    # 显示服务状态
    print_info "服务状态:"
    docker compose ps
}

# 停止服务
stop_services() {
    print_header "停止服务"
    
    print_info "停止所有服务..."
    docker compose down
    
    print_success "服务已停止！"
}

# 清理资源
cleanup() {
    print_header "清理 Docker 资源"
    
    print_warning "这将清理未使用的 Docker 资源..."
    read -p "确认继续? (y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        print_info "清理未使用的镜像..."
        docker image prune -f
        
        print_info "清理构建缓存..."
        docker builder prune -f
        
        print_info "清理未使用的网络..."
        docker network prune -f
        
        print_success "清理完成！"
        
        print_info "当前 Docker 资源使用情况:"
        docker system df
    else
        print_info "清理操作已取消"
    fi
}

# 查看日志
view_logs() {
    local service=${1:-backend}
    
    print_header "查看服务日志: $service"
    
    if docker compose ps | grep -q "$service"; then
        docker compose logs -f --tail=50 "$service"
    else
        print_error "服务 '$service' 未运行"
        print_info "可用服务:"
        docker compose ps --format "table {{.Name}}\t{{.Status}}"
    fi
}

# 健康检查
health_check() {
    print_header "服务健康检查"
    
    # 检查容器状态
    print_info "检查容器状态..."
    docker compose ps
    
    # 检查后端健康
    print_info "检查后端 API 健康..."
    if curl -f http://localhost:8000/api/v1/utils/health-check/ >/dev/null 2>&1; then
        print_success "后端 API 健康检查通过"
    else
        print_warning "后端 API 健康检查失败"
    fi
    
    # 检查前端
    print_info "检查前端服务..."
    if curl -f http://localhost:5173 >/dev/null 2>&1 || curl -f http://localhost >/dev/null 2>&1; then
        print_success "前端服务健康检查通过"
    else
        print_warning "前端服务健康检查失败"
    fi
    
    # 检查数据库
    print_info "检查数据库连接..."
    if docker compose exec -T db pg_isready -U ${POSTGRES_USER:-postgres} >/dev/null 2>&1; then
        print_success "数据库连接检查通过"
    else
        print_warning "数据库连接检查失败"
    fi
}

# 推送镜像
push_images() {
    local registry=${1:-docker.io}
    
    print_header "推送镜像到仓库: $registry"
    
    # 设置镜像名称
    local backend_image="${DOCKER_IMAGE_BACKEND:-rst-ai-core/backend}:${TAG:-latest}"
    local frontend_image="${DOCKER_IMAGE_FRONTEND:-rst-ai-core/frontend}:${TAG:-latest}"
    
    if [ "$registry" != "docker.io" ]; then
        # 为非 Docker Hub 仓库重新标记镜像
        local new_backend_image="$registry/${backend_image}"
        local new_frontend_image="$registry/${frontend_image}"
        
        print_info "重新标记镜像..."
        docker tag "$backend_image" "$new_backend_image"
        docker tag "$frontend_image" "$new_frontend_image"
        
        backend_image="$new_backend_image"
        frontend_image="$new_frontend_image"
    fi
    
    print_info "推送后端镜像: $backend_image"
    docker push "$backend_image"
    
    print_info "推送前端镜像: $frontend_image"
    docker push "$frontend_image"
    
    print_success "镜像推送完成！"
}

# 显示使用帮助
show_help() {
    cat << EOF
RST AI Core - Docker 部署脚本

用法:
    $0 [选项] [参数]

选项:
    dev                 启动开发环境 (带热重载)
    build               构建 Docker 镜像
    start               启动生产环境服务
    stop                停止所有服务
    restart             重启服务 (等同于 stop + start)
    logs [service]      查看服务日志 (默认: backend)
    health              运行健康检查
    push [registry]     推送镜像到仓库 (默认: docker.io)
    cleanup             清理未使用的 Docker 资源
    help                显示此帮助信息

环境变量:
    TAG                 镜像标签 (默认: latest)
    FRONTEND_ENV        前端环境 (默认: production)
    VITE_API_URL        前端 API 地址 (默认: http://localhost:8000)

示例:
    $0 dev              # 启动开发环境
    $0 build            # 构建镜像
    $0 start            # 启动生产环境
    $0 logs frontend    # 查看前端日志
    $0 push ghcr.io     # 推送到 GitHub Container Registry
    $0 cleanup          # 清理 Docker 资源

EOF
}

# 主函数
main() {
    case "${1:-help}" in
        "dev")
            check_prerequisites
            check_environment
            print_info "启动开发环境..."
            start_services "docker-compose.override.yml"
            ;;
        "build")
            check_prerequisites
            check_environment
            build_images
            ;;
        "start")
            check_prerequisites
            check_environment
            start_services "docker-compose.yml"
            ;;
        "stop")
            check_prerequisites
            stop_services
            ;;
        "restart")
            check_prerequisites
            stop_services
            check_environment
            start_services "docker-compose.yml"
            ;;
        "logs")
            check_prerequisites
            view_logs "${2:-backend}"
            ;;
        "health")
            check_prerequisites
            health_check
            ;;
        "push")
            check_prerequisites
            check_environment
            push_images "${2:-docker.io}"
            ;;
        "cleanup")
            check_prerequisites
            cleanup
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            print_error "未知选项: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
