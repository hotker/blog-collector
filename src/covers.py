"""
Cover images module - AI-generated cover images using multiple providers (Pollinations.ai, Gemini)
"""

import os
import io
import json
import requests
import random
from typing import Optional, List
from urllib.parse import quote
from src.utils import get_retry_session

from google import genai
from google.genai import types

# Lazy session initialization
_session = None

# Fallback Image Library (Curated High-Quality Unsplash Images)
FALLBACK_IMAGES = {
    "ai": [
        "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200&q=80",  # Abstract AI brain
        "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1200&q=80",  # Neural network particles
        "https://images.unsplash.com/photo-1675271591211-126ad94e495d?w=1200&q=80",  # AI Humanoid hand
        "https://images.unsplash.com/photo-1655720031554-a929595ff968?w=1200&q=80",  # Digital brain visualization
    ],
    "code": [
        "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200&q=80",  # Coding screen dark mode
        "https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=1200&q=80",  # Source code generic
        "https://images.unsplash.com/photo-1607799275518-d750cc6867a8?w=1200&q=80",  # Programmer keyboard
    ],
    "robot": [
        "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1200&q=80",  # White sleek robot
        "https://images.unsplash.com/photo-1535378437327-b7149a516c17?w=1200&q=80",  # Robot close up
    ],
    "default": [
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=80",  # Tech chips/circuits
        "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1200&q=80",  # Team working tech
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&q=80",  # Global network abstract
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1200&q=80",  # Cyberpunk city
    ]
}

def _get_session():
    global _session
    if _session is None:
        _session = get_retry_session()
    return _session


def _get_gemini_api_key():
    """Get Gemini API key from environment."""
    return os.getenv("GEMINI_API_KEY")


# Configuration
UPLOAD_URL = "https://imagine.hotker.com/upload?authCode=130075"
IMAGE_BASE_URL = "https://imagine.hotker.com"

# Initialize Gemini client
client = None
if _get_gemini_api_key():
    client = genai.Client(api_key=_get_gemini_api_key())


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


def generate_cover_url(keywords: str, style: str) -> str:
    """
    Generate cover image URL using Pollinations.ai (free, no API key required).
    Returns the URL directly - Pollinations.ai URLs are persistent.

    Args:
        keywords: Keywords describing the image content
        style: Style for the image

    Returns:
        Direct URL to the generated image
    """
    prompt = f"Blog cover about {keywords}, {style} style, tech blog header, professional, no text"
    encoded_prompt = quote(prompt)

    # Pollinations.ai URL-based API
    # Using flux model for better quality, 16:9 aspect ratio for blog covers
    # Add seed for cache-friendly reproducible results
    import hashlib
    seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&model=flux&nologo=true&seed={seed}"

    print(f"    [Cover Pollinations] Generating URL for keywords: {keywords}, style: {style}")

    # Verify the URL works by making a HEAD request
    try:
        session = _get_session()
        response = session.head(url, timeout=30, allow_redirects=True)
        if response.status_code == 200:
            print(f"    [Cover Pollinations] URL verified: {url[:80]}...")
            return url
        else:
            raise ValueError(f"Pollinations.ai returned status {response.status_code}")
    except Exception as e:
        raise ValueError(f"Pollinations.ai request failed: {e}")


def generate_cover_image(keywords: str, style: str) -> bytes:
    """
    Generate cover image bytes using Pollinations.ai (for upload fallback).

    Args:
        keywords: Keywords describing the image content
        style: Style for the image

    Returns:
        Image bytes (PNG format)
    """
    prompt = f"Blog cover about {keywords}, {style} style, tech blog header, professional, no text"
    encoded_prompt = quote(prompt)

    import hashlib
    seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&model=flux&nologo=true&seed={seed}"

    print(f"    [Cover Pollinations] Downloading image for keywords: {keywords}, style: {style}")

    try:
        session = _get_session()
        response = session.get(url, timeout=60)
        response.raise_for_status()

        image_bytes = response.content
        print(f"    [Cover Pollinations] Downloaded {len(image_bytes)} bytes")
        return image_bytes

    except Exception as e:
        raise ValueError(f"Pollinations.ai request failed: {e}")


def generate_cover_image_gemini(keywords: str, style: str) -> bytes:
    """
    Generate cover image using Gemini Imagen (fallback).

    Args:
        keywords: Keywords describing the image content
        style: Style for the image

    Returns:
        Image bytes (PNG format)
    """
    if not client:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    prompt = f"Create a blog cover image. Theme: {keywords}. Style: {style}. Visually appealing, professional, suitable for a tech blog header. No text in the image."

    print(f"    [Cover Gemini] Generating image for keywords: {keywords}, style: {style}")
    response = client.models.generate_images(
        model="imagen-3.0-generate-001",
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="16:9",
            safety_filter_level="BLOCK_ONLY_HIGH",
        )
    )

    if not response.generated_images:
        raise ValueError("No images generated by Gemini")

    image_bytes = response.generated_images[0].image.image_bytes
    print(f"    [Cover Gemini] Generated {len(image_bytes)} bytes")
    return image_bytes


