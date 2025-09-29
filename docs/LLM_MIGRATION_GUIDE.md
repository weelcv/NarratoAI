# NarratoAI 大模型服务迁移指南

## 📋 概述

本指南帮助开发者将现有代码从旧的大模型调用方式迁移到新的统一LLM服务架构。新架构提供了更好的模块化、错误处理和配置管理。

## 🔄 迁移对比

### 旧的调用方式 vs 新的调用方式

#### 1. 视觉分析器创建

**旧方式：**
```python
from app.utils import gemini_analyzer, qwenvl_analyzer

if provider == 'gemini':
    analyzer = gemini_analyzer.VisionAnalyzer(
        model_name=model, 
        api_key=api_key, 
        base_url=base_url
    )
elif provider == 'qwenvl':
    analyzer = qwenvl_analyzer.QwenAnalyzer(
        model_name=model,
        api_key=api_key,
        base_url=base_url
    )
```

**新方式：**
```python
from app.services.llm.unified_service import UnifiedLLMService

# 方式1: 直接使用统一服务
results = await UnifiedLLMService.analyze_images(
    images=images,
    prompt=prompt,
    provider=provider  # 可选，使用配置中的默认值
)

# 方式2: 使用迁移适配器（向后兼容）
from app.services.llm.migration_adapter import create_vision_analyzer
analyzer = create_vision_analyzer(provider, api_key, model, base_url)
results = await analyzer.analyze_images(images, prompt)
```

#### 2. 文本生成

**旧方式：**
```python
from openai import OpenAI

client = OpenAI(api_key=api_key, base_url=base_url)
response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ],
    temperature=temperature,
    response_format={"type": "json_object"}
)
result = response.choices[0].message.content
```

**新方式：**
```python
from app.services.llm.unified_service import UnifiedLLMService

result = await UnifiedLLMService.generate_text(
    prompt=prompt,
    system_prompt=system_prompt,
    temperature=temperature,
    response_format="json"
)
```

#### 3. 解说文案生成

**旧方式：**
```python
from app.services.generate_narration_script import generate_narration

narration = generate_narration(
    markdown_content,
    api_key,
    base_url=base_url,
    model=model
)
# 手动解析JSON和验证格式
import json
narration_dict = json.loads(narration)['items']
```

**新方式：**
```python
from app.services.llm.unified_service import UnifiedLLMService

# 自动验证输出格式
narration_items = await UnifiedLLMService.generate_narration_script(
    prompt=prompt,
    validate_output=True  # 自动验证JSON格式和字段
)
```

## 📝 具体迁移步骤

### 步骤1: 更新配置文件

**旧配置格式：**
```toml
[app]
    llm_provider = "openai"
    openai_api_key = "sk-xxx"
    openai_model_name = "gpt-4"
    
    vision_llm_provider = "gemini"
    gemini_api_key = "xxx"
    gemini_model_name = "gemini-1.5-pro"
```

**新配置格式：**
```toml
[app]
    # 视觉模型配置
    vision_llm_provider = "gemini"
    vision_gemini_api_key = "xxx"
    vision_gemini_model_name = "gemini-2.0-flash-lite"
    vision_gemini_base_url = "https://generativelanguage.googleapis.com/v1beta"
    
    # 文本模型配置
    text_llm_provider = "openai"
    text_openai_api_key = "sk-xxx"
    text_openai_model_name = "gpt-4o-mini"
    text_openai_base_url = "https://api.openai.com/v1"
```

### 步骤2: 更新导入语句

**旧导入：**
```python
from app.utils import gemini_analyzer, qwenvl_analyzer
from app.services.generate_narration_script import generate_narration
from app.services.SDE.short_drama_explanation import analyze_subtitle
```

**新导入：**
```python
from app.services.llm.unified_service import UnifiedLLMService
from app.services.llm.migration_adapter import (
    create_vision_analyzer,
    SubtitleAnalyzerAdapter
)
```

### 步骤3: 更新函数调用

#### 图片分析迁移

**旧代码：**
```python
def analyze_images_old(provider, api_key, model, base_url, images, prompt):
    if provider == 'gemini':
        analyzer = gemini_analyzer.VisionAnalyzer(
            model_name=model, 
            api_key=api_key, 
            base_url=base_url
        )
    else:
        analyzer = qwenvl_analyzer.QwenAnalyzer(
            model_name=model,
            api_key=api_key,
            base_url=base_url
        )
    
    # 同步调用
    results = []
    for batch in batches:
        result = analyzer.analyze_batch(batch, prompt)
        results.append(result)
    return results
```

