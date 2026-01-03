"""
Rewriter module - Uses Gemini AI (primary) and Groq (fallback) to rewrite articles
"""

import os
import json
import re
from typing import Optional
from datetime import datetime


class Rewriter:
    """Rewrites articles using AI APIs with automatic fallback"""

    REWRITE_PROMPT = """你是一位专业的AI领域技术博主。请基于以下原文，创作一篇全新的中文博客文章。

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
{content}

请严格按照以下JSON格式输出（不要添加任何其他文字）：
{{
    "title": "中文标题（吸引人但不标题党）",
    "summary": "一句话摘要（50字以内）",
    "tags": ["标签1", "标签2", "标签3"],
    "categories": ["AI资讯"],
    "content": "正文内容（Markdown格式，包含小标题和段落）"
}}"""

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        groq_api_key: Optional[str] = None
    ):
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")

        self.gemini_model = None
        self.groq_client = None

        # Initialize Gemini
        if self.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")
                print("Gemini API initialized")
            except Exception as e:
                print(f"Failed to initialize Gemini: {e}")

        # Initialize Groq
        if self.groq_api_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_api_key)
                print("Groq API initialized")
            except Exception as e:
                print(f"Failed to initialize Groq: {e}")

        if not self.gemini_model and not self.groq_client:
            raise ValueError("At least one API (GEMINI_API_KEY or GROQ_API_KEY) is required")

    def rewrite(self, title: str, content: str, source_name: str, source_url: str) -> Optional[dict]:
        """
        Rewrite an article using AI APIs with automatic fallback

        Returns:
            dict with keys: title, summary, tags, categories, content
        """
        prompt = self.REWRITE_PROMPT.format(
            title=title,
            source_name=source_name,
            source_url=source_url,
            content=content[:8000]
        )

        # Try Gemini first
        if self.gemini_model:
            result = self._try_gemini(prompt)
            if result:
                print("    [Gemini] Success")
                return result
            print("    [Gemini] Failed, trying Groq...")

        # Fallback to Groq
        if self.groq_client:
            result = self._try_groq(prompt)
            if result:
                print("    [Groq] Success")
                return result
            print("    [Groq] Failed")

        return None

    def _try_gemini(self, prompt: str) -> Optional[dict]:
        """Try to generate content using Gemini API"""
        try:
            response = self.gemini_model.generate_content(prompt)
            result_text = response.text
            return self._parse_json_response(result_text)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                print(f"    [Gemini] Quota exceeded")
            else:
                print(f"    [Gemini] Error: {e}")
            return None

    def _try_groq(self, prompt: str) -> Optional[dict]:
        """Try to generate content using Groq API"""
        try:
            # Use a more explicit JSON prompt for Groq
            json_prompt = prompt + "\n\n重要：只输出JSON，不要输出任何其他文字、解释或markdown代码块标记。"

            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional AI technology blogger. You MUST respond with ONLY valid JSON, no markdown, no explanations, no code blocks. Just pure JSON object starting with { and ending with }."
                    },
                    {
                        "role": "user",
                        "content": json_prompt
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.5,
                max_tokens=4096,
                response_format={"type": "json_object"}
            )
            result_text = chat_completion.choices[0].message.content
            return self._parse_json_response(result_text)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate" in error_str.lower():
                print(f"    [Groq] Rate limited")
            else:
                print(f"    [Groq] Error: {e}")
            return None

    def _parse_json_response(self, text: str) -> Optional[dict]:
        """Parse JSON from AI response, handling markdown code blocks"""
        # Try to extract JSON from markdown code block
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)

        # Try to find JSON object directly
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                # Validate required fields
                required_fields = ["title", "summary", "tags", "content"]
                if all(field in result for field in required_fields):
                    return result
            except json.JSONDecodeError:
                pass

        # Try parsing the whole text
        try:
            result = json.loads(text)
            required_fields = ["title", "summary", "tags", "content"]
            if all(field in result for field in required_fields):
                return result
        except json.JSONDecodeError:
            pass

        print("    Failed to parse JSON response")
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
    # Test
    rewriter = Rewriter()
    result = rewriter.rewrite(
        title="Test Article",
        content="This is a test article about AI...",
        source_name="Test Source",
        source_url="https://example.com"
    )
    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
