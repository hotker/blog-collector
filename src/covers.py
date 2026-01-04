"""
Cover images module - Provides diverse AI-related cover images for blog posts
"""

import random
from typing import Optional, List

# Curated collection of AI-related Unsplash images
# Each image is categorized by theme for potential future tag-based matching
AI_COVER_IMAGES = {
    # AI & Neural Networks
    "neural_network": [
        "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200",  # AI abstract
        "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1200",  # Brain network
        "https://images.unsplash.com/photo-1676299081847-824916de030a?w=1200",  # AI visualization
        "https://images.unsplash.com/photo-1655720033654-a4239dd42d10?w=1200",  # Neural patterns
    ],
    # Robots & Automation
    "robot": [
        "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1200",  # Robot hand
        "https://images.unsplash.com/photo-1531746790731-6c087fecd65a?w=1200",  # Robot face
        "https://images.unsplash.com/photo-1546776310-eef45dd6d63c?w=1200",  # Humanoid robot
        "https://images.unsplash.com/photo-1558346490-a72e53ae2d4f?w=1200",  # Industrial robot
    ],
    # Data & Analytics
    "data": [
        "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200",  # Data dashboard
        "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=1200",  # Analytics screen
        "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200",  # Data visualization
        "https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=1200",  # Charts display
    ],
    # Technology & Future
    "tech": [
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1200",  # Matrix code
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1200",  # Cyber security
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200",  # Digital earth
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200",  # Circuit board
    ],
    # Machine Learning & Code
    "ml": [
        "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=1200",  # Code screen
        "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=1200",  # Python code
        "https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=1200",  # Code dark
        "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=1200",  # Programming
    ],
    # ChatGPT & LLM
    "llm": [
        "https://images.unsplash.com/photo-1684369176170-463e84248b70?w=1200",  # ChatGPT style
        "https://images.unsplash.com/photo-1675271591211-930246f80c5c?w=1200",  # AI chat
        "https://images.unsplash.com/photo-1697577418970-95d99b5a55cf?w=1200",  # AI assistant
        "https://images.unsplash.com/photo-1699311080149-76fde4b97815?w=1200",  # Language model
    ],
    # Abstract & Creative
    "abstract": [
        "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=1200",  # Abstract blue
        "https://images.unsplash.com/photo-1614850523459-c2f4c699c52e?w=1200",  # Gradient abstract
        "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1200",  # 3D abstract
        "https://images.unsplash.com/photo-1634017839464-5c339bbe3c35?w=1200",  # Neon abstract
    ],
    # Cloud & Infrastructure
    "cloud": [
        "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=1200",  # Server room
        "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1200",  # Data center
        "https://images.unsplash.com/photo-1484557052118-f32bd25b45b5?w=1200",  # Cloud computing
        "https://images.unsplash.com/photo-1667372393119-3d4c48d07fc9?w=1200",  # Modern datacenter
    ],
}

# Keywords to category mapping for smart cover selection
CATEGORY_KEYWORDS = {
    "neural_network": ["神经网络", "neural", "深度学习", "deep learning", "transformer", "attention"],
    "robot": ["机器人", "robot", "自动化", "automation", "humanoid", "波士顿动力"],
    "data": ["数据", "data", "分析", "analytics", "可视化", "visualization", "统计"],
    "tech": ["安全", "security", "区块链", "blockchain", "元宇宙", "metaverse", "量子"],
    "ml": ["机器学习", "machine learning", "训练", "training", "模型", "model", "算法"],
    "llm": ["ChatGPT", "GPT", "语言模型", "LLM", "对话", "Claude", "Gemini", "OpenAI", "Anthropic"],
    "abstract": ["AGI", "未来", "future", "创意", "creative", "艺术", "art"],
    "cloud": ["云", "cloud", "服务器", "server", "基础设施", "infrastructure", "GPU"],
}


def get_all_images() -> List[str]:
    """Get a flat list of all cover images"""
    all_images = []
    for images in AI_COVER_IMAGES.values():
        all_images.extend(images)
    return all_images


def get_random_cover() -> str:
    """Get a random cover image from the entire collection"""
    all_images = get_all_images()
    return random.choice(all_images)


def get_cover_by_category(category: str) -> str:
    """Get a random cover image from a specific category"""
    if category in AI_COVER_IMAGES:
        return random.choice(AI_COVER_IMAGES[category])
    return get_random_cover()


def get_smart_cover(title: str, tags: Optional[List[str]] = None, summary: str = "") -> str:
    """
    Intelligently select a cover image based on article content.

    Args:
        title: Article title
        tags: List of article tags
        summary: Article summary

    Returns:
        URL of a matching cover image
    """
    # Combine all text for matching
    text = f"{title} {summary} {' '.join(tags or [])}".lower()

    # Score each category by keyword matches
    category_scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword.lower() in text)
        if score > 0:
            category_scores[category] = score

    # If we found matching categories, pick from the best matches
    if category_scores:
        # Get top matching categories
        max_score = max(category_scores.values())
        top_categories = [cat for cat, score in category_scores.items() if score == max_score]

        # Randomly select from top category's images
        selected_category = random.choice(top_categories)
        return random.choice(AI_COVER_IMAGES[selected_category])

    # No keyword matches, return random cover
    return get_random_cover()


if __name__ == "__main__":
    # Test the module
    print("Total images available:", len(get_all_images()))
    print("\nRandom cover:", get_random_cover())
    print("\nSmart cover for 'ChatGPT新功能发布':",
          get_smart_cover("ChatGPT新功能发布", ["AI", "OpenAI"]))
    print("\nSmart cover for '机器人技术突破':",
          get_smart_cover("机器人技术突破", ["机器人", "自动化"]))
    print("\nSmart cover for '深度学习优化':",
          get_smart_cover("深度学习优化", ["神经网络", "训练"]))
