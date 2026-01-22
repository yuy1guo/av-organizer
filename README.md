# AV Organizer

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-2.7%2B-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-1.0.0-blue)]()

**English** | [中文](README_CN.md)

*Automatically organize your AV video collection by extracting codes from filenames and fetching metadata from javbus.com.*

</div>

---

## 🎯 Overview

AV Organizer is an OpenCode skill that automatically organizes your AV video collection:

1. 📂 Scan target directory for video files (standalone and in folders)
2. 🔢 Extract AV codes from filenames (e.g., SSIS-001, IPX-123)
3. 🌐 Fetch metadata from javbus.com (studio, title, actresses)
4. 📁 Create studio-based folder structure
5. ✏️ Rename files to `[Code]-[Title]` format
6. 📦 Move files to appropriate studio folders

### ✨ Features

- 🎬 **Auto Code Extraction** - Smart regex matching for various code formats
- 🔍 **Metadata Fetching** - Automatically retrieve info from javbus.com
- 📁 **Smart Categorization** - Organize into studio-based folders
- 📝 **Standardized Naming** - Consistent `[Code]-[Title]` naming convention
- 🛡️ **Safe Mode** - Preview mode (`--dry-run`) before execution
- 🔄 **Failure Handling** - Unrecognized files moved to `/others` folder

## 🚀 Quick Start

### Requirements

- Python 2.7+ or Python 3.6+
- Windows / Linux / macOS

### Installation

```bash
# Clone the repository
git clone https://github.com/yuy1guo/av-organizer.git
cd av-organizer
```

### Usage

#### Preview Mode (Recommended)

```bash
# Preview all files (no actual changes)
python scripts/simple_organizer.py "<your-video-path>" --dry-run

# Process only first file (testing)
python scripts/simple_organizer.py "<your-video-path>" --dry-run --first-only
```

#### Execute

```bash
# Organize all files
python scripts/simple_organizer.py "<your-video-path>"
```

### Command Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview mode, no actual file changes |
| `--first-only` | Process only first file (for testing) |

## 📂 Output Example

### Before

```
<your-video-path>\
├── SSIS-001.mp4
├── IPX-123.mp4
├── Folder/
│   └── MIDV-456.mp4
└── Unknown-789.mp4
```

### After

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

## 📖 Script Reference

| Script | Description | Python Version |
|--------|-------------|----------------|
| `scripts/simple_organizer.py` | Simplified version (recommended), uses built-in studio mappings | 2.7+ |
| `scripts/organize.py` | Full version, real-time javbus.com scraping | 3.6+ |
| `scripts/extract_code.py` | Extract codes from filenames | 3.x |
| `scripts/javbus_scraper.py` | Fetch metadata from javbus.com | 3.x |
| `scripts/normalize_studio.py` | Normalize studio names | 3.x |

## 🏷️ Supported Studio Prefixes

| Prefix | Studio |
|--------|--------|
| SSIS, SSNI, SONE | S1 |
| IPX, IPZZ | IdeaPocket |
| MIDV, MIAB, MIDA, MFYD | MOODYZ |
| PRED | Premium |
| JUR, JUQ, URE | Madonna |
| EBWH | E-Body |
| ... | ... (30+ prefixes) |

Unrecognized codes are moved to the `/others` folder.

## 🌐 About javbus.com Access

> **⚠️ Note**: Due to well-known reasons, accessing javbus.com from certain regions requires a VPN/proxy connection.
>
> If javbus.com is inaccessible, the system will use built-in studio mappings for organization, with titles displayed as their codes.

### Full Version vs Simplified Version

| Version | Network Required | Info Completeness |
|---------|------------------|-------------------|
| Full (`organize.py`) | Access to javbus.com | Full titles + actress info |
| Simplified (`simple_organizer.py`) | No network needed | Studio only, titles as codes |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [javbus.com](https://javbus.com) for providing the metadata API
- [OpenCode](https://opencode.ai) for the skill framework
- All contributors and users

---

## 📧 Contact

- GitHub: [https://github.com/yuy1guo](https://github.com/yuy1guo)
