# Blog Collector

AI文章自动采集系统 - 每天定时采集全球优秀AI资讯，通过AI改写后自动发布到Hexo博客。

## 功能特点

- **多源采集**：RSS订阅 + 网站爬虫，覆盖全球主流AI媒体（8个RSS源 + 2个中文站）
- **灵活AI引擎**：OpenAI兼容API，支持自托管/第三方服务
- **智能改写**：AI二次创作，将英文资讯转化为原创中文内容
- **智能封面**：Gemini AI 实时生成，每篇文章专属封面
- **自动发布**：通过GitHub API推送到hexo-blog仓库
- **防重复**：记录已发布文章URL，避免重复采集
- **定时运行**：GitHub Actions每天北京时间8:00自动执行

## 系统架构

```
┌─────────────────────┐
│   blog-collector    │  ← 本仓库
│  GitHub Actions     │
│  每天定时运行        │
└─────────┬───────────┘
          │ 1. 采集内容（RSS/爬虫）
          │ 2. AI改写（OpenAI兼容API）
          │ 3. 生成Hexo Markdown
          │ 4. GitHub API推送
          ▼
┌─────────────────────┐
│     hexo-blog       │  ← 博客源码仓库
│  source/_posts/     │
└─────────┬───────────┘
          │ 5. 触发构建
          │ 6. 部署
          ▼
┌─────────────────────┐
│  hotker.github.io   │  ← 静态站点
└─────────────────────┘
```

## 项目结构

```
blog-collector/
├── .github/workflows/
│   └── collect.yml       # GitHub Actions定时任务
├── src/
│   ├── __init__.py
│   ├── collector.py      # 采集器（RSS解析 + 网站爬虫）
│   ├── rewriter.py       # AI改写（OpenAI兼容API）
│   ├── covers.py         # 智能封面（Gemini AI 生成）
│   └── publisher.py      # GitHub API发布
├── state/
│   └── published.json    # 已发布文章记录（防重复）
├── sources.yaml          # 数据源配置
├── config.yaml           # 全局配置
├── main.py               # 入口文件
├── requirements.txt      # Python依赖
└── README.md
```

## 快速开始

### 1. Fork 本仓库

### 2. 配置 GitHub Secrets

在仓库 **Settings → Secrets and variables → Actions** 中添加：

| Secret 名称 | 说明 | 必需 |
|------------|------|------|
| `OPENAI_API_KEY` | NewAPI 密钥 | 是 |
| `OPENAI_MODEL` | 使用的模型（默认：gpt-4o-mini） | 否 |
| `BLOG_PUSH_TOKEN` | GitHub Personal Access Token | 是 |
| `GEMINI_API_KEY` | Gemini API 密钥（封面生成） | 是 |

> 默认 API 地址为 NewAPI 自托管服务地址，可在 workflow 中修改。

#### 获取 GitHub Personal Access Token

1. 访问 https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**
3. 勾选 `repo` 权限（完整仓库访问）
4. 生成并复制 Token

### 3. 修改目标仓库

编辑 `config.yaml`，修改 `target_repo` 为你的博客仓库：

```yaml
target_repo: "your-username/your-hexo-blog"
```

### 4. 配置数据源

编辑 `sources.yaml` 添加或修改采集源。

### 5. 运行测试

在 **Actions** 页面手动触发 workflow 测试。

## 配置说明

### config.yaml - 全局配置

```yaml
# 每次运行最多发布的文章数
max_articles_per_run: 2

# 目标博客仓库（用户名/仓库名）
target_repo: "hotker/hexo-blog"

# 默认封面图
default_cover: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200"

# 文章设置
article:
  min_content_length: 200  # 最小内容长度
  max_age_days: 3          # 最大文章年龄（天）
```

### sources.yaml - 数据源配置

#### RSS 订阅源（8个）

| 名称 | RSS 地址 | 语言 |
|-----|---------|------|
| OpenAI Blog | `https://openai.com/blog/rss.xml` | en |
| Google AI Blog | `https://blog.google/technology/ai/rss/` | en |
| Anthropic News | `https://www.anthropic.com/rss.xml` | en |
| Hacker News AI | `https://hnrss.org/newest?q=AI+OR+LLM+OR+GPT+OR+Claude` | en |
| MIT Technology Review AI | `https://www.technologyreview.com/topic/artificial-intelligence/feed` | en |
| The Verge AI | `https://www.theverge.com/rss/ai-artificial-intelligence/index.xml` | en |
| Ars Technica AI | `https://feeds.arstechnica.com/arstechnica/technology-lab` | en |
| TechCrunch AI | `https://techcrunch.com/category/artificial-intelligence/feed/` | en |

