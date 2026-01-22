# AV Organizer

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-2.7%2B-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-1.0.0-blue)]()

[**English**](README.md) | **中文**

*自动整理您的 AV 视频收藏夹，提取番号并从 javbus.com 获取元数据，智能重命名文件。*

</div>

---

## 🎯 功能概述

AV Organizer 是一个 OpenCode skill，用于自动整理 AV 视频收藏：

1. 📂 扫描目标目录中的视频文件（包括独立文件和文件夹内的文件）
2. 🔢 从文件名中提取番号（如 SSIS-001、IPX-123）
3. 🌐 从 javbus.com 获取元数据（制作商、标题、女优）
4. 📁 创建基于制作商的文件夹结构
5. ✏️ 将文件重命名为 `[番号]-[标题]` 格式
6. 📦 将文件移动到对应的制作商文件夹

### ✨ 主要特性

- 🎬 **自动番号提取** - 使用正则表达式智能匹配多种番号格式
- 🔍 **元数据获取** - 自动从 javbus.com 获取影片信息
- 📁 **智能分类** - 自动归类到制作商文件夹
- 📝 **标准化命名** - 采用一致的 `[番号]-[标题]` 命名格式
- 🛡️ **安全模式** - 支持预览模式（`--dry-run`）先查看效果
- 🔄 **失败处理** - 无法识别的文件自动移到 `/others` 文件夹

## 🚀 快速开始

### 环境要求

- Python 2.7+ 或 Python 3.6+
- Windows / Linux / macOS

### 安装

```bash
# 克隆仓库
git clone https://github.com/yuy1guo/av-organizer.git
cd av-organizer
```

### 使用方法

#### 预览模式（推荐先预览）

```bash
# 预览所有文件（不实际修改）
python scripts/simple_organizer.py "<your-video-path>" --dry-run

# 只处理第一个文件（测试）
python scripts/simple_organizer.py "<your-video-path>" --dry-run --first-only
```

#### 正式运行

```bash
# 整理所有文件
python scripts/simple_organizer.py "<your-video-path>"
```

### 命令行选项

| 选项 | 描述 |
|------|------|
| `--dry-run` | 预览模式，不实际修改文件 |
| `--first-only` | 只处理第一个文件，用于测试 |

## 📂 输出示例

### 整理前

```
<your-video-path>\
├── SSIS-001.mp4
├── IPX-123.mp4
├── Folder/
│   └── MIDV-456.mp4
└── Unknown-789.mp4
```

### 整理后

```
<your-video-path>\
├── s1\
│   └── [SSIS-001]-[Beautiful Girl].mp4
├── ideapocket\
│   └── [IPX-123]-[Hot Scene].mp4
├── moodyz\
│   └── [MIDV-456]-[Amazing Action].mp4
└── others\
    └── Unknown-789.mp4
```

## 📖 脚本说明

| 脚本 | 描述 | Python 版本 |
|------|------|-------------|
| `scripts/simple_organizer.py` | 简化版（推荐），使用内置厂牌映射 | 2.7+ |
| `scripts/organize.py` | 完整版，实时抓取 javbus.com | 3.6+ |
| `scripts/extract_code.py` | 从文件名提取番号 | 3.x |
| `scripts/javbus_scraper.py` | 从 javbus.com 获取元数据 | 3.x |
| `scripts/normalize_studio.py` | 标准化制作商名称 | 3.x |

## 🏷️ 已支持的厂牌前缀

| 前缀 | 制作商 |
|------|--------|
| SSIS, SSNI, SONE | S1 |
| IPX, IPZZ | IdeaPocket |
| MIDV, MIAB, MIDA, MFYD | MOODYZ |
| PRED | Premium |
| JUR, JUQ, URE | Madonna |
| EBWH | E-Body |
| ... | ... (30+ 个前缀) |

未识别的番号会移动到 `/others` 文件夹。

## 🌐 关于 javbus.com 访问

> **⚠️ 注意**：由于众所周知的原因，在中国大陆访问 javbus.com 需要自备科学上网方式。
>
> 如果无法访问 javbus.com，系统将使用内置的厂牌映射规则进行整理，标题将显示为番号。

### 完整版 vs 简化版

| 版本 | 网络要求 | 信息完整度 |
|------|----------|------------|
| 完整版 (`organize.py`) | 需要访问 javbus.com | 完整标题 + 女优信息 |
| 简化版 (`simple_organizer.py`) | 无需网络 | 仅厂牌信息，标题为番号 |

## 🤝 贡献

欢迎贡献代码！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 开源许可

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [javbus.com](https://javbus.com) - 提供元数据 API
- [OpenCode](https://opencode.ai) - 提供 skill 框架
- 所有贡献者和用户

---

## 📧 联系方式

- GitHub: [https://github.com/yuy1guo](https://github.com/yuy1guo)
