#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
综合测试脚本，验证视频处理流程中的ID唯一性和时间戳处理
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.update_script import update_script_timestamps
from app.services.merger_video import VideoAspect


def test_comprehensive_video_processing():
    """综合测试视频处理流程"""
    print("开始综合测试视频处理流程...")
    
    # 创建测试脚本数据
    test_script_list = [
        {
            "picture": "开场画面",
            "timestamp": "00:00:00,000-00:00:15,000",
            "narration": "欢迎观看本期视频",
            "OST": 1,
            "_id": 1
        },
        {
            "picture": "主要内容",
            "timestamp": "00:00:15,000-00:00:30,000",
            "narration": "这里是主要内容",
            "OST": 0,
            "_id": 2
        },
        {
            "picture": "结尾画面",
            "timestamp": "00:00:30,000-00:00:45,000",
            "narration": "感谢观看",
            "OST": 1,
            "_id": 3
        }
    ]
    
    # 创建测试视频结果数据
    test_video_result = {
        1: "/path/to/video1.mp4",
        2: "/path/to/video2.mp4",
        3: "/path/to/video3.mp4"
    }
    
    # 创建测试音频结果数据
    test_audio_result = {
        1: "/path/to/audio1.mp3",
        2: "/path/to/audio2.mp3"
    }
    
    # 创建测试字幕结果数据
    test_subtitle_result = {
        1: "/path/to/subtitle1.srt",
        2: "/path/to/subtitle2.srt"
    }
    
    try:
        print("\n测试1: 脚本时间戳更新处理")
        result = update_script_timestamps(
            script_list=test_script_list,
            video_result=test_video_result,
            audio_result=test_audio_result,
            subtitle_result=test_subtitle_result
        )
        
        # 验证结果
        if len(result) != len(test_script_list):
            print(f"❌ 脚本数量不匹配: 期望 {len(test_script_list)}, 实际 {len(result)}")
            return False
            
        # 检查每个片段都有必要的字段
        for i, item in enumerate(result):
            required_fields = ['_id', 'picture', 'timestamp', 'narration', 'OST', 
                             'sourceTimeRange', 'duration', 'editedTimeRange', 
                             'audio', 'subtitle', 'video']
            for field in required_fields:
                if field not in item:
                    print(f"❌ 片段 {i+1} 缺少必要字段: {field}")
                    return False
                    
            # 检查ID唯一性
            item_id = item.get('_id')
            if item_id is None:
                print(f"❌ 片段 {i+1} 缺少ID")
                return False
                
            # 检查时间戳格式
            if 'sourceTimeRange' not in item or not item['sourceTimeRange']:
                print(f"❌ 片段 {i+1} 缺少源时间戳")
                return False
                
            if 'editedTimeRange' not in item or not item['editedTimeRange']:
                print(f"❌ 片段 {i+1} 缺少编辑时间戳")
                return False
                
            # 检查持续时间
            if 'duration' not in item or item['duration'] <= 0:
                print(f"❌ 片段 {i+1} 持续时间无效: {item.get('duration', 'None')}")
                return False
                
            print(f"✅ 片段 {item_id}: 源时间={item['sourceTimeRange']}, 编辑时间={item['editedTimeRange']}, 持续时间={item['duration']}秒")
        
        print("✅ 脚本时间戳更新处理完成")
        
        # 测试重复ID处理
        print("\n测试2: 重复ID处理")
        test_script_with_duplicate_ids = [
            {
                "picture": "片段1",
                "timestamp": "00:00:00,000-00:00:10,000",
                "narration": "第一个片段",
                "OST": 1,
                "_id": 1
            },
            {
                "picture": "片段2(重复ID)",
                "timestamp": "00:00:10,000-00:00:20,000",
                "narration": "第二个片段",
                "OST": 0,
                "_id": 1  # 重复ID
            },
            {
                "picture": "片段3",
                "timestamp": "00:00:20,000-00:00:30,000",
                "narration": "第三个片段",
                "OST": 1,
                "_id": 3
            }
        ]
        
        result = update_script_timestamps(
            script_list=test_script_with_duplicate_ids,
            video_result=test_video_result,
            audio_result=test_audio_result
        )
        
        # 检查ID唯一性
        used_ids = set()
        for item in result:
            item_id = item.get('_id')
            if item_id in used_ids:
                print(f"❌ 发现重复ID: {item_id}")
                return False
            used_ids.add(item_id)
            
        print(f"✅ 重复ID处理完成，生成的唯一ID: {[item['_id'] for item in result]}")
        
        # 测试缺失ID处理
        print("\n测试3: 缺失ID处理")
        test_script_without_ids = [
            {
                "picture": "片段1",
                "timestamp": "00:00:00,000-00:00:10,000",
                "narration": "第一个片段",
                "OST": 1
                # 缺失_id字段
            },
            {
                "picture": "片段2",
                "timestamp": "00:00:10,000-00:00:20,000",
                "narration": "第二个片段",
                "OST": 0
                # 缺失_id字段
            }
        ]
        
        result = update_script_timestamps(
            script_list=test_script_without_ids,
            video_result=test_video_result,
            audio_result=test_audio_result
        )
        
        # 检查是否已分配ID
        for item in result:
            item_id = item.get('_id')
            if item_id is None:
                print("❌ 发现未分配ID的片段")
                return False
                
        print(f"✅ 缺失ID处理完成，分配的ID: {[item['_id'] for item in result]}")
        
        print("\n✅ 所有综合测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 综合测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_video_merger_aspect():
    """测试视频合并器的宽高比功能"""
    print("\n开始测试视频合并器宽高比功能...")
    
    try:
        # 测试所有支持的宽高比
        aspects = [
            (VideoAspect.portrait, (1080, 1920)),
            (VideoAspect.landscape, (1920, 1080)),
            (VideoAspect.square, (1080, 1080))
        ]
        
        for aspect, expected_resolution in aspects:
            resolution = aspect.to_resolution()
            if resolution != expected_resolution:
                print(f"❌ 宽高比 {aspect.value} 分辨率不正确: 期望 {expected_resolution}, 实际 {resolution}")
                return False
            print(f"✅ 宽高比 {aspect.value}: {resolution[0]}x{resolution[1]}")
            
        print("✅ 视频合并器宽高比功能测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 视频合并器宽高比功能测试失败: {e}")
        return False


if __name__ == "__main__":
    print("综合视频处理功能测试")
    print("=" * 40)
    
    success1 = test_comprehensive_video_processing()
    success2 = test_video_merger_aspect()
    
    if success1 and success2:
        print("\n🎉 所有综合测试通过，视频处理流程已正确实现ID唯一性和时间戳处理!")
    else:
        print("\n❌ 部分测试失败，请检查代码实现")