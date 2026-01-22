@echo off
REM AV Organizer - 一键发布到 GitHub
REM 使用方法: 双击运行此脚本

echo ========================================
echo    AV Organizer - GitHub 发布脚本
echo ========================================
echo.

REM 检查是否安装 GitHub CLI
where gh >nul 2>&1
if errorlevel 1 (
    echo [✗] 未检测到 GitHub CLI
    echo.
    echo 请先安装 GitHub CLI:
    echo   1. 访问 https://cli.github.com/
    echo   2. 下载 Windows 版本安装包
    echo   3. 运行安装程序
    echo.
    echo 或使用 winget:
    echo   winget install --id GitHub.cli
    echo.
    pause
    exit /b 1
)

REM 检查登录状态
echo [1/4] 检查 GitHub 登录状态...
gh auth status >nul 2>&1
if errorlevel 1 (
    echo [提示] 需要登录 GitHub
    gh auth login
) else (
    echo [✓] 已登录 GitHub
)

REM 创建仓库
echo [2/4] 创建 GitHub 仓库...
gh repo create av-organizer --public --description "Automatically organize your AV video collection with metadata fetching and smart file renaming."

if errorlevel 1 (
    echo [✗] 仓库创建失败，可能已存在
    echo.
    echo 请手动删除现有仓库后重试，或联系支持
    pause
    exit /b 1
)
echo [✓] 仓库创建成功

REM 初始化并推送
echo [3/4] 初始化 Git 仓库...
git init
git add .
git commit -m "Initial commit: AV Organizer skill v1.0.0"

echo [4/4] 推送代码到 GitHub...
git branch -M main
git push -u origin main

echo.
echo ========================================
echo    发布完成！
echo ========================================
echo.
echo 你的仓库地址:
echo   https://github.com/394861919/av-organizer
echo.
echo 下一步建议:
echo   1. 访问仓库页面
echo   2. 点击 "About" → Edit → 添加 Topics: opencode, skill, mcp
echo   3. 创建第一个 Release
echo.
pause
