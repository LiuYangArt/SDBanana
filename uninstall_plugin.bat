@echo off
echo ========================================
echo SDBanana Plugin Uninstaller
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 此脚本需要管理员权限运行！
    echo 请右键点击此文件，选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

REM 设置路径变量
set "TARGET_DIR=C:\Program Files\Adobe\Adobe Substance 3D Designer\resources\python\sdplugins\SDBanana"

echo 目标目录: %TARGET_DIR%
echo.

REM 检查链接是否存在
if not exist "%TARGET_DIR%" (
    echo [信息] 插件链接不存在，无需卸载
    echo.
    pause
    exit /b 0
)

REM 删除链接
echo 正在删除插件链接...
rmdir "%TARGET_DIR%"

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo [成功] 插件链接已删除！
    echo ========================================
    echo.
    echo 插件已从 Substance Designer 中卸载
    echo 你的开发文件仍然保留在原位置
    echo.
) else (
    echo.
    echo [错误] 删除链接失败！
    echo 可能该目录不是链接，或者 Substance Designer 正在运行
    echo.
)

pause
