@echo off
chcp 65001 >nul
echo ========================================
echo 强制结束占用8000和5173端口的进程
echo ========================================
echo.

echo [1/3] 查找占用8000端口的进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo 找到进程ID: %%a
    echo 正在结束进程...
    taskkill /PID %%a /F >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  无法结束进程 %%a（可能需要管理员权限）
    ) else (
        echo ✅ 已结束进程 %%a
    )
)

echo.
echo [2/3] 查找占用5173端口的进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do (
    echo 找到进程ID: %%a
    echo 正在结束进程...
    taskkill /PID %%a /F >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  无法结束进程 %%a（可能需要管理员权限）
    ) else (
        echo ✅ 已结束进程 %%a
    )
)

echo.
echo [3/3] 等待2秒让端口释放...
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo 检查端口是否已释放...
echo ========================================
netstat -ano | findstr :8000 >nul
if errorlevel 1 (
    echo ✅ 端口8000已释放
) else (
    echo ❌ 端口8000仍被占用，请以管理员身份运行此脚本
)

netstat -ano | findstr :5173 >nul
if errorlevel 1 (
    echo ✅ 端口5173已释放
) else (
    echo ❌ 端口5173仍被占用，请以管理员身份运行此脚本
)

echo.
echo ========================================
echo 完成！现在可以重新启动服务了
echo ========================================
pause

