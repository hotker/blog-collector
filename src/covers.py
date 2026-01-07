"""
Cover images module - AI-generated cover images using multiple providers (Pollinations AI, Hugging Face, Gemini)
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
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  # Optional
UPLOAD_URL = "https://imagine.hotker.com/upload?authCode=130075"
IMAGE_BASE_URL = "https://imagine.hotker.com"

# Pollinations AI API (free, no auth required)
POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"

# Hugging Face Inference API (requires token)
HF_INFERENCE_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1-base"

# Initialize clients
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


def generate_cover_image_pollinations(keywords: str, style: str) -> bytes:
    """
    Generate cover image using Pollinations AI (completely free, no auth required).

    Args:
        keywords: Keywords describing the image content
        style: Style for the image

    Returns:
        Image bytes (PNG format)
    """
    from urllib.parse import quote

    prompt = f"Blog cover about {keywords}, {style} style, tech blog header, professional, no text"

    print(f"    [Cover Pollinations] Generating image for keywords: {keywords}, style: {style}")

    # Build URL with parameters
    prompt_encoded = quote(prompt)
    url = f"{POLLINATIONS_BASE_URL}/{prompt_encoded}?width=1280&height=720&seed={hash(keywords + style) % 1000000}&nologo=true&model=flux"

    try:
        response = requests.get(url, timeout=180)
        response.raise_for_status()

        image_bytes = response.content
        print(f"    [Cover Pollinations] Generated {len(image_bytes)} bytes")
        return image_bytes

    except requests.RequestException as e:
        raise ValueError(f"Pollinations AI request failed: {e}")


def generate_cover_image(keywords: str, style: str) -> bytes:
    """
    Generate cover image using Hugging Face Inference API (SD2.1).

    Args:
        keywords: Keywords describing the image content
        style: Style for the image

    Returns:
        Image bytes (PNG format)
    """
    prompt = f"Blog cover about {keywords}, {style} style, tech blog header, professional, no text"

    print(f"    [Cover HF] Generating image for keywords: {keywords}, style: {style}")

    headers = {}
    if HUGGINGFACE_API_KEY:
        headers["Authorization"] = f"Bearer {HUGGINGFACE_API_KEY}"

    try:
        response = requests.post(
            HF_INFERENCE_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=120
        )

        if response.status_code == 200:
            image_bytes = response.content
            print(f"    [Cover HF] Generated {len(image_bytes)} bytes")
            return image_bytes
        elif response.status_code == 429:
            raise ValueError("Hugging Face rate limit exceeded")
        elif response.status_code == 503:
            # Model loading, wait and retry
            import time
            wait_time = response.json().get("estimated_time", 20)
            print(f"    [Cover HF] Model loading, waiting {wait_time}s...")
            time.sleep(wait_time)
            # Retry once
            response = requests.post(
                HF_INFERENCE_URL,
                headers=headers,
                json={"inputs": prompt},
                timeout=120
            )
            if response.status_code == 200:
                image_bytes = response.content
                print(f"    [Cover HF] Generated {len(image_bytes)} bytes after retry")
                return image_bytes
            raise ValueError(f"Hugging Face error after retry: {response.status_code}")
        else:
            raise ValueError(f"Hugging Face API error: {response.status_code} - {response.text[:200]}")

    except requests.RequestException as e:
        raise ValueError(f"Hugging Face request failed: {e}")


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
        model="imagen-3.0-generate-002",
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
    print(f"    [Upload] Sending {len(image_data)} bytes to {UPLOAD_URL}")

    try:
        response = requests.post(UPLOAD_URL, files=files, timeout=30)

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


def get_smart_cover(title: str, tags: Optional[List[str]] = None, summary: str = "") -> str:
    """
    Intelligently generate a cover image based on article content.
    Try Pollinations first (free, no auth), then Hugging Face, then Gemini, then default cover.

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

    # Try Pollinations AI first (free, no auth required)
    try:
        image_data = generate_cover_image_pollinations(keywords, style)
        image_url = upload_image(image_data)
        print(f"    [Cover] Generated cover using Pollinations AI")
        return image_url
    except Exception as e:
        print(f"    [Cover] Pollinations AI failed: {e}")

    # Fallback to Hugging Face (requires API key)
    if HUGGINGFACE_API_KEY:
        try:
            image_data = generate_cover_image(keywords, style)
            image_url = upload_image(image_data)
            print(f"    [Cover] Generated cover using Hugging Face (fallback)")
            return image_url
        except Exception as e:
            print(f"    [Cover] Hugging Face failed: {e}")

    # Fallback to Gemini
    if client:
        try:
            image_data = generate_cover_image_gemini(keywords, style)
            image_url = upload_image(image_data)
            print(f"    [Cover] Generated cover using Gemini (fallback)")
            return image_url
        except Exception as e:
            print(f"    [Cover] Gemini also failed: {e}")

    # Fallback to default cover
    print(f"    [Cover] Using default cover")
    return default_cover


if __name__ == "__main__":
    print("Testing AI cover generation (Pollinations AI -> Hugging Face -> Gemini)...")

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
    print("  1. Pollinations AI (free, no auth)")
    if HUGGINGFACE_API_KEY:
        print("  2. Hugging Face (requires API key)")
    else:
        print("  2. Hugging Face (skipped - no API key)")
    if client:
        print("  3. Gemini (requires API key)")
    else:
        print("  3. Gemini (skipped - no API key)")
    print("  4. Default cover")

    print("\nGenerating and uploading cover...")
    try:
        url = get_smart_cover(test_title, test_tags, test_summary)
        print(f"\nCover URL: {url}")
    except Exception as e:
        print(f"Error: {e}")
