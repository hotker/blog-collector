"""
Editorial Room module - Transforms articles into high-quality content using multi-persona AI agents.
"""

import os
import json
import re
import yaml
from typing import Optional, Dict, Any
from datetime import datetime

from src.covers import get_smart_cover
from src.personas import PERSONAS, DEFAULT_PERSONA, get_persona

class Rewriter:
    """Orchestrates the AI Editorial Room pipeline: Triage -> Critique -> Write"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: Optional[str] = None,
        config: Optional[Dict] = None
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_base = api_base or os.getenv("OPENAI_API_BASE", "https://api.hotker.com/v1")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.config = config or {}

        # Editorial settings
        self.enable_triage = self.config.get("editorial", {}).get("enable_auto_triage", True)
        self.default_persona = self.config.get("editorial", {}).get("default_persona", DEFAULT_PERSONA)

        self.client = None

        # Initialize OpenAI client
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.api_base
                )
                print(f"OpenAI API initialized (base: {self.api_base})")
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")

        if not self.client:
            raise ValueError("OPENAI_API_KEY is required")

    def rewrite(self, title: str, content: str, source_name: str, source_url: str) -> Optional[dict]:
        """
        Execute the editorial pipeline:
        1. Triage: Select the best persona
        2. Critique: Generate insights (if enabled)
        3. Write: Generate the final article
        """
        print(f"    [Editorial] Processing: {title[:30]}...")

        # Step 1: Triage
        persona_id = self.default_persona
        if self.enable_triage:
            persona_id = self._triage(title, content)
            print(f"    [Editorial] Selected Persona: {PERSONAS[persona_id]['name']}")

        persona = get_persona(persona_id)

        # Step 2: Critique (Optional, but recommended for depth)
        critique = self._critique(title, content, persona)
        if critique:
            print(f"    [Editorial] Generated critique with {len(critique)} insights")

        # Step 3: Write
        result = self._rewrite_with_persona(title, content, source_name, source_url, persona, critique)

        if result:
            # Add persona metadata for debugging/display
            result["_persona"] = persona_id
            print("    [Editorial] Success")
            return result

        print("    [Editorial] Failed")
        return None

    def _triage(self, title: str, content: str) -> str:
        """Analyze content to select the best persona"""
        prompt = f"""Analyze the following tech article and select the most suitable editorial persona to rewrite it.

Article Title: {title}
Article Excerpt: {content[:1000]}

Personas:
1. 'philosopher': For news about AI ethics, society, policy, or future humanity.
2. 'geek': For new tools, code releases, benchmarks, technical tutorials.
3. 'observer': For funding news, acquisitions, business strategy, market analysis.

