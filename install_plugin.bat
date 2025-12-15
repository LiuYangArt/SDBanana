@echo off
echo ========================================
echo SDBanana Plugin Installer
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
REM 移除末尾的反斜杠
set "SOURCE_DIR=%~dp0"
set "SOURCE_DIR=%SOURCE_DIR:~0,-1%"
set "TARGET_DIR=C:\Program Files\Adobe\Adobe Substance 3D Designer\resources\python\sdplugins\SDBanana"

echo 源目录: %SOURCE_DIR%
echo 目标目录: %TARGET_DIR%
echo.

REM 检查源目录和必要文件是否存在
if not exist "%SOURCE_DIR%\pluginInfo.json" (
    echo [错误] pluginInfo.json 文件不存在: %SOURCE_DIR%\pluginInfo.json
    echo 请确保在正确的目录运行此脚本
    echo.
    pause
    exit /b 1
)

if not exist "%SOURCE_DIR%\SDBanana" (
    echo [错误] SDBanana 模块目录不存在: %SOURCE_DIR%\SDBanana
    echo.
    pause
    exit /b 1
)

REM 检查 Substance Designer 插件目录是否存在
if not exist "C:\Program Files\Adobe\Adobe Substance 3D Designer\resources\python\sdplugins" (
    echo [错误] Substance Designer 插件目录不存在
    echo 请确认 Substance Designer 已正确安装
    echo.
    pause
    exit /b 1
)

REM 如果目标已经存在，先删除
if exist "%TARGET_DIR%" (
    echo 检测到已存在的链接或目录，正在删除...
    rmdir "%TARGET_DIR%" 2>nul
    if exist "%TARGET_DIR%" (
        echo [警告] 无法删除现有目录，可能不是链接
        echo 请手动删除: %TARGET_DIR%
        echo.
        pause
        exit /b 1
    )
    echo 已删除旧的链接
    echo.
)

REM 创建目录链接
echo 正在创建目录链接...
mklink /j "%TARGET_DIR%" "%SOURCE_DIR%"

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo [成功] 插件链接创建成功！
    echo ========================================
    echo.
    echo 现在你可以：
    echo 1. 启动 Substance 3D Designer
    echo 2. 在开发目录中修改代码会立即生效
    echo 3. 重启 Designer 以重新加载插件
    echo.
) else (
    echo.
    echo [错误] 创建链接失败！
    echo.
)

pause
