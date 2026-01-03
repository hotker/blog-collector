"""
Publisher module - Pushes generated articles to hexo-blog repository via GitHub API
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from github import Github
from slugify import slugify


class Publisher:
    """Publishes articles to hexo-blog repository via GitHub API"""

    def __init__(
        self,
        github_token: Optional[str] = None,
        target_repo: str = "hotker/hexo-blog",
        state_file: str = "state/published.json"
    ):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN is required")

        self.target_repo = target_repo
        self.state_file = Path(state_file)
        self.github = Github(self.github_token)
        self.repo = self.github.get_repo(target_repo)

    def publish(
        self,
        title: str,
        content: str,
        source_url: str,
        branch: str = "main"
    ) -> Optional[str]:
        """
        Publish a markdown file to the hexo-blog repository

        Args:
            title: Article title (used for filename)
            content: Full markdown content including front matter
            source_url: Original article URL (for state tracking)
            branch: Target branch

        Returns:
            Path of created file, or None if failed
        """
        try:
            # Generate filename
            date_prefix = datetime.now().strftime("%Y-%m-%d")
            slug = slugify(title, lowercase=True, max_length=50)
            filename = f"{date_prefix}-{slug}.md"
            file_path = f"source/_posts/{filename}"

            # Check if file already exists
            try:
                self.repo.get_contents(file_path, ref=branch)
                print(f"File already exists: {file_path}")
                return None
            except Exception:
                pass  # File doesn't exist, continue

            # Create file via GitHub API
            commit_message = f"Auto: 新增文章 - {title}"

            self.repo.create_file(
                path=file_path,
                message=commit_message,
                content=content,
                branch=branch
            )

            print(f"Published: {file_path}")

            # Update state
            self._update_state(source_url, title, file_path)

            return file_path

        except Exception as e:
            print(f"Error publishing article: {e}")
            return None

    def _update_state(self, source_url: str, title: str, hexo_path: str):
        """Update the published articles state file"""
        state = {"articles": []}

        if self.state_file.exists():
            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)

        state["articles"].append({
            "source_url": source_url,
            "title": title,
            "published_at": datetime.now().isoformat(),
            "hexo_path": hexo_path
        })

        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def get_published_count(self) -> int:
        """Get count of published articles"""
        if self.state_file.exists():
            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
                return len(state.get("articles", []))
        return 0


if __name__ == "__main__":
    # Test
    publisher = Publisher()
    print(f"Published articles: {publisher.get_published_count()}")