Return ONLY a JSON object: {{"persona": "philosopher" | "geek" | "observer", "reason": "short explanation"}}
"""
        try:
            response = self._call_api(prompt, system_prompt="You are an Editor-in-Chief. Output JSON only.")
            if response and "persona" in response:
                pid = response["persona"].lower()
                if pid in PERSONAS:
                    return pid
        except Exception as e:
            print(f"    [Triage] Error: {e}")

        return self.default_persona

    def _critique(self, title: str, content: str, persona: Dict) -> Optional[str]:
        """Generate critical insights based on the persona's perspective"""
        prompt = f"""Read this article and identify 3 critical angles or deep insights to explore.

Article Title: {title}
Article Content: {content[:3000]}

Your Persona: {persona['name']}
{persona['system_prompt']}

Task: Provide 3 short, sharp, bullet-pointed insights that add depth to this story.
Focus on what is NOT said in the text.
"""
        # We don't need JSON here, just text is fine, but _call_api expects JSON parsing usually.
        # Let's use a simpler API call or just ask for JSON to keep it consistent.
        json_prompt = prompt + "\nReturn JSON: {{\"insights\": [\"insight 1\", \"insight 2\", \"insight 3\"]}}"

        try:
            response = self._call_api(json_prompt, system_prompt="You are an Analyst. Output JSON only.")
            if response and "insights" in response:
                return "\n".join(f"- {i}" for i in response["insights"])
        except Exception:
            pass
        return None

    def _rewrite_with_persona(
        self,
        title: str,
        content: str,
        source_name: str,
        source_url: str,
        persona: Dict,
        critique: Optional[str]
    ) -> Optional[dict]:
        """Rewrite the article using the specific persona and critique"""

        critique_section = ""
        if critique:
            critique_section = f"\nCritical Insights to Incorporate:\n{critique}\n"

        prompt = f"""你是一位专业的AI领域技术博主。请基于以下原文，创作一篇全新的中文博客文章。

【当前人设】：{persona['name']} ({persona['description']})
请务必坚持这个人设的语气和关注点！
{persona['system_prompt']}

【原文信息】
标题：{title}
来源：{source_name}
链接：{source_url}
内容：
{content[:6000]}

{critique_section}

【写作要求】
1. 深度重写，拒绝简单的翻译或搬运。
2. 必须融入【当前人设】的独特视角和语调。
3. 如果有"Critical Insights"，请自然地整合到文章分析中。
4. 结构清晰：引人入胜的标题 -> 独特的切入点 -> 核心分析 -> 总结与展望。
5. 字数：1000-2000字。

请严格按照以下JSON格式输出（不要添加任何其他文字）：
{{
    "title": "中文标题（必须符合人设风格）",
    "summary": "一句话摘要（50字以内）",
    "tags": ["标签1", "标签2", "标签3"],
    "categories": ["AI资讯"],
    "content": "正文内容（Markdown格式，包含小标题和段落）"
}}"""

        return self._call_api(prompt, system_prompt=f"You are {persona['name']}. You output ONLY valid JSON.")

    def _call_api(self, prompt: str, system_prompt: str = "") -> Optional[dict]:
        """Call OpenAI-compatible API"""
        if not system_prompt:
            system_prompt = "You are a helpful assistant. You MUST respond with ONLY valid JSON."

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4096
            )
            result_text = response.choices[0].message.content
            return self._parse_json_response(result_text)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate" in error_str.lower():
                print(f"    [API] Rate limited")
            else:
                print(f"    [API] Error: {e}")
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
                return result
            except json.JSONDecodeError:
                pass

        # Try parsing the whole text
        try:
            result = json.loads(text)
            return result
        except json.JSONDecodeError:
            pass

        print("    Failed to parse JSON response")
        return None

    def format_hexo_post(
        self,
        rewritten: dict,
        cover_url: str = "",
        source_url: str = ""
    ) -> str:
        """Format the rewritten content as a Hexo blog post"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")

        # Default cover if not provided - use smart selection based on article content
        if not cover_url:
            cover_url = get_smart_cover(
                title=rewritten.get('title', ''),
                tags=rewritten.get('tags', []),
                summary=rewritten.get('summary', '')
            )

        # Construct frontmatter dict
        frontmatter = {
            "title": rewritten['title'],
            "date": date_str,
            "tags": rewritten.get("tags", ["AI"]),
            "categories": rewritten.get("categories", ["AI资讯"]),
            "poster": {
                "topic": None,
                "headline": rewritten.get('summary', '')[:100],
                "caption": None,
                "color": None
            },
            "cover": cover_url,
            "banner": cover_url
        }

        # Generate YAML frontmatter
        yaml_str = yaml.dump(
            frontmatter,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False
        ).strip()

        # Add Persona badge to the content
        persona_badge = ""
        if "_persona" in rewritten:
            persona_name = get_persona(rewritten["_persona"])["name"]
            persona_badge = f"\n\n> *本文由 AI 编辑部【{persona_name}】撰写*"

        post = f"""---
{yaml_str}
---

{rewritten['content']}

---

> 本文基于 [{source_url}]({source_url}) 内容改编{persona_badge}
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
