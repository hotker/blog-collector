"""
Collector module - Fetches articles from various sources (RSS, API, Web scraping)
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Optional
import yaml
import json
from pathlib import Path


class Article:
    """Represents a collected article"""

    def __init__(
        self,
        title: str,
        content: str,
        url: str,
        source_name: str,
        lang: str = "en",
        published_at: Optional[datetime] = None
    ):
        self.title = title
        self.content = content
        self.url = url
        self.source_name = source_name
        self.lang = lang
        self.published_at = published_at or datetime.now()

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "source_name": self.source_name,
            "lang": self.lang,
            "published_at": self.published_at.isoformat()
        }


class Collector:
    """Main collector class that aggregates articles from multiple sources"""

    def __init__(self, sources_file: str = "sources.yaml", state_file: str = "state/published.json"):
        self.sources_file = Path(sources_file)
        self.state_file = Path(state_file)
        self.sources = self._load_sources()
        self.published = self._load_published()

    def _load_sources(self) -> dict:
        """Load source configuration from YAML file"""
        if self.sources_file.exists():
            with open(self.sources_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def _load_published(self) -> set:
        """Load already published article URLs"""
        if self.state_file.exists():
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {a["source_url"] for a in data.get("articles", [])}
        return set()

    def _is_published(self, url: str) -> bool:
        """Check if an article has already been published"""
        return url in self.published

    def collect_rss(self) -> list[Article]:
        """Collect articles from RSS feeds"""
        articles = []
        rss_sources = self.sources.get("rss", [])

        for source in rss_sources:
            try:
                feed = feedparser.parse(source["url"])
                for entry in feed.entries[:5]:  # Top 5 per source
                    url = entry.get("link", "")
                    if self._is_published(url):
                        continue

                    # Try to get full content
                    content = ""
                    if hasattr(entry, "content"):
                        content = entry.content[0].value
                    elif hasattr(entry, "summary"):
                        content = entry.summary
                    elif hasattr(entry, "description"):
                        content = entry.description

                    # Parse published date
                    published_at = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6])

                    articles.append(Article(
                        title=entry.get("title", "Untitled"),
                        content=self._clean_html(content),
                        url=url,
                        source_name=source["name"],
                        lang=source.get("lang", "en"),
                        published_at=published_at
                    ))
            except Exception as e:
                print(f"Error fetching RSS from {source['name']}: {e}")

        return articles

    def collect_reddit(self) -> list[Article]:
        """Collect articles from Reddit API"""
        articles = []
        api_sources = self.sources.get("api", [])

        for source in api_sources:
            if source.get("type") != "reddit":
                continue

            try:
                subreddit = source["subreddit"]
                sort = source.get("sort", "hot")
                limit = source.get("limit", 10)

                url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={limit}"
                headers = {"User-Agent": "BlogCollector/1.0"}

                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()

                for post in data.get("data", {}).get("children", []):
                    post_data = post.get("data", {})
                    post_url = f"https://reddit.com{post_data.get('permalink', '')}"

                    if self._is_published(post_url):
                        continue

                    # Skip if it's just a link post with no content
                    selftext = post_data.get("selftext", "")
                    if not selftext and post_data.get("is_self", False):
                        continue

                    articles.append(Article(
                        title=post_data.get("title", "Untitled"),
                        content=selftext or f"Link: {post_data.get('url', '')}",
                        url=post_url,
                        source_name=f"Reddit r/{subreddit}",
                        lang="en",
                        published_at=datetime.fromtimestamp(post_data.get("created_utc", 0))
                    ))
            except Exception as e:
                print(f"Error fetching Reddit from r/{source.get('subreddit', 'unknown')}: {e}")

        return articles

    def collect_websites(self) -> list[Article]:
        """Collect articles from websites via scraping"""
        articles = []
        website_sources = self.sources.get("websites", [])

        for source in website_sources:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                }
                response = requests.get(source["url"], headers=headers, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                selector = source.get("selector", "article")

                for article_elem in soup.select(selector)[:5]:
                    # Try to find title and link
                    title_elem = article_elem.select_one("h1, h2, h3, .title, a")
                    link_elem = article_elem.select_one("a[href]")

                    if not title_elem or not link_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    href = link_elem.get("href", "")

                    # Make URL absolute
                    if href.startswith("/"):
                        from urllib.parse import urljoin
                        href = urljoin(source["url"], href)

                    if self._is_published(href):
                        continue

                    # Fetch full article content
                    content = self._fetch_article_content(href, headers)

                    articles.append(Article(
                        title=title,
                        content=content,
                        url=href,
                        source_name=source["name"],
                        lang=source.get("lang", "zh")
                    ))
            except Exception as e:
                print(f"Error scraping {source['name']}: {e}")

        return articles

    def _fetch_article_content(self, url: str, headers: dict) -> str:
        """Fetch and extract main content from an article URL"""
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Try common content selectors
            content_selectors = [
                "article", ".article-content", ".post-content",
                ".entry-content", ".content", "main"
            ]

            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    return self._clean_html(str(content_elem))

            # Fallback: get body text
            body = soup.find("body")
            if body:
                return self._clean_html(str(body))[:5000]

            return ""
        except Exception as e:
            print(f"Error fetching article content from {url}: {e}")
            return ""

    def _clean_html(self, html: str) -> str:
        """Remove HTML tags and clean up text"""
        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
            element.decompose()

        text = soup.get_text(separator="\n")

        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines()]
        text = "\n".join(line for line in lines if line)

        return text

    def collect_all(self, max_articles: int = 5) -> list[Article]:
        """Collect articles from all sources and return top candidates"""
        all_articles = []

        # Collect from all source types
        all_articles.extend(self.collect_rss())
        all_articles.extend(self.collect_reddit())
        all_articles.extend(self.collect_websites())

        # Filter: only recent articles (last 3 days)
        cutoff = datetime.now() - timedelta(days=3)
        recent_articles = [
            a for a in all_articles
            if a.published_at and a.published_at > cutoff
        ]

        # Sort by recency
        recent_articles.sort(key=lambda a: a.published_at, reverse=True)

        # Return top candidates
        return recent_articles[:max_articles]


if __name__ == "__main__":
    collector = Collector()
    articles = collector.collect_all()
    for article in articles:
        print(f"- {article.title} ({article.source_name})")
