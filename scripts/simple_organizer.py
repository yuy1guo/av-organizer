# -*- coding: utf-8 -*-
"""
简化版 AV 整理脚本 - Python 2.7 兼容

使用方法:
    python simple_organizer.py "E:\\迅雷下载" [--dry-run] [--first-only]
"""

from __future__ import print_function
import os
import sys
import re
import shutil
import json

# 视频文件扩展名
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.wmv', '.flv', '.mov', '.m4v', '.rmvb'}

# 厂牌名称映射
STUDIO_MAPPINGS = {
    's1': 's1',
    's1 no.1 style': 's1',
    'ideapocket': 'ideapocket',
    'idea pocket': 'ideapocket',
    'moodyz': 'moodyz',
    'prestige': 'prestige',
    'e-body': 'e-body',
    'ebody': 'e-body',
    'faleno': 'faleno',
    'attackers': 'attackers',
    'madonna': 'madonna',
    'premium': 'premium',
    'kawaii': 'kawaii',
}


def extract_av_code(filename):
    """从文件名提取番号"""
    name = filename.upper()
    
    # 匹配模式: 字母+分隔符+数字
    patterns = [
        r'([A-Z]{2,6}[-\s]\d{3,5})',  # ABC-123 or ABC 123
        r'([A-Z]{2,6}\d{3,5})',       # ABC123
    ]
    
    for pattern in patterns:
        match = re.search(pattern, name)
        if match:
            code = match.group(1)
            # 标准化为连字符格式
            code = re.sub(r'([A-Z]+)\s+(\d+)', r'\1-\2', code)
            code = re.sub(r'([A-Z]+)(\d+)', r'\1-\2', code)
            return code
    
    return None


def fetch_javbus_metadata(code):
    """
    从 javbus.com 获取元数据
    注意: 这个函数需要 Python 3 和网络访问
    在 Python 2.7 环境下,我们将返回模拟数据
    """
    # 由于 Python 2.7 的限制,这里返回基于番号的默认数据
    # 实际使用时需要 Python 3 环境
    
    studio_mapping = {
        'SSIS': 'S1',
        'SSNI': 'S1',
        'IPX': 'IdeaPocket',
        'IPZZ': 'IdeaPocket',
        'HEZ': 'Hot Entertainment',
        'MIDV': 'MOODYZ',
        'MIAB': 'MOODYZ', 
        'MIDA': 'MOODYZ',
        'PRED': 'Premium',
        'ABF': 'Prestige',
        'SONE': 'S1',
        'START': 'SOD Create',
        'WAAA': 'Wanz Factory',
        'DASS': 'DAS!',
        'MEYD': 'Tameike Goro',
        'MFYD': 'MOODYZ',
        'JUR': 'Madonna',
        'JUQ': 'Madonna',
        'ROYD': 'Royal',
        'EBWH': 'E-Body',
        'HMN': 'Hon Naka',
        'ADN': 'Attackers',
        'NGOD': 'JET Eizou',
        'DLDSS': 'DAHLIA',
        'FSDSS': 'FALENO',
        'CAWD': 'kawaii',
        'URE': 'Madonna',
        'ATID': 'Attackers',
        'FNS': 'Faleno Star',
        'FFT': 'Faleno',
        'GVH': 'Glory Quest',
    }
    
    # 从番号提取厂牌前缀
    prefix_match = re.match(r'([A-Z]+)', code.upper())
    if prefix_match:
        prefix = prefix_match.group(1)
        studio = studio_mapping.get(prefix, 'Unknown')
    else:
        studio = 'Unknown'
    
    return {
        'studio': studio,
        'title': code,  # 默认使用番号作为标题
        'actresses': []
    }


def normalize_studio(studio_name):
    """标准化厂牌名称"""
    if not studio_name:
        return 'others'
    
    cleaned = studio_name.lower().strip()
    
    if cleaned in STUDIO_MAPPINGS:
        return STUDIO_MAPPINGS[cleaned]
    
    # 默认处理: 小写,空格转连字符
    normalized = re.sub(r'[^\w\s-]', '', cleaned)
    normalized = re.sub(r'[\s]+', '-', normalized)
    normalized = re.sub(r'-+', '-', normalized)
    
    return normalized if normalized else 'others'


def sanitize_filename(filename):
    """清理文件名中的非法字符"""
    # 移除 Windows 文件名非法字符
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '', filename)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    return sanitized[:200]


def scan_directory(directory):
    """扫描目录,找出所有视频文件和包含视频的文件夹"""
    results = []
    
    try:
        items = os.listdir(directory)
    except Exception as e:
        print("Error reading directory: {}".format(e))
        return results
    
    for item_name in items:
        item_path = os.path.join(directory, item_name)
        
        if os.path.isfile(item_path):
            ext = os.path.splitext(item_name)[1].lower()
            if ext in VIDEO_EXTENSIONS:
                results.append((item_path, False))
        
        elif os.path.isdir(item_path):
            # 检查文件夹内是否有视频文件
            has_video = False
            try:
                for root, dirs, files in os.walk(item_path):
                    for f in files:
                        ext = os.path.splitext(f)[1].lower()
                        if ext in VIDEO_EXTENSIONS:
                            has_video = True
                            break
                    if has_video:
                        break
            except:
                pass
            
            if has_video:
                results.append((item_path, True))
    
    return results


