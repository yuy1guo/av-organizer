#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AV 完整整理脚本 v2.0
新目录结构: 厂商/女优/[番号] 标题/
"""

import os
import sys
import re
import json
import shutil
import urllib.request
import urllib.error
from pathlib import Path

# 设置控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 导入爬虫
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from complete_javbus_scraper import scrape_javbus_complete

# 视频扩展名
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.wmv', '.flv', '.mov', '.m4v', '.rmvb', '.ts'}

# 厂商映射
STUDIO_MAPPING = {
    'エスワン ナンバーワンスタイル': 's1',
    'S1 NO.1 STYLE': 's1',
    'アイデアポケット': 'ideapocket',
    'IDEA POCKET': 'ideapocket',
    'ムーディーズ': 'moodyz',
    "MOODYZ": 'moodyz',
    'プレステージ': 'prestige',
    'PRESTIGE': 'prestige',
    'FALENO': 'faleno',
    'FALENO STAR': 'faleno-star',
    'kawaii': 'kawaii',
    'E-BODY': 'e-body',
    'Madonna': 'madonna',
    'ATTACKERS': 'attackers',
    'アタッカーズ': 'attackers',
    'Das': 'das',
    'ダスッ！': 'das',
    'プレミアム': 'premium',
    'PREMIUM': 'premium',
    'SODクリエイト': 'sod-create',
    'SOD CREATE': 'sod-create',
    '本中': 'hon-naka',
    'ROYAL': 'royal',
    'WANZ': 'wanz-factory',
    'DAHLIA': 'dahlia',
    'JETビデオ': 'jet-eizou',
    '溜池ゴロー': 'tameike-goro',
    'Glory Quest': 'glory-quest',
}

def extract_code_from_filename(filename):
    """从文件名提取番号"""
    # 移除扩展名
    name = os.path.splitext(filename)[0]
    
    # 移除已有的方括号
    name = re.sub(r'[\[\]]', '', name)
    
    # 常见番号格式: 字母-数字
    patterns = [
        r'([A-Z]{2,10}[-\s]?\d{3,5})',  # SONE-586, IPX 123
        r'([A-Z]{3,10}\d{3,5})',         # MIDV456
    ]
    
    for pattern in patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            code = match.group(1).upper()
            # 规范化: 统一用横杠
            code = re.sub(r'\s+', '-', code)
            # 确保字母和数字之间有横杠
            code = re.sub(r'([A-Z]+)(\d+)', r'\1-\2', code)
            return code
    
    return None

def normalize_studio(studio_name):
    """规范化厂商名称"""
    if not studio_name:
        return 'unknown'
    
    # 直接映射
    if studio_name in STUDIO_MAPPING:
        return STUDIO_MAPPING[studio_name]
    
    # 部分匹配
    studio_lower = studio_name.lower()
    for key, value in STUDIO_MAPPING.items():
        if key.lower() in studio_lower or studio_lower in key.lower():
            return value
    
    # 未知厂商
    return 'others'

def sanitize_filename(name):
    """清理文件名中的非法字符"""
    # Windows 非法字符
    illegal_chars = r'<>:"/\\|?*'
    for char in illegal_chars:
        name = name.replace(char, '')
    
    # 移除前后空格和点
    name = name.strip('. ')
    
    # 限制长度
    return name[:200]

def download_poster(url, save_path, proxy='http://127.0.0.1:7890'):
    """下载海报"""
    try:
        # 代理设置
        proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
        opener = urllib.request.build_opener(proxy_handler)
        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
            ('Referer', 'https://www.javbus.com/'),
        ]
        
        # 下载
        response = opener.open(url, timeout=30)
        with open(save_path, 'wb') as f:
            f.write(response.read())
        
        return True
    except Exception as e:
        print(f"  ✗ 海报下载失败: {e}")
        return False

def organize_single_file(file_path, base_dir, proxy='http://127.0.0.1:7890', dry_run=False):
    """
    整理单个视频文件
    
    新结构: base_dir/厂商/女优/[番号] 标题/文件
    """
    filename = os.path.basename(file_path)
    print(f"\n处理: {filename}")
    
    # 1. 提取番号
    code = extract_code_from_filename(filename)
    if not code:
        print(f"  ✗ 无法提取番号")
        return False, 'no_code'
    
    print(f"  ✓ 番号: {code}")
    
    # 2. 爬取元数据
    print(f"  爬取中...")
    metadata = scrape_javbus_complete(code, proxy)
    
    if not metadata or not metadata.get('title'):
        print(f"  ✗ 爬取失败")
        return False, 'scrape_failed'
    
    print(f"  ✓ 标题: {metadata['title']}")
    print(f"  ✓ 厂商: {metadata['studio']}")
    print(f"  ✓ 女优: {', '.join(metadata['actresses']) if metadata['actresses'] else '未知'}")
    
    # 3. 确定目录结构
    studio_folder = normalize_studio(metadata['studio'])
    
    # 女优名称: 使用第一个女优,如果没有则用 "未知女优"
    actress = metadata['actresses'][0] if metadata['actresses'] else '未知女优'
    actress_folder = sanitize_filename(actress)
    
    # 影片文件夹: [番号] 标题
    title = sanitize_filename(metadata['title'])
    video_folder_name = f"[{code}] {title}"
    
    # 完整路径
    target_dir = Path(base_dir) / studio_folder / actress_folder / video_folder_name
    
    # 4. 创建目录
    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"  目标: {target_dir}")
    
    # 5. 移动/复制视频文件
    ext = os.path.splitext(filename)[1]
    new_video_name = f"[{code}] {title}{ext}"
    target_video_path = target_dir / new_video_name
    
    if not dry_run:
        try:
            shutil.move(file_path, target_video_path)
            print(f"  ✓ 视频已移动")
        except Exception as e:
            print(f"  ✗ 移动失败: {e}")
            return False, 'move_failed'
    else:
        print(f"  [Dry Run] 将移动到: {target_video_path}")
    
    # 6. 下载海报
    if metadata.get('poster_url'):
        poster_path = target_dir / 'cover.jpg'
        if not dry_run:
            print(f"  下载海报...")
            if download_poster(metadata['poster_url'], poster_path, proxy):
                print(f"  ✓ 海报已保存")
            else:
                print(f"  ⚠ 海报下载失败(非致命错误)")
        else:
            print(f"  [Dry Run] 将下载海报到: {poster_path}")
    
    # 7. 保存元数据
    metadata_path = target_dir / 'metadata.json'
    if not dry_run:
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"  ✓ 元数据已保存")
    else:
        print(f"  [Dry Run] 将保存元数据到: {metadata_path}")
    
    print(f"  ✓ 完成")
    return True, None

def scan_videos(directory):
    """扫描目录中的所有视频文件"""
    videos = []
    
    for item in Path(directory).iterdir():
        if item.is_file() and item.suffix.lower() in VIDEO_EXTENSIONS:
            videos.append(str(item))
        elif item.is_dir():
            # 递归扫描子目录
            for video_file in item.rglob('*'):
                if video_file.is_file() and video_file.suffix.lower() in VIDEO_EXTENSIONS:
                    videos.append(str(video_file))
    
    return videos

def scan_all_videos_recursively(base_dir):
    """递归扫描所有视频文件（包括已整理和未整理的）"""
    videos = []
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS:
                file_path = os.path.join(root, file)
                videos.append(file_path)
    
    return videos

def is_video_in_standard_location(video_path):
    """检查视频是否在标准位置且有完整元数据"""
    video_folder = Path(video_path).parent
    
    # 检查文件夹名格式: [番号] 标题
    folder_name = video_folder.name
    if not (folder_name.startswith('[') and ']' in folder_name):
        return False
    
    # 检查是否有 metadata.json
    metadata_path = video_folder / 'metadata.json'
    if not metadata_path.exists():
        return False
    
    return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='AV 完整整理脚本 v2.0')
    parser.add_argument('directory', help='要整理的目录')
    parser.add_argument('--proxy', default='http://127.0.0.1:7890', help='代理地址')
    parser.add_argument('--dry-run', action='store_true', help='预览模式(不实际移动文件)')
    parser.add_argument('--first-only', action='store_true', help='只处理第一个文件(测试用)')
    parser.add_argument('--file', help='只处理指定的单个文件')
    parser.add_argument('--reorganize', action='store_true', help='重新整理所有非标准位置的视频')
    
    args = parser.parse_args()
    
    base_dir = os.path.abspath(args.directory)
    
    if not os.path.isdir(base_dir):
        print(f"错误: 目录不存在: {base_dir}")
        sys.exit(1)
    
    print("=" * 70)
    print("AV 完整整理脚本 v2.0")
    print("=" * 70)
    print(f"目录: {base_dir}")
    print(f"代理: {args.proxy}")
    print(f"模式: {'预览' if args.dry_run else '执行'}")
    print("=" * 70)
    
    # 处理单个文件
    if args.file:
        file_path = os.path.abspath(args.file)
        if not os.path.isfile(file_path):
            print(f"错误: 文件不存在: {file_path}")
            sys.exit(1)
        
        success, error = organize_single_file(file_path, base_dir, args.proxy, args.dry_run)
        sys.exit(0 if success else 1)
    
    # 重新整理模式: 扫描所有视频，只处理非标准位置的
    if args.reorganize:
        print("\n重新整理模式: 扫描所有视频...")
        all_videos = scan_all_videos_recursively(base_dir)
        
        # 过滤出非标准位置的视频
        videos = [v for v in all_videos if not is_video_in_standard_location(v)]
        
        print(f"找到 {len(all_videos)} 个视频文件")
        print(f"其中 {len(videos)} 个需要重新整理\n")
        
        if not videos:
            print("所有视频都已在标准位置!")
            sys.exit(0)
    else:
        # 正常模式: 只扫描根目录和一级子目录
        print("\n扫描视频文件...")
        videos = scan_videos(base_dir)
    
    if not videos:
        print("未找到视频文件")
        sys.exit(0)
    
    print(f"找到 {len(videos)} 个视频文件\n")
    
    if args.first_only:
        videos = videos[:1]
        print("(仅处理第一个文件)")
    
    # 统计
    success_count = 0
    failed_count = 0
    errors = {}
    
    # 处理每个视频
    for video in videos:
        success, error = organize_single_file(video, base_dir, args.proxy, args.dry_run)
        
        if success:
            success_count += 1
        else:
            failed_count += 1
            errors[error] = errors.get(error, 0) + 1
    
    # 总结
    print("\n" + "=" * 70)
    print("整理完成")
    print("=" * 70)
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    
    if errors:
        print("\n失败原因统计:")
        for error, count in errors.items():
            print(f"  {error}: {count}")
    
    if args.dry_run:
        print("\n注意: 这是预览模式,未实际移动文件")
        print("确认无误后,去掉 --dry-run 参数执行")

if __name__ == "__main__":
    main()
