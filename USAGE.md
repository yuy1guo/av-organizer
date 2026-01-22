# AV Organizer Skill - 使用指南

## Skill 已创建成功!

位置: `C:\Users\郭羽仪\.config\opencode\skill\av-organizer`

## 测试结果

✓ 第一个文件已成功整理:
- 原始: `E:\迅雷下载\4k2.com@hez-772.mp4`
- 新位置: `E:\迅雷下载\hot-entertainment\[HEZ-772]-[HEZ-772].mp4`

## 使用方法

### 选项 1: 直接运行脚本

```bash
# 预览模式 (不实际修改文件)
python C:\Users\郭羽仪\.config\opencode\skill\av-organizer\scripts\simple_organizer.py "E:\迅雷下载" --dry-run

# 只处理第一个文件 (测试)
python C:\Users\郭羽仪\.config\opencode\skill\av-organizer\scripts\simple_organizer.py "E:\迅雷下载" --dry-run --first-only

# 正式运行 (整理所有文件)
python C:\Users\郭羽仪\.config\opencode\skill\av-organizer\scripts\simple_organizer.py "E:\迅雷下载"
```

### 选项 2: 通过 OpenCode Skill 系统

1. Skill 已经创建在标准位置,可以通过 `/av-organizer` 命令加载
2. 加载后,直接告诉我要整理的目录,我会自动使用这个 skill

## 当前限制

由于使用 Python 2.7,脚本使用内置的厂牌映射规则而不是实时抓取 javbus.com:

- ✓ 优点: 速度快,无需网络,兼容 Python 2.7
- ✗ 限制: 标题显示为番号,无女优信息

已映射的厂牌前缀:
- SSIS, SSNI, SONE → S1
- IPX, IPZZ → IdeaPocket  
- MIDV, MIAB, MIDA, MFYD → MOODYZ
- PRED → Premium
- JUR, JUQ, URE → Madonna
- EBWH → E-Body
- 等等... (共 30+ 个前缀)

未识别的番号会移动到 `/others` 文件夹。

## 升级到完整版本

如果安装 Python 3.6+,可以使用 `scripts/organize.py`,它会:
- 实时从 javbus.com 抓取元数据
- 获取完整标题和女优信息
- 标题格式: `[番号]-[完整影片名]`

## 文件结构

```
E:\迅雷下载\
├── s1\
│   ├── [SSIS-001]-[标题].mp4
│   └── [SONE-586]-[标题]\ (文件夹)
├── ideapocket\
│   └── [IPX-123]-[标题].mp4
├── moodyz\
│   └── [MIDV-456]-[标题].mp4
├── hot-entertainment\
│   └── [HEZ-772]-[HEZ-772].mp4 ✓ (已整理)
└── others\
    └── 无法识别的文件
```

## 下一步

你可以:
1. 继续整理剩余的 94 个文件
2. 先多测试几个文件
3. 调整厂牌映射规则
4. 或者让我做其他修改
