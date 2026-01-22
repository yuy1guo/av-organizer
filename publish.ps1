# AV Organizer - GitHub 发布脚本 (PowerShell)
# 使用方法: 右键 -> "用 PowerShell 运行"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   AV Organizer - GitHub 发布脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Git
$gitPath = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitPath) {
    Write-Host "[✗] 未检测到 Git" -ForegroundColor Red
    Write-Host "请先安装 Git: https://git-scm.com/download/win" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}
Write-Host "[✓] Git 已安装" -ForegroundColor Green

# 获取 GitHub Token
Write-Host ""
Write-Host "[1/4] 获取认证信息..." -ForegroundColor Yellow
$token = $null

# 尝试从环境变量获取
if ($env:GITHUB_TOKEN) {
    $token = $env:GITHUB_TOKEN
    Write-Host "[✓] 使用环境变量中的 Token" -ForegroundColor Green
}
else {
    Write-Host "请输入 GitHub Personal Access Token:" -ForegroundColor Yellow
    Write-Host "(访问: https://github.com/settings/tokens 生成 Token，勾选 'repo' 权限)" -ForegroundColor Gray
    $token = Read-Host "Token" -AsSecureString
    $token = [System.Net.NetworkCredential]::new("", $token).Password
}

if ([string]::IsNullOrEmpty($token)) {
    Write-Host "[✗] Token 不能为空" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 检查仓库是否已存在
Write-Host ""
Write-Host "[2/4] 检查远程仓库..." -ForegroundColor Yellow
$repoUrl = "https://api.github.com/repos/394861919/av-organizer"
$repoCheck = Invoke-RestMethod -Uri $repoUrl -Headers @{"Authorization"="token $token"} -ErrorAction SilentlyContinue

if ($repoCheck) {
    Write-Host "[!] 仓库 '394861919/av-organizer' 已存在" -ForegroundColor Yellow
    $createNew = Read-Host "是否已存在仓库，要推送到现有仓库? (y/n)"
    if ($createNew.ToLower() -ne "y") {
        Write-Host "请使用其他仓库名或删除现有仓库" -ForegroundColor Yellow
        exit 0
    }
}
else {
    # 创建仓库
    Write-Host "[3/4] 创建 GitHub 仓库..." -ForegroundColor Yellow
    $body = @{
        name          = "av-organizer"
        description   = "Automatically organize your AV video collection with metadata fetching and smart file renaming."
        @public       = $true
        auto_init     = $false
    } | ConvertTo-Json

    try {
        $createResult = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers @{"Authorization"="token $token"; "Accept"="application/vnd.github.v3+json"} -Body $body -ErrorAction Stop
        Write-Host "[✓] 仓库创建成功" -ForegroundColor Green
    }
    catch {
        Write-Host "[✗] 仓库创建失败: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# 初始化并推送
Write-Host ""
Write-Host "[4/4] 推送代码..." -ForegroundColor Yellow

# 保存当前目录
$originalDir = Get-Location

# 进入项目目录
Set-Location "C:\Users\郭羽仪\.config\opencode\skill\av-organizer"

# 初始化 Git
git init
git add .
git commit -m "Initial commit: AV Organizer skill v1.0.0"
git branch -M main

# 设置远程仓库 URL（包含 Token）
$remoteUrl = "https://$token@github.com/394861919/av-organizer.git"
git remote remove origin 2>$null | Out-Null
git remote add origin $remoteUrl
git push -u origin main

# 恢复原目录
Set-Location $originalDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   发布完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "你的仓库地址:" -ForegroundColor Yellow
Write-Host "  https://github.com/394861919/av-organizer" -ForegroundColor Cyan
Write-Host ""
Write-Host "建议操作:" -ForegroundColor Yellow
Write-Host "  1. 访问仓库页面" -ForegroundColor Gray
Write-Host "  2. 点击 'About' → Edit" -ForegroundColor Gray
Write-Host "  3. 添加 Topics: opencode, skill, mcp" -ForegroundColor Gray
Write-Host "  4. 创建第一个 Release" -ForegroundColor Gray
Write-Host ""

Read-Host "按回车键退出"
