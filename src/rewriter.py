"""
Rewriter module - Uses Gemini AI to rewrite articles
"""

import os
import json
import re
import google.generativeai as genai
from typing import Optional
from datetime import datetime


class Rewriter:
    """Rewrites articles using Gemini AI"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def rewrite(self, title: str, content: str, source_name: str, source_url: str) -> Optional[dict]:
        """
        Rewrite an article using Gemini AI

        Returns:
            dict with keys: title, summary, tags, categories, content
        """
        prompt = f"""你是一位专业的AI领域技术博主。请基于以下原文，创作一篇全新的中文博客文章。

要求：
1. 用自己的语言重新表达，不要直接翻译
2. 保留核心技术观点和数据
3. 添加个人见解和分析
4. 语言风格：专业但易懂，适合技术爱好者阅读
5. 文章结构：引言 → 核心内容 → 总结思考
6. 字数：800-1500字

原文标题：{title}
原文来源：{source_name}
原文链接：{source_url}
原文内容：
{content[:8000]}

请严格按照以下JSON格式输出（不要添加任何其他文字）：
{{
    "title": "中文标题（吸引人但不标题党）",
    "summary": "一句话摘要（50字以内）",
    "tags": ["标签1", "标签2", "标签3"],
    "categories": ["AI资讯"],
    "content": "正文内容（Markdown格式，包含小标题和段落）"
}}
"""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text

            # Extract JSON from response
            result = self._parse_json_response(result_text)

            if result:
                # Validate required fields
                required_fields = ["title", "summary", "tags", "content"]
                if all(field in result for field in required_fields):
                    return result

            print(f"Invalid response format from Gemini")
            return None

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return None

    def _parse_json_response(self, text: str) -> Optional[dict]:
        """Parse JSON from Gemini response, handling markdown code blocks"""
        # Try to extract JSON from markdown code block
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)

        # Try to find JSON object directly
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Try parsing the whole text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def generate_cover_prompt(self, title: str, summary: str) -> str:
        """Generate a prompt for AI image generation (for future use)"""
        return f"A professional tech blog cover image for an article about: {title}. {summary}. Modern, clean, abstract digital art style."

    def format_hexo_post(
        self,
        rewritten: dict,
        cover_url: str = "",
        source_url: str = ""
    ) -> str:
        """Format the rewritten content as a Hexo blog post"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")

        # Format tags
        tags_yaml = "\n".join(f"  - {tag}" for tag in rewritten.get("tags", ["AI"]))

        # Format categories
        categories = rewritten.get("categories", ["AI资讯"])
        categories_yaml = "\n".join(f"  - {cat}" for cat in categories)

        # Default cover if not provided
        if not cover_url:
            cover_url = "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200"

        post = f"""---
title: {rewritten['title']}
date: {date_str}
tags:
{tags_yaml}
categories:
{categories_yaml}
poster:
  topic: null
  headline: {rewritten.get('summary', '')[:100]}
  caption: null
  color: null
cover: {cover_url}
banner: {cover_url}
---

{rewritten['content']}

---

> 本文基于 [{source_url}]({source_url}) 内容改编
"""
        return post


if __name__ == "__main__":
    # Test with sample content
    rewriter = Rewriter()
    result = rewriter.rewrite(
        title="Test Article",
        content="This is a test article about AI...",
        source_name="Test Source",
        source_url="https://example.com"
    )
    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
