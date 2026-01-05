# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- **Install dependencies**: `pip install -r requirements.txt`
- **Run application**: `python main.py`
- **Run single module**: `python src/<module_name>.py` (e.g., `python src/collector.py`) - Modules have `__main__` blocks for isolated testing.

## Architecture

This project is an AI-powered automated content pipeline (Python).

- **`main.py`**: Orchestrates the flow: Collection -> Rewriting -> Publishing.
- **`src/collector.py`**: Fetches content from RSS feeds (`feedparser`) and scrapes websites (`BeautifulSoup`). Configured in `sources.yaml`.
- **`src/rewriter.py`**: Rewrites content using an OpenAI-compatible API (self-hosted NewAPI). Formats as Hexo-compatible Markdown.
- **`src/publisher.py`**: Pushes new articles to a target Hexo blog repository using `PyGithub`.
- **`src/covers.py`**: Selects cover images based on keywords.
- **`state/published.json`**: Tracks processed URLs to prevent duplicates.
- **`config.yaml`**: Main settings (limits, target repo, etc.).

## Testing

- No formal test runner (e.g., pytest) is configured.
- Test manually by running individual modules: `python src/collector.py`, etc.
- GitHub Actions workflow (`.github/workflows/collect.yml`) runs the pipeline daily.

## Style Guidelines

- **Language**: Python 3.x
- **Typing**: Use standard Python type hints.
- **Formatting**: Follow standard PEP 8 conventions. No automated linters are currently enforced.
- **Configuration**: Prefer `config.yaml` for settings and `sources.yaml` for data sources over hardcoding.
