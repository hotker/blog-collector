"""
Blog Collector - Main entry point

Collects AI-related articles from various sources, rewrites them using Gemini AI,
and publishes them to the hexo-blog repository.
"""

import os
import yaml
from pathlib import Path
from src.collector import Collector
from src.rewriter import Rewriter
from src.publisher import Publisher


def load_config(config_file: str = "config.yaml") -> dict:
    """Load configuration from YAML file"""
    config_path = Path(config_file)
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def main():
    """Main execution flow"""
    print("=" * 50)
    print("Blog Collector - Starting...")
    print("=" * 50)

    # Load configuration
    config = load_config()
    max_articles = config.get("max_articles_per_run", 2)
    target_repo = config.get("target_repo", "hotker/hexo-blog")

    # Step 1: Collect articles from all sources
    print("\n[1/3] Collecting articles from sources...")
    collector = Collector(
        sources_file="sources.yaml",
        state_file="state/published.json"
    )
    candidates = collector.collect_all(max_articles=5)

    if not candidates:
        print("No new articles found. Exiting.")
        return

    print(f"Found {len(candidates)} candidate articles:")
    for i, article in enumerate(candidates, 1):
        print(f"  {i}. {article.title[:50]}... ({article.source_name})")

    # Step 2: Rewrite articles using Gemini AI
    print("\n[2/3] Rewriting articles with Gemini AI...")
    rewriter = Rewriter()
    rewritten_articles = []

    for article in candidates[:max_articles]:
        print(f"  Rewriting: {article.title[:40]}...")
        result = rewriter.rewrite(
            title=article.title,
            content=article.content,
            source_name=article.source_name,
            source_url=article.url
        )

        if result:
            # Format as Hexo post
            hexo_content = rewriter.format_hexo_post(
                rewritten=result,
                source_url=article.url
            )
            rewritten_articles.append({
                "title": result["title"],
                "content": hexo_content,
                "source_url": article.url
            })
            print(f"    ✓ Success: {result['title']}")
        else:
            print(f"    ✗ Failed to rewrite")

    if not rewritten_articles:
        print("No articles were successfully rewritten. Exiting.")
        return

    # Step 3: Publish to hexo-blog repository
    print("\n[3/3] Publishing to hexo-blog repository...")
    publisher = Publisher(
        target_repo=target_repo,
        state_file="state/published.json"
    )

    published_count = 0
    for article in rewritten_articles:
        result = publisher.publish(
            title=article["title"],
            content=article["content"],
            source_url=article["source_url"]
        )
        if result:
            published_count += 1
            print(f"  ✓ Published: {article['title']}")
        else:
            print(f"  ✗ Failed to publish: {article['title']}")

    # Summary
    print("\n" + "=" * 50)
    print(f"Completed! Published {published_count} article(s).")
    print(f"Total articles in state: {publisher.get_published_count()}")
    print("=" * 50)


if __name__ == "__main__":
    main()
