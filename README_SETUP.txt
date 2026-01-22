"""
AV Organizer Skill - 使用说明

由于当前环境的 Python 版本限制，skill 已创建但需要 Python 3.6+ 才能运行。

## Skill 位置
C:\Users\郭羽仪\.config\opencode\skill\av-organizer

## 包含的脚本

### 1. extract_code.py
从文件名提取番号
用法: python extract_code.py "filename.mp4"
输出: HEZ-772

### 2. javbus_scraper.py
从 javbus.com 获取元数据
用法: python javbus_scraper.py "HEZ-772"
输出: JSON 格式的厂牌、标题、女优信息

### 3. normalize_studio.py
标准化厂牌名称为文件夹名
用法: python normalize_studio.py "Studio Name"
输出: normalized-folder-name

### 4. organize.py (主脚本)
完整整理流程
用法: python organize.py "E:\迅雷下载" [--dry-run] [--first-only]

选项:
--dry-run: 只显示将要执行的操作,不实际修改文件
--first-only: 只处理第一个文件(测试用)

## 环境要求

需要 Python 3.6+,当前系统只有 Python 2.7。

## 解决方案

方案 1: 安装 Python 3
- 从 python.org 下载并安装 Python 3.8+
- 或者通过 Microsoft Store 安装 Python 3

方案 2: 直接使用 skill
如果 Python 3 可用,可以这样调用 skill:
1. 加载 skill: /av-organizer
2. 使用 skill 整理目录

## 测试

番号提取已验证可用:
- 输入: 4k2.com@hez-772.mp4
- 输出: HEZ-772

下一步需要:
1. 确保 Python 3 可用
2. 运行: python organize.py "E:\迅雷下载" --dry-run --first-only
3. 检查输出,确认逻辑正确
4. 去掉 --dry-run 和 --first-only,正式运行