**新代码：**
```python
async def analyze_images_new(images, prompt, provider=None):
    # 异步调用，自动批处理
    results = await UnifiedLLMService.analyze_images(
        images=images,
        prompt=prompt,
        provider=provider,
        batch_size=10
    )
    return results
```

#### 字幕分析迁移

**旧代码：**
```python
from app.services.SDE.short_drama_explanation import analyze_subtitle

result = analyze_subtitle(
    subtitle_file_path=subtitle_path,
    api_key=api_key,
    model=model,
    base_url=base_url,
    provider=provider
)
```

**新代码：**
```python
# 方式1: 使用统一服务
with open(subtitle_path, 'r', encoding='utf-8') as f:
    subtitle_content = f.read()

result = await UnifiedLLMService.analyze_subtitle(
    subtitle_content=subtitle_content,
    provider=provider,
    validate_output=True
)

# 方式2: 使用适配器
from app.services.llm.migration_adapter import SubtitleAnalyzerAdapter

analyzer = SubtitleAnalyzerAdapter(api_key, model, base_url, provider)
result = analyzer.analyze_subtitle(subtitle_content)
```

## 🔧 常见迁移问题

### 1. 同步 vs 异步调用

**问题：** 新架构使用异步调用，旧代码是同步的。

**解决方案：**
```python
# 在同步函数中调用异步函数
import asyncio

def sync_function():
    result = asyncio.run(UnifiedLLMService.generate_text(prompt))
    return result

# 或者将整个函数改为异步
async def async_function():
    result = await UnifiedLLMService.generate_text(prompt)
    return result
```

### 2. 配置获取方式变化

**问题：** 配置键名发生变化。

**解决方案：**
```python
# 旧方式
api_key = config.app.get('openai_api_key')
model = config.app.get('openai_model_name')

# 新方式
provider = config.app.get('text_llm_provider', 'openai')
api_key = config.app.get(f'text_{provider}_api_key')
model = config.app.get(f'text_{provider}_model_name')
```

### 3. 错误处理更新

**旧方式：**
```python
try:
    result = some_llm_call()
except Exception as e:
    print(f"Error: {e}")
```

**新方式：**
```python
from app.services.llm.exceptions import LLMServiceError, ValidationError

try:
    result = await UnifiedLLMService.generate_text(prompt)
except ValidationError as e:
    print(f"输出验证失败: {e.message}")
except LLMServiceError as e:
    print(f"LLM服务错误: {e.message}")
except Exception as e:
    print(f"未知错误: {e}")
```

## ✅ 迁移检查清单

### 配置迁移
- [ ] 更新配置文件格式
- [ ] 验证所有API密钥配置正确
- [ ] 运行配置验证器检查

### 代码迁移
- [ ] 更新导入语句
- [ ] 将同步调用改为异步调用
- [ ] 更新错误处理机制
- [ ] 使用新的统一接口

### 测试验证
- [ ] 运行LLM服务测试脚本
- [ ] 测试所有功能模块
- [ ] 验证输出格式正确
- [ ] 检查性能和稳定性

### 清理工作
- [ ] 移除未使用的旧代码
- [ ] 更新文档和注释
- [ ] 清理过时的依赖

## 🚀 迁移最佳实践

### 1. 渐进式迁移
- 先迁移一个模块，测试通过后再迁移其他模块
- 保留旧代码作为备用方案
- 使用迁移适配器确保向后兼容

### 2. 充分测试
- 在每个迁移步骤后运行测试
- 比较新旧实现的输出结果
- 测试边界情况和错误处理

### 3. 监控和日志
- 启用详细日志记录
- 监控API调用成功率
- 跟踪性能指标

### 4. 文档更新
- 更新代码注释
- 更新API文档
- 记录迁移过程中的问题和解决方案

## 📞 获取帮助

如果在迁移过程中遇到问题：

1. **查看测试脚本输出**：
   ```bash
   python app/services/llm/test_llm_service.py
   ```

2. **验证配置**：
   ```python
   from app.services.llm.config_validator import LLMConfigValidator
   results = LLMConfigValidator.validate_all_configs()
   LLMConfigValidator.print_validation_report(results)
   ```

3. **查看详细日志**：
   ```python
   from loguru import logger
   logger.add("migration.log", level="DEBUG")
   ```

4. **参考示例代码**：
   - 查看 `app/services/llm/test_llm_service.py` 中的使用示例
   - 参考已迁移的文件如 `webui/tools/base.py`

---

*最后更新: 2025-01-07*
