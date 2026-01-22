#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理和重新整理脚本
1. 删除不符合标准结构的空文件夹
2. 重新整理非标准结构的影片
"""

import os
import sys
import shutil
from pathlib import Path

# 设置控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 视频扩展名
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.wmv', '.flv', '.mov', '.m4v', '.rmvb', '.ts'}

def is_standard_video_folder(folder_path):
    """
    检查文件夹是否符合标准结构：
    - 文件夹名格式: [番号] 标题
    - 必须包含: 视频文件
    - 应该包含: cover.jpg, metadata.json
    """
    folder_name = os.path.basename(folder_path)
    
    # 检查文件夹名格式
    if not folder_name.startswith('[') or ']' not in folder_name:
        return False, 'folder_name_format'
    
    # 列出文件
    try:
        files = list(Path(folder_path).iterdir())
    except:
        return False, 'access_error'
    
    # 检查是否有视频文件
    has_video = any(f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS for f in files)
    
    if not has_video:
        return False, 'no_video'
    
    return True, None

def find_video_in_folder(folder_path):
    """在文件夹中查找视频文件"""
    for item in Path(folder_path).iterdir():
        if item.is_file() and item.suffix.lower() in VIDEO_EXTENSIONS:
            return str(item)
    return None

def clean_empty_and_invalid_folders(base_dir, dry_run=True):
    """
    清理空文件夹和不符合标准的文件夹
    
    返回: (deleted_folders, videos_to_reorganize)
    """
    deleted_folders = []
    videos_to_reorganize = []
    
    print("=" * 70)
    print("扫描不标准的文件夹...")
    print("=" * 70)
    
    # 遍历厂商目录
    for studio_dir in Path(base_dir).iterdir():
        if not studio_dir.is_dir():
            continue
        
        studio_name = studio_dir.name
        
        # 遍历女优目录
        for actress_dir in studio_dir.iterdir():
            if not actress_dir.is_dir():
                continue
            
            actress_name = actress_dir.name
            
            # 检查女优目录下的影片文件夹
            for video_folder in actress_dir.iterdir():
                if not video_folder.is_dir():
                    continue
                
                is_standard, reason = is_standard_video_folder(video_folder)
                
                if not is_standard:
                    folder_rel = f"{studio_name}/{actress_name}/{video_folder.name}"
                    
                    if reason == 'no_video':
                        # 没有视频文件的文件夹 - 删除
                        print(f"\n✗ 空文件夹: {folder_rel}")
                        print(f"  原因: 没有视频文件")
                        
                        if not dry_run:
                            try:
                                shutil.rmtree(video_folder)
                                deleted_folders.append(str(video_folder))
                                print(f"  ✓ 已删除")
                            except Exception as e:
                                print(f"  ✗ 删除失败: {e}")
                        else:
                            print(f"  [Dry Run] 将删除")
                            deleted_folders.append(str(video_folder))
                    
                    elif reason == 'folder_name_format':
                        # 文件夹名格式不对，但有视频文件 - 需要重新整理
                        video_file = find_video_in_folder(video_folder)
                        if video_file:
                            print(f"\n⚠ 非标准文件夹: {folder_rel}")
                            print(f"  视频: {os.path.basename(video_file)}")
                            print(f"  将重新整理")
                            videos_to_reorganize.append(video_file)
            
            # 检查女优目录是否为空
            try:
                if not any(actress_dir.iterdir()):
                    print(f"\n✗ 空女优目录: {studio_name}/{actress_name}")
                    if not dry_run:
                        actress_dir.rmdir()
                        print(f"  ✓ 已删除")
                    else:
                        print(f"  [Dry Run] 将删除")
            except:
                pass
        
        # 检查厂商目录是否为空
        try:
            if not any(studio_dir.iterdir()):
                print(f"\n✗ 空厂商目录: {studio_name}")
                if not dry_run:
                    studio_dir.rmdir()
                    print(f"  ✓ 已删除")
                else:
                    print(f"  [Dry Run] 将删除")
        except:
            pass
    
    return deleted_folders, videos_to_reorganize

def find_all_videos_in_directory(base_dir):
    """
    递归查找所有视频文件（包括非标准结构中的视频）
    """
    videos = []
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS:
                file_path = os.path.join(root, file)
                videos.append(file_path)
    
    return videos

def check_video_in_standard_location(video_path):
    """
    检查视频是否在标准位置
    标准位置: base_dir/厂商/女优/[番号] 标题/[番号] 标题.ext
    """
    path_parts = Path(video_path).parts
    
    # 至少需要: base/studio/actress/folder/video.ext (5层)
    if len(path_parts) < 5:
        return False
    
    video_folder = Path(video_path).parent
    video_folder_name = video_folder.name
    
    # 检查文件夹名格式
    if not (video_folder_name.startswith('[') and ']' in video_folder_name):
        return False
    
    # 检查是否有 metadata.json
    metadata_path = video_folder / 'metadata.json'
    if not metadata_path.exists():
        return False
    
    return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='清理和重新整理脚本')
    parser.add_argument('directory', help='要清理的目录')
    parser.add_argument('--dry-run', action='store_true', help='预览模式(不实际删除文件)')
    parser.add_argument('--clean-only', action='store_true', help='只清理，不重新整理')
    
    args = parser.parse_args()
    
    base_dir = os.path.abspath(args.directory)
    
    if not os.path.isdir(base_dir):
        print(f"错误: 目录不存在: {base_dir}")
        sys.exit(1)
    
    print("=" * 70)
    print("AV 清理和重新整理脚本")
    print("=" * 70)
    print(f"目录: {base_dir}")
    print(f"模式: {'预览' if args.dry_run else '执行'}")
    print("=" * 70)
    
    # 第一步: 清理空文件夹和不标准的文件夹
    deleted_folders, videos_to_reorganize = clean_empty_and_invalid_folders(
        base_dir, 
        dry_run=args.dry_run
    )
    
    print("\n" + "=" * 70)
    print("清理统计")
    print("=" * 70)
    print(f"删除的空文件夹: {len(deleted_folders)}")
    print(f"需要重新整理的视频: {len(videos_to_reorganize)}")
    
    if videos_to_reorganize:
        print("\n需要重新整理的视频:")
        for video in videos_to_reorganize[:10]:  # 只显示前10个
            print(f"  - {os.path.basename(video)}")
        if len(videos_to_reorganize) > 10:
            print(f"  ... 还有 {len(videos_to_reorganize) - 10} 个")
    
    # 第二步: 查找所有非标准位置的视频
    if not args.clean_only:
        print("\n" + "=" * 70)
        print("扫描非标准位置的视频...")
        print("=" * 70)
        
        all_videos = find_all_videos_in_directory(base_dir)
        non_standard_videos = [
            v for v in all_videos 
            if not check_video_in_standard_location(v)
        ]
        
        print(f"找到 {len(all_videos)} 个视频文件")
        print(f"其中 {len(non_standard_videos)} 个不在标准位置")
        
        if non_standard_videos:
            print("\n非标准位置的视频:")
            for video in non_standard_videos[:10]:
                print(f"  - {video}")
            if len(non_standard_videos) > 10:
                print(f"  ... 还有 {len(non_standard_videos) - 10} 个")
            
            print("\n提示: 运行以下命令重新整理这些视频:")
            print(f"  py -3 organize_v2.py \"{base_dir}\" --reorganize")
    
    if args.dry_run:
        print("\n注意: 这是预览模式,未实际删除文件")
        print("确认无误后,去掉 --dry-run 参数执行")

if __name__ == "__main__":
    main()
