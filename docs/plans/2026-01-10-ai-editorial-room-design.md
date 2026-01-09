# AI Editorial Room Design Document

## 1. Overview
Transform the simple "rewrite" logic into a multi-persona, depth-oriented AI editorial system. The goal is to produce high-quality, distinctive content by matching articles to the most suitable "Persona" (Philosopher, Geek, or Observer) and enhancing them with critical analysis.

## 2. Core Concepts

### 2.1 The Personas
We will define three distinct editorial voices:

*   **The Philosopher (A)**
    *   **Focus**: Ethics, societal impact, long-term history, human-AI relationship.
    *   **Tone**: Profound, reflective, elegant, slightly academic but accessible.
    *   **Triggers**: AI safety, policy, regulation, "future of work", art/culture.
    *   **Style Ref**: *The Atlantic*, *New Yorker*.

*   **The Geek (B)**
    *   **Focus**: Implementation details, code, benchmarks, tools, libraries, performance.
    *   **Tone**: Direct, technical, practical, rigorous, code-heavy.
    *   **Triggers**: GitHub repos, release notes, benchmarks, new frameworks, tutorials.
    *   **Style Ref**: *Hacker News*, *Ars Technica*, *Jeff Dean*.

*   **The Observer (C)**
    *   **Focus**: Business strategy, market dynamics, competitive analysis, money.
    *   **Tone**: Sharp, analytical, opinionated, "follow the money".
    *   **Triggers**: Funding news, M&A, executive changes, quarterly earnings, product launches.
    *   **Style Ref**: *Stratechery (Ben Thompson)*, *TechCrunch*.

### 2.2 The Pipeline
1.  **Ingest**: Receive raw article (title + content).
2.  **Triage (The Editor)**: AI analyzes the content to determine the best-fit Persona (A, B, or C).
3.  **Critique (The Analyst)**: AI generates 3-5 critical questions or angles based on the chosen Persona's perspective.
4.  **Synthesis (The Writer)**: AI rewrites the article adopting the Persona, weaving in the critical angles.

## 3. Architecture Changes

### 3.1 New File: `src/personas.py`
This module will house the prompt definitions and persona logic.

```python
PERSONAS = {
    "philosopher": {
        "name": "The Philosopher",
        "description": "Deep thinker on ethics and society",
        "system_prompt": "You are a tech philosopher...",
        "triggers": ["ethics", "society", "policy", "future"]
    },
    "geek": { ... },
    "observer": { ... }
}
```

### 3.2 Modified: `src/rewriter.py`
The `Rewriter` class will be upgraded to `EditorialRoom`.

*   `rewrite()` method becomes the orchestrator.
*   New method: `select_persona(title, content) -> persona_id`
*   New method: `generate_critique(content, persona_id) -> critique_text`
*   Updated method: `_call_api()` will need to handle variable system prompts.

### 3.3 Configuration
Add persona settings to `config.yaml`:

```yaml
editorial:
  default_persona: "geek"
  enable_auto_triage: true
  personas:
    philosopher: true
    geek: true
    observer: true
```

## 4. Implementation Steps
1.  **Create `src/personas.py`**: Define the detailed prompts for A/B/C.
2.  **Refactor `src/rewriter.py`**: Implement Triage -> Critique -> Write flow.
3.  **Update `config.yaml`**: Add configuration support.
4.  **Test**: Run manual tests with different article types to verify persona switching.

## 5. Success Metrics
*   **Distinctiveness**: A "Geek" rewrite of a funding news should look completely different from an "Observer" rewrite of the same news.
*   **Depth**: Articles should contain at least 2 novel insights not present in the source text (generated via the Critique step).
