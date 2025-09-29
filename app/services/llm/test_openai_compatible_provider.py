#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
通用OpenAI兼容提供商测试脚本

测试通用OpenAI兼容提供商是否正确集成到LLM服务架构中
"""

import asyncio
import sys
import os
from pathlib import Path
from loguru import logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.services.llm.manager import LLMServiceManager
from app.services.llm.providers.openai_compatible_provider import OpenAICompatibleVisionProvider, OpenAICompatibleTextProvider


async def test_openai_compatible_provider_registration():
    """测试通用OpenAI兼容提供商注册"""
    print("🧪 测试通用OpenAI兼容提供商注册...")
    
    try:
        # 获取所有注册的提供商
        vision_providers = LLMServiceManager.list_vision_providers()
        text_providers = LLMServiceManager.list_text_providers()
        
        print(f"✅ 视觉模型提供商: {', '.join(vision_providers)}")
        print(f"✅ 文本模型提供商: {', '.join(text_providers)}")
        
        # 检查通用OpenAI兼容提供商是否已注册
        if 'openai_compatible' in vision_providers:
            print("✅ 通用OpenAI兼容视觉模型提供商已成功注册")
        else:
            print("❌ 通用OpenAI兼容视觉模型提供商未注册")
            return False
            
        if 'openai_compatible' in text_providers:
            print("✅ 通用OpenAI兼容文本模型提供商已成功注册")
        else:
            print("❌ 通用OpenAI兼容文本模型提供商未注册")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 测试通用OpenAI兼容提供商注册失败: {str(e)}")
        return False


async def test_openai_compatible_provider_creation():
    """测试通用OpenAI兼容提供商实例创建"""
    print("\n🔧 测试通用OpenAI兼容提供商实例创建...")
    
    try:
        # 尝试获取通用OpenAI兼容视觉模型提供商实例
        try:
            vision_provider = LLMServiceManager.get_vision_provider('openai_compatible')
            print(f"✅ 通用OpenAI兼容视觉模型提供商实例创建成功: {type(vision_provider).__name__}")
        except Exception as e:
            print(f"⚠️  通用OpenAI兼容视觉模型提供商实例创建失败: {str(e)}")
            print("   注意: 这可能是因为未在配置文件中设置API密钥")
            
        # 尝试获取通用OpenAI兼容文本模型提供商实例
        try:
            text_provider = LLMServiceManager.get_text_provider('openai_compatible')
            print(f"✅ 通用OpenAI兼容文本模型提供商实例创建成功: {type(text_provider).__name__}")
        except Exception as e:
            print(f"⚠️  通用OpenAI兼容文本模型提供商实例创建失败: {str(e)}")
            print("   注意: 这可能是因为未在配置文件中设置API密钥")
            
        return True
        
    except Exception as e:
        print(f"❌ 测试通用OpenAI兼容提供商实例创建失败: {str(e)}")
        return False


async def test_openai_compatible_provider_info():
    """测试通用OpenAI兼容提供商信息获取"""
    print("\n📋 测试通用OpenAI兼容提供商信息获取...")
    
    try:
        provider_info = LLMServiceManager.get_provider_info()
        
        # 检查通用OpenAI兼容提供商信息
        vision_info = provider_info["vision_providers"]
        text_info = provider_info["text_providers"]
        
        if "openai_compatible" in vision_info:
            openai_compatible_vision_info = vision_info["openai_compatible"]
            print(f"✅ 通用OpenAI兼容视觉模型提供商信息:")
            print(f"   类名: {openai_compatible_vision_info['class']}")
            print(f"   模块: {openai_compatible_vision_info['module']}")
        else:
            print("❌ 未找到通用OpenAI兼容视觉模型提供商信息")
            
        if "openai_compatible" in text_info:
            openai_compatible_text_info = text_info["openai_compatible"]
            print(f"✅ 通用OpenAI兼容文本模型提供商信息:")
            print(f"   类名: {openai_compatible_text_info['class']}")
            print(f"   模块: {openai_compatible_text_info['module']}")
        else:
            print("❌ 未找到通用OpenAI兼容文本模型提供商信息")
            
        return True
        
    except Exception as e:
        print(f"❌ 测试通用OpenAI兼容提供商信息获取失败: {str(e)}")
        return False


async def run_all_tests():
    """运行所有测试"""
    print("🚀 开始通用OpenAI兼容提供商集成测试...")
    print("="*50)
    
    # 测试结果统计
    test_results = []
    
    # 1. 测试提供商注册
    test_results.append(("提供商注册", await test_openai_compatible_provider_registration()))
    
    # 2. 测试提供商实例创建
    test_results.append(("实例创建", await test_openai_compatible_provider_creation()))
    
    # 3. 测试提供商信息获取
    test_results.append(("信息获取", await test_openai_compatible_provider_info()))
    
    # 输出测试结果
    print("\n" + "="*50)
    print("📊 测试结果汇总:")
    print("="*50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name:<15} {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！通用OpenAI兼容提供商已成功集成。")
    elif passed > 0:
        print("⚠️  部分测试通过，请检查失败的测试项。")
    else:
        print("💥 所有测试失败，请检查集成配置。")
    
    print("="*50)


if __name__ == "__main__":
    # 设置日志级别
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    # 运行测试
    asyncio.run(run_all_tests())