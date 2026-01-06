"""
Cover images module - AI-generated cover images using Gemini
"""

import os
import io
import json
import requests
from typing import Optional, List

from google import genai
from google.genai import types

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
UPLOAD_URL = "https://imagine.hotker.com/upload?authCode=130075"
IMAGE_BASE_URL = "https://imagine.hotker.com"

# Initialize Gemini client
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


def analyze_content(title: str, tags: Optional[List[str]] = None, summary: str = "") -> dict:
    """
    Use Gemini to analyze article content and extract keywords + style.

    Args:
        title: Article title
        tags: List of article tags
        summary: Article summary

    Returns:
        dict with 'keywords' and 'style' keys
    """
    if not client:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    content = f"""分析以下文章内容，提取关键词和推荐的封面图片风格。

标题: {title}
标签: {', '.join(tags or [])}
摘要: {summary[:500] if summary else '无'}

请用JSON格式返回:
{{
    "keywords": "3-5个英文关键词，用逗号分隔",
    "style": "推荐的图片风格，从以下选择一个: futuristic tech, digital art, minimalist illustration, abstract geometric, cyberpunk, clean modern"
}}

只返回JSON，不要其他内容。"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=content
    )

    try:
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except (json.JSONDecodeError, IndexError):
        return {
            "keywords": "artificial intelligence, technology, innovation",
            "style": "futuristic tech"
        }


def generate_cover_image(keywords: str, style: str) -> bytes:
    """
    Generate cover image using Gemini Imagen.

    Args:
        keywords: Keywords describing the image content
        style: Style for the image

    Returns:
        Image bytes (PNG format)
    """
    if not client:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    prompt = f"Create a blog cover image. Theme: {keywords}. Style: {style}. Visually appealing, professional, suitable for a tech blog header. No text in the image."

    response = client.models.generate_images(
        model="imagen-3.0-generate-002",
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="16:9",
            safety_filter_level="BLOCK_ONLY_HIGH",
        )
    )

    return response.generated_images[0].image.image_bytes


def upload_image(image_data: bytes) -> str:
    """
    Upload image to image hosting service.

    Args:
        image_data: Image bytes

    Returns:
        Full URL of uploaded image
    """
    files = {"file": ("cover.png", io.BytesIO(image_data), "image/png")}
    response = requests.post(UPLOAD_URL, files=files, timeout=30)
    response.raise_for_status()

    result = response.json()
    src = result[0]["src"]

    if src.startswith("http"):
        return src
    return f"{IMAGE_BASE_URL}{src}"


def get_smart_cover(title: str, tags: Optional[List[str]] = None, summary: str = "") -> str:
    """
    Intelligently generate a cover image based on article content.

    Args:
        title: Article title
        tags: List of article tags
        summary: Article summary

    Returns:
        URL of the generated cover image
    """
    analysis = analyze_content(title, tags, summary)
    keywords = analysis.get("keywords", "technology, AI, innovation")
    style = analysis.get("style", "futuristic tech")

    image_data = generate_cover_image(keywords, style)
    image_url = upload_image(image_data)

    return image_url


if __name__ == "__main__":
    print("Testing Gemini cover generation...")

    if not client:
        print("Error: GEMINI_API_KEY not set")
    else:
        print("\nAnalyzing content for 'ChatGPT新功能发布'...")
        analysis = analyze_content("ChatGPT新功能发布", ["AI", "OpenAI"], "OpenAI发布了ChatGPT的新功能")
        print(f"Keywords: {analysis.get('keywords')}")
        print(f"Style: {analysis.get('style')}")

        print("\nGenerating and uploading cover...")
        try:
            url = get_smart_cover("ChatGPT新功能发布", ["AI", "OpenAI"], "OpenAI发布了ChatGPT的新功能")
            print(f"Cover URL: {url}")
        except Exception as e:
            print(f"Error: {e}")