def upload_image(image_data: bytes) -> str:
    """
    Upload image to image hosting service.

    Args:
        image_data: Image bytes

    Returns:
        Full URL of uploaded image
    """
    if not image_data:
        raise ValueError("Empty image data provided for upload")

    files = {"file": ("cover.png", io.BytesIO(image_data), "image/png")}
    # Add User-Agent to bypass Cloudflare basic bot protection
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }
    print(f"    [Upload] Sending {len(image_data)} bytes to {UPLOAD_URL}")

    try:
        session = _get_session()
        response = session.post(UPLOAD_URL, files=files, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f"    [Upload] Error: {response.status_code} - {response.text}")
            response.raise_for_status()

        result = response.json()
        print(f"    [Upload] Response: {result}")

        # Extremely robust parsing to handle various image hosting response formats
        src = None

        # 1. Check for 'src' or 'url' in direct result if it's a dict
        if isinstance(result, dict):
            src = result.get("src") or result.get("url")

            # 2. Check nested in 'data' field (common for many image hosts)
            if not src and "data" in result:
                data = result["data"]
                if isinstance(data, dict):
                    src = data.get("src") or data.get("url") or data.get("links", {}).get("url")
                elif isinstance(data, list) and len(data) > 0:
                    src = data[0].get("src") or data[0].get("url")

            # 3. Check for specific structures like {'status': 'success', 'url': '...'}
            if not src and result.get("status") in [True, "success", 200]:
                src = result.get("url") or result.get("link")

        # 4. Check if result is a list (original behavior)
        elif isinstance(result, list) and len(result) > 0:
            src = result[0].get("src") or result[0].get("url")

        if not src:
            raise ValueError(f"Could not find image URL in response: {result}")

        if src.startswith("http"):
            return src
        return f"{IMAGE_BASE_URL}{src if src.startswith('/') else '/' + src}"

    except Exception as e:
        print(f"    [Upload] Failed: {e}")
        raise


def _get_fallback_cover(tags: Optional[List[str]] = None) -> str:
    """Select a fallback cover based on tags."""
    if not tags:
        return random.choice(FALLBACK_IMAGES["default"])

    # Normalize tags to lowercase for matching
    tags_lower = [t.lower() for t in tags]

    # Check for categories
    if any(k in t for t in tags_lower for k in ["ai", "gpt", "llm", "neural", "model", "diffusion"]):
        return random.choice(FALLBACK_IMAGES["ai"])

    if any(k in t for t in tags_lower for k in ["code", "python", "javascript", "dev", "programming", "api"]):
        return random.choice(FALLBACK_IMAGES["code"])

    if any(k in t for t in tags_lower for k in ["robot", "hardware", "bot", "drone"]):
        return random.choice(FALLBACK_IMAGES["robot"])

    # Default fallback
    return random.choice(FALLBACK_IMAGES["default"])


def get_smart_cover(title: str, tags: Optional[List[str]] = None, summary: str = "") -> str:
    """
    Intelligently generate a cover image based on article content.
    Try Hugging Face first, then Gemini, then default cover.

    Args:
        title: Article title
        tags: List of article tags
        summary: Article summary

    Returns:
        URL of the generated cover image or a default one
    """
    default_cover = "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200"

    # Try to load default cover from config if possible
    try:
        import yaml
        from pathlib import Path
        config_path = Path(__file__).parent.parent / "config.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                default_cover = config.get("default_cover", default_cover)
    except Exception:
        pass

    # Analyze content (use Gemini if available, otherwise use hardcoded keywords)
    try:
        if client:
            analysis = analyze_content(title, tags, summary)
            keywords = analysis.get("keywords", "technology, AI, innovation")
            style = analysis.get("style", "futuristic tech")
        else:
            # Simple keyword extraction from title and tags
            keywords = (", ".join(tags or [])).replace(" ", ", ") if tags else "technology"
            style = "futuristic tech"
    except Exception as e:
        print(f"    [Cover] Content analysis failed: {e}")
        keywords = "technology, AI, innovation"
        style = "futuristic tech"

    # Try Pollinations.ai direct URL first (no upload needed, bypasses Cloudflare)
    try:
        image_url = generate_cover_url(keywords, style)
        print(f"    [Cover] Generated cover using Pollinations.ai (direct URL)")
        return image_url
    except Exception as e:
        print(f"    [Cover] Pollinations.ai direct URL failed: {e}")

    # Fallback: Try Pollinations.ai with upload to our server
    try:
        image_data = generate_cover_image(keywords, style)
        image_url = upload_image(image_data)
        print(f"    [Cover] Generated cover using Pollinations.ai (uploaded)")
        return image_url
    except Exception as e:
        print(f"    [Cover] Pollinations.ai upload failed: {e}")

    # Fallback to Gemini
    if client:
        try:
            image_data = generate_cover_image_gemini(keywords, style)
            image_url = upload_image(image_data)
            print(f"    [Cover] Generated cover using Gemini (fallback)")
            return image_url
        except Exception as e:
            print(f"    [Cover] Gemini also failed: {e}")

    # Fallback to smart fallback selection
    print(f"    [Cover] Using smart fallback cover")
    return _get_fallback_cover(tags)


if __name__ == "__main__":
    print("Testing AI cover generation (Pollinations.ai -> Gemini)...")

    test_title = "ChatGPT新功能发布"
    test_tags = ["AI", "OpenAI", "LLM"]
    test_summary = "OpenAI发布了ChatGPT的新功能，支持多模态输入输出"

    print(f"\nAnalyzing content for '{test_title}'...")

    if client:
        print("Found GEMINI_API_KEY - using for content analysis")
        try:
            analysis = analyze_content(test_title, test_tags, test_summary)
            print(f"Keywords: {analysis.get('keywords')}")
            print(f"Style: {analysis.get('style')}")
        except Exception as e:
            print(f"Analysis failed: {e}")
    else:
        print("No GEMINI_API_KEY found - using simple keyword extraction")

    print("\nProvider Priority:")
    print("  1. Pollinations.ai (primary, free, no API key needed)")
    if client:
        print("  2. Gemini (fallback, requires API key)")
    else:
        print("  2. Gemini (skipped - no API key)")
    print("  3. Default cover")

    print("\nGenerating and uploading cover...")
    try:
        url = get_smart_cover(test_title, test_tags, test_summary)
        print(f"\nCover URL: {url}")
    except Exception as e:
        print(f"Error: {e}")