#### 网站爬虫（2个）

| 名称 | URL | CSS选择器 |
|-----|-----|----------|
| 机器之心 | `https://www.jiqizhixin.com/` | `.article-item` |
| 量子位 | `https://www.qbitai.com/` | `.post-item` |

## AI 引擎说明

### NewAPI 自托管服务

系统使用 NewAPI 自托管的 OpenAI 兼容 API 接口，不支持官方 API。

**优势**：
- 零成本使用 GPT-4o-mini 等模型
- 更高的可用性和稳定性
- 完全的数据控制

**支持的模型**：
- GPT-4o-mini（默认）
- GPT-4o
- Claude 3.5 Sonnet
- 其他 OpenAI 兼容模型

### 环境变量配置

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `OPENAI_API_KEY` | NewAPI 密钥 | 必需 |
| `OPENAI_API_BASE` | NewAPI 服务地址 | `https://api.hotker.com/v1` |
| `OPENAI_MODEL` | 使用的模型 | `gpt-4o-mini` |
| `GEMINI_API_KEY` | Gemini API 密钥 | 必需 |

> **注意**：本系统仅支持 NewAPI 自托管服务，不支持官方 OpenAI API。

## 本地开发

### 安装依赖

```bash
pip install -r requirements.txt
```

### 设置环境变量

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_BASE="https://api.hotker.com/v1"  # 可选
export OPENAI_MODEL="gpt-4o-mini"  # 可选
export GITHUB_TOKEN="your-github-token"
export GEMINI_API_KEY="your-gemini-key"
```

### 运行

```bash
python main.py
```

### 仅测试采集（不发布）

```python
from src.collector import Collector

collector = Collector()
articles = collector.collect_all()
for a in articles:
    print(f"- {a.title} ({a.source_name})")
```

## 定时任务

默认每天 UTC 00:00（北京时间 08:00）自动运行。

修改定时时间，编辑 `.github/workflows/collect.yml`：

```yaml
on:
  schedule:
    # UTC时间，北京时间需要-8小时
    - cron: '0 0 * * *'   # UTC 00:00 = 北京 08:00
```

### 手动触发

1. 打开仓库 **Actions** 页面
2. 选择 **Auto Collect & Publish**
3. 点击 **Run workflow**

## 智能封面生成

系统使用 Gemini AI 为每篇文章实时生成专属封面图。

### 工作流程

1. **内容分析**：使用 Gemini 分析文章标题、标签和摘要，提取关键词和风格
2. **图片生成**：通过 Gemini Imagen API 生成 16:9 比例的高质量封面图
3. **自动上传**：将生成的图片上传到图床服务并返回 URL

### 支持的风格

| 风格 | 说明 |
|-----|------|
| futuristic tech | 未来科技感 |
| digital art | 数字艺术 |
| minimalist illustration | 极简插画 |
| abstract geometric | 抽象几何 |
| cyberpunk | 赛博朋克 |
| clean modern | 简约现代 |

### 环境配置

封面生成需要配置以下环境变量：

| 环境变量 | 说明 |
|---------|------|
| `GEMINI_API_KEY` | Google AI Studio API 密钥 |
| 自定义图床 | 可在 `src/covers.py` 中修改 `UPLOAD_URL` |

### 本地测试

```bash
python -c "
from src.covers import get_smart_cover
url = get_smart_cover('ChatGPT新功能发布', ['AI', 'OpenAI'], 'OpenAI发布了ChatGPT的新功能')
print(f'Cover URL: {url}')
"

## 常见问题

### Q: API 报 429 错误？

A: API配额用尽或请求频率过高。等待配额重置，或考虑升级计划。

### Q: 文章没有发布到 hexo-blog？

A: 检查以下几点：
1. `BLOG_PUSH_TOKEN` 是否有 `repo` 权限
2. `config.yaml` 中的 `target_repo` 是否正确
3. 查看 Actions 日志中的错误信息

### Q: 如何修改 NewAPI 配置？

A: 编辑 `.github/workflows/collect.yml` 中的环境变量：

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  OPENAI_API_BASE: https://your-newapi-domain.com/v1  # 修改为你的 NewAPI 地址
  OPENAI_MODEL: gpt-4o-mini  # 修改为你要使用的模型
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

> **注意**：本系统仅支持 NewAPI 自托管服务，不支持官方 OpenAI API。

### Q: 如何添加新的数据源？

A: 编辑 `sources.yaml`，按格式添加 RSS 或网站源，然后提交推送。

### Q: 如何修改文章生成格式？

A: 编辑 `src/rewriter.py` 中的 `REWRITE_PROMPT` 和 `format_hexo_post` 方法。

## License

MIT
