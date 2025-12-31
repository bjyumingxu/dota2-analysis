@echo off
chcp 65001 >nul
echo ========================================
echo 清理缓存并重启服务
echo ========================================
echo.

echo [1/4] 清理Python缓存...
cd backend
if exist src\__pycache__ (
    echo 删除 __pycache__ 文件夹...
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
    echo Python缓存已清理
) else (
    echo 没有找到Python缓存文件
)
cd ..

echo.
echo [2/4] 检查后端服务是否运行...
netstat -ano | findstr :8000 >nul
if %errorlevel% == 0 (
    echo ⚠️  警告：端口8000已被占用！
    echo 请手动停止后端服务（在运行后端的终端按Ctrl+C）
    echo.
    pause
) else (
    echo ✓ 端口8000未被占用，可以启动
)

echo.
echo [3/4] 检查前端服务是否运行...
netstat -ano | findstr :5173 >nul
if %errorlevel% == 0 (
    echo ⚠️  警告：端口5173已被占用！
    echo 请手动停止前端服务（在运行前端的终端按Ctrl+C）
    echo.
    pause
) else (
    echo ✓ 端口5173未被占用，可以启动
)

echo.
echo [4/4] 清理完成！
echo.
echo ========================================
echo 下一步操作：
echo ========================================
echo.
echo 1. 打开两个新的终端窗口
echo.
echo 2. 终端1 - 启动后端：
echo    cd backend
echo    .\venv\Scripts\Activate.ps1
echo    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 3. 终端2 - 启动前端：
echo    cd frontend
echo    npm run dev
echo.
echo 4. 在浏览器中按 Ctrl+Shift+R 强制刷新
echo.
echo ========================================
pause

