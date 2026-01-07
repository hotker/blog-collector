# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- **Install dependencies**: `pip install -r requirements.txt`
- **Run application**: `python main.py`
- **Run single module**: `python src/<module_name>.py` (e.g., `python src/collector.py`) - Each module has a `__main__` block for isolated testing.
- **Check environment**: Ensure `OPENAI_API_KEY`, `GITHUB_TOKEN`, and `GEMINI_API_KEY` are set.

## Environment Variables

Required for local development and GitHub Actions:

```bash
export OPENAI_API_KEY="your-newapi-key"      # Required - NewAPI key (not official OpenAI)
export OPENAI_API_BASE="https://api.hotker.com/v1"  # Optional - Defaults to NewAPI
export OPENAI_MODEL="gpt-4o-mini"            # Optional - Default model
export GITHUB_TOKEN="your-github-token"      # Required - For publishing to hexo-blog repo
export GEMINI_API_KEY="your-gemini-key"      # Required - For AI cover image generation
```

## Architecture

Automated AI content pipeline: Collect -> Rewrite -> Publish.

- **Main Orchestrator** (`main.py`): Coordinates the three-step flow using classes from `src/`.
- **Collector** (`src/collector.py`):
  - Parses `sources.yaml` for RSS feeds (`feedparser`) and HTML scrapers (`BeautifulSoup`).
  - Checks `state/published.json` to skip already processed URLs.
- **Rewriter** (`src/rewriter.py`):
  - Uses OpenAI-compatible API (NewAPI) to translate/rewrite content.
  - Formats output as Hexo Markdown with front-matter.
- **Cover Manager** (`src/covers.py`):
  - Uses Gemini AI to analyze article content and extract keywords.
  - Generates cover images via Pollinations.ai (free, no API key) with Gemini as fallback.
  - Uploads images to custom image hosting service.
- **Publisher** (`src/publisher.py`):
  - Uses `PyGithub` to push generated Markdown files to a separate repository (e.g., `hotker/hexo-blog`).
  - Updates `state/published.json` after successful publication.

## Configuration

- `config.yaml`: Global settings like `max_articles_per_run` and `target_repo`.
- `sources.yaml`: List of RSS and Web sources with CSS selectors for scraping.

## Testing & Development

- No formal test suite (pytest/unittest).
- Development cycle: Modify `src/*.py`, run the module directly to verify its specific logic.
- Verify `state/published.json` updates to ensure no duplicate processing.

## Style Guidelines

- **Typing**: Use standard Python 3.9+ type hints.
- **Docs**: Use Google-style docstrings for classes and methods.
- **State**: Never manually edit `state/published.json` unless fixing corruption; it is managed by the code.
