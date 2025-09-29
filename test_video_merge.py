#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
测试视频合并功能，验证重复片段问题是否已解决
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.merger_video import combine_clip_videos, VideoAspect


def create_test_video(duration=5, filename="test_video.mp4"):
    """创建测试视频文件"""
    # 使用ffmpeg创建一个简单的测试视频
    import subprocess
    
    output_path = os.path.join(tempfile.gettempdir(), filename)
    
    # 创建一个纯色视频用于测试
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', f'color=c=blue:s=1080x1920:d={duration}:r=30',
        '-c:v', 'libx264',
        '-t', str(duration),
        '-pix_fmt', 'yuv420p',
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"创建测试视频失败: {e}")
        return None


def test_duplicate_fragment_handling():
    """测试重复片段处理逻辑"""
    print("开始测试重复片段处理...")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    output_video = os.path.join(temp_dir, "merged_output.mp4")
    
    try:
        # 创建几个测试视频
        video1 = create_test_video(3, "test1.mp4")
        video2 = create_test_video(4, "test2.mp4")
        video3 = create_test_video(2, "test3.mp4")
        
        if not all([video1, video2, video3]):
            print("创建测试视频失败")
            return False
            
        # 测试1: 正常情况 - 无重复片段
        print("\n测试1: 正常情况 - 无重复片段")
        video_paths = [video1, video2, video3]
        video_ost_list = [0, 1, 2]
        
        try:
            result = combine_clip_videos(
                output_video_path=output_video,
                video_paths=video_paths,
                video_ost_list=video_ost_list,
                video_aspect=VideoAspect.portrait,
                threads=2
            )
            print(f"正常合并成功: {result}")
        except Exception as e:
            print(f"正常合并失败: {e}")
            return False
            
        # 测试2: 包含重复片段的情况
        print("\n测试2: 包含重复片段的情况")
        duplicate_video_paths = [video1, video2, video1, video3, video2]  # 包含重复
        duplicate_ost_list = [0, 1, 0, 2, 1]  # 对应的OST列表
        
        try:
            result = combine_clip_videos(
                output_video_path=output_video.replace(".mp4", "_duplicate.mp4"),
                video_paths=duplicate_video_paths,
                video_ost_list=duplicate_ost_list,
                video_aspect=VideoAspect.portrait,
                threads=2
            )
            print(f"重复片段合并成功: {result}")
            print("重复片段问题已解决!")
            return True
        except Exception as e:
            print(f"重复片段合并失败: {e}")
            return False
            
    finally:
        # 清理测试文件
        try:
            shutil.rmtree(temp_dir)
            for video in [video1, video2, video3]:
                if video and os.path.exists(video):
                    os.remove(video)
        except Exception as e:
            print(f"清理测试文件失败: {e}")


if __name__ == "__main__":
    print("视频合并重复片段处理测试")
    print("=" * 40)
    
    success = test_duplicate_fragment_handling()
    
    if success:
        print("\n✅ 所有测试通过，重复片段问题已解决!")
    else:
        print("\n❌ 测试失败，请检查代码实现")