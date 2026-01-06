# Gemini 智能封面生成设计方案

## 概述

使用 Gemini AI 替换现有的 Unsplash 静态图库，根据文章内容智能生成封面图片。

## 架构流程

```
文章内容 (标题/摘要/标签)
         ↓
   Gemini 分析提取关键词
         ↓
   Gemini Imagen 生成图片
         ↓
   上传到 imagine.hotker.com
         ↓
   返回图片 URL 用于封面
```

## 环境变量

| 变量名 | 说明 |
|--------|------|
| `GEMINI_API_KEY` | Gemini API 密钥 |

## 图床配置

- **上传接口**: `POST https://imagine.hotker.com/upload?authCode=130075`
- **参数名**: `file`
- **响应解析**: `response[0].src`
- **完整 URL**: `https://imagine.hotker.com` + `src`

## 核心流程

### 1. 分析文章内容
调用 Gemini 文本模型分析文章：
- 输入: 标题 + 摘要 + 标签
- 输出: 关键词 + 推荐风格

### 2. 生成图片
构建 prompt 调用 Gemini Imagen：
- 示例: `"A futuristic tech illustration about: AI language models. Style: digital art, blue tones"`

### 3. 上传图床
- POST 图片到图床 API
- 解析返回的 src 路径
- 拼接完整 URL

## 代码结构

**`src/covers.py` 新结构：**

```python
import os
import requests
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
UPLOAD_URL = "https://imagine.hotker.com/upload?authCode=130075"
IMAGE_BASE_URL = "https://imagine.hotker.com"

def analyze_content(title: str, tags: list, summary: str) -> dict:
    """用 Gemini 分析文章，返回关键词和风格"""
    ...

def generate_cover_image(keywords: str, style: str) -> bytes:
    """用 Gemini Imagen 生成图片"""
    ...

def upload_image(image_data: bytes) -> str:
    """上传图片到图床，返回完整 URL"""
    ...

def get_smart_cover(title: str, tags: list, summary: str) -> str:
    """主函数：分析 → 生成 → 上传 → 返回 URL"""
    ...
```

## 依赖

新增 `requirements.txt`:
```
google-generativeai
```

## 错误处理

- API 调用失败时记录日志
- 可返回默认占位图或抛出异常
