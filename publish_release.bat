@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Get versions using Python script
python version_manager.py info

if not exist versions.bat (
    echo [Error] Failed to get version information.
    pause
    goto :eof
)

call versions.bat
del versions.bat

:menu
cls
echo ========================================================
echo       SD Banana 插件发布助手 (Substance Designer)
echo ========================================================
echo.
echo  当前版本: !CURRENT_VERSION!
echo.
echo  请选择升级类型：
echo.
echo  [1] 补丁 (Patch) : 修复 Bug (!CURRENT_VERSION! -^> !NEXT_PATCH!)
echo  [2] 次版本 (Minor): 新增功能 (!CURRENT_VERSION! -^> !NEXT_MINOR!)
echo  [3] 主版本 (Major): 重大变更 (!CURRENT_VERSION! -^> !NEXT_MAJOR!)
echo  [4] 退出
echo.
echo ========================================================
echo.

set /p choice="请输入选项 [1-4]: "

if "%choice%"=="1" set vtype=patch
if "%choice%"=="2" set vtype=minor
if "%choice%"=="3" set vtype=major
if "%choice%"=="4" goto :eof

if not defined vtype (
    echo 无效输入，请重新选择。
    timeout /t 2 >nul
    goto menu
)

echo.
echo --------------------------------------------------------
echo [1/2] 正在更新 pluginInfo.json 版本 (%vtype%) ...
echo --------------------------------------------------------
python version_manager.py update %vtype%

if %errorlevel% neq 0 (
    echo.
    echo [错误] 版本更新失败！
    pause >nul
    goto menu
)

:: Get the new version
python version_manager.py get
if not exist new_version.bat (
    echo [Error] Failed to retrieve new version.
    pause >nul
    goto menu
)

call new_version.bat
del new_version.bat

echo.
echo --------------------------------------------------------
echo [2/2] 提交更改并推送到 GitHub ...
echo --------------------------------------------------------
echo 即将提交版本 !NEW_VERSION! 并打标签，这将触发 GitHub Actions 自动打包发布 .zip。
echo.
set /p confirm="确认发布吗? (Y/N): "

if /i "%confirm%"=="y" (
    echo.
    echo 正在提交 git commit ...
    git add pluginInfo.json version_manager.py
    git commit -m "chore(release): version !NEW_VERSION!"
    
    echo 正在打标签 ...
    git tag v!NEW_VERSION!
    
    echo 正在推送 ...
    git push && git push --tags
    
    if !errorlevel! equ 0 (
        echo.
        echo ========================================================
        echo  ✅ 发布成功！
        echo  版本 v!NEW_VERSION! 已推送。
        echo  请访问 GitHub 仓库的 Actions 页面查看构建进度。
        echo ========================================================
    ) else (
        echo.
        echo [错误] 推送失败，请检查网络或 Git 配置。
    )
) else (
    echo.
    echo 已取消发布。本地文件已修改，请手动还原或提交。
)

pause