def organize_item(item_path, is_folder, metadata, base_directory, dry_run=False):
    """重命名并移动项目到厂牌文件夹"""
    studio_folder = normalize_studio(metadata['studio'])
    studio_path = os.path.join(base_directory, studio_folder)
    
    safe_title = sanitize_filename(metadata['title'])
    new_name = "[{}]-[{}]".format(metadata['code'], safe_title)
    
    if is_folder:
        new_path = os.path.join(studio_path, new_name)
    else:
        ext = os.path.splitext(item_path)[1]
        new_path = os.path.join(studio_path, "{}{}".format(new_name, ext))
    
    # 处理重名
    if os.path.exists(new_path):
        counter = 1
        original_new_path = new_path
        while os.path.exists(new_path):
            if is_folder:
                new_path = "{}_{}".format(original_new_path, counter)
            else:
                base, ext = os.path.splitext(original_new_path)
                new_path = "{}_{}{}".format(base, counter, ext)
            counter += 1
    
    if dry_run:
        print("  [DRY RUN] Would move to: {}".format(new_path))
        return (True, new_path)
    
    try:
        if not os.path.exists(studio_path):
            os.makedirs(studio_path)
        
        shutil.move(item_path, new_path)
        return (True, new_path)
    except Exception as e:
        return (False, str(e))


def handle_failed_item(item_path, base_directory, reason, dry_run=False):
    """将失败的项目移动到 /others 文件夹"""
    others_path = os.path.join(base_directory, 'others')
    item_name = os.path.basename(item_path)
    new_path = os.path.join(others_path, item_name)
    
    # 处理重名
    if os.path.exists(new_path):
        counter = 1
        base_name, ext = os.path.splitext(item_name)
        while os.path.exists(new_path):
            new_name = "{}_{}{}".format(base_name, counter, ext if ext else '')
            new_path = os.path.join(others_path, new_name)
            counter += 1
    
    if dry_run:
        print("  [DRY RUN] Would move to /others: {} (reason: {})".format(item_name, reason))
        return
    
    try:
        if not os.path.exists(others_path):
            os.makedirs(others_path)
        
        shutil.move(item_path, new_path)
        print("  Moved to /others: {} (reason: {})".format(item_name, reason))
    except Exception as e:
        print("  Error moving to /others: {}".format(e))


def organize_av_directory(directory, dry_run=False, first_only=False):
    """完整的整理流程"""
    print("Scanning directory: {}".format(directory))
    items = scan_directory(directory)
    print("Found {} items\n".format(len(items)))
    
    if first_only and items:
        items = items[:1]
        print("Processing first item only (test mode)\n")
    
    success_count = 0
    failed_count = 0
    
    for item_path, is_folder in items:
        item_name = os.path.basename(item_path)
        item_type = "Folder" if is_folder else "File"
        
        print("\n" + "=" * 60)
        print("{}: {}".format(item_type, item_name))
        print("=" * 60)
        
        # 提取番号
        print("Extracting code...")
        code = extract_av_code(item_name)
        
        if not code:
            print("  X Code not found")
            failed_count += 1
            handle_failed_item(item_path, directory, 'code_not_found', dry_run)
            continue
        
        print("  √ Code: {}".format(code))
        
        # 获取元数据
        print("Fetching metadata...")
        metadata = fetch_javbus_metadata(code)
        metadata['code'] = code
        
        print("  √ Studio: {}".format(metadata['studio']))
        print("  √ Title: {}".format(metadata['title']))
        
        # 整理
        print("Organizing...")
        success, result = organize_item(item_path, is_folder, metadata, directory, dry_run)
        
        if success:
            print("  √ Moved to: {}".format(result))
            success_count += 1
        else:
            print("  X Error: {}".format(result))
            failed_count += 1
            handle_failed_item(item_path, directory, 'move_error', dry_run)
    
    # 汇总
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("Total items: {}".format(len(items)))
    print("Success: {}".format(success_count))
    print("Failed: {}".format(failed_count))
    
    if dry_run:
        print("\n[DRY RUN] No actual changes were made")


def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_organizer.py <directory> [--dry-run] [--first-only]")
        sys.exit(1)
    
    directory = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    first_only = '--first-only' in sys.argv
    
    if not os.path.isdir(directory):
        print("Error: Directory not found: {}".format(directory))
        sys.exit(1)
    
    organize_av_directory(directory, dry_run, first_only)


if __name__ == "__main__":
    main()
