@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo     阿米巴核算系统 - 启动中...
echo ========================================

if not exist "backend\amoeba.db" (
    echo [1/3] 首次运行，正在安装后端依赖...
    cd backend
    pip install -r requirements.txt -q
    cd ..
    echo [2/3] 后端依赖安装完成，数据库将在首次启动时自动初始化
) else (
    echo [2/3] 数据库已存在，跳过初始化
)

echo [3/3] 启动后端服务 (端口 8000)...
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
