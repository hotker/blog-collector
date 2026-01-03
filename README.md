# Blog Collector

AI文章自动采集系统 - 每天定时采集全球优秀AI资讯，通过AI改写后自动发布到Hexo博客。

## 功能特点

- **多源采集**：RSS订阅、网站爬虫，覆盖全球主流AI媒体
- **双AI引擎**：Gemini（主）+ Groq（备），自动切换，保障稳定性
- **智能改写**：AI二次创作，生成原创中文内容
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
          │ 1. 采集内容
          │ 2. AI改写（Gemini → Groq）
          │ 3. 生成md文件
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
│   ├── collector.py      # 采集器模块（RSS/爬虫）
│   ├── rewriter.py       # AI改写模块（Gemini + Groq）
│   └── publisher.py      # 发布模块（GitHub API）
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

| Secret 名称 | 说明 | 获取方式 |
|------------|------|---------|
| `GEMINI_API_KEY` | Gemini API密钥（主AI） | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `GROQ_API_KEY` | Groq API密钥（备用AI） | [Groq Console](https://console.groq.com/keys) |
| `BLOG_PUSH_TOKEN` | GitHub Personal Access Token | [GitHub Settings](https://github.com/settings/tokens) |

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

```yaml
# RSS 订阅源
rss:
  - name: "OpenAI Blog"           # 源名称（用于标识）
    url: "https://openai.com/blog/rss.xml"  # RSS地址
    lang: "en"                    # 语言（en/zh）

  - name: "Hacker News AI"
    url: "https://hnrss.org/newest?q=AI+OR+LLM+OR+GPT"
    lang: "en"

# 网站爬虫（谨慎使用）
websites:
  - name: "机器之心"
    url: "https://www.jiqizhixin.com/"
    selector: ".article-item"     # CSS选择器
    lang: "zh"
```

#### 推荐 RSS 源

| 名称 | RSS 地址 | 说明 |
|-----|---------|------|
| OpenAI Blog | `https://openai.com/blog/rss.xml` | OpenAI官方博客 |
| Google AI Blog | `https://blog.google/technology/ai/rss/` | Google AI博客 |
| Anthropic | `https://www.anthropic.com/rss.xml` | Claude官方博客 |
| Hacker News AI | `https://hnrss.org/newest?q=AI+OR+LLM` | HN AI话题 |
| The Verge AI | `https://www.theverge.com/rss/ai-artificial-intelligence/index.xml` | The Verge AI |
| TechCrunch AI | `https://techcrunch.com/category/artificial-intelligence/feed/` | TechCrunch AI |
| MIT Tech Review | `https://www.technologyreview.com/topic/artificial-intelligence/feed` | MIT科技评论 |

## AI 引擎说明

### 双引擎自动切换

```
请求 → Gemini API
         │
         ├─ 成功 → 返回结果
         │
         └─ 失败（429配额用尽）
                │
                ▼
            Groq API
                │
                ├─ 成功 → 返回结果
                │
                └─ 失败 → 跳过该文章
```

### 使用的模型

| 引擎 | 模型 | 说明 |
|-----|------|------|
| Gemini | `gemini-2.0-flash` | 主引擎，快速响应 |
| Groq | `llama-3.3-70b-versatile` | 备用引擎，免费额度高 |

## 本地开发

### 安装依赖

```bash
pip install -r requirements.txt
```

### 设置环境变量

```bash
export GEMINI_API_KEY="your-gemini-api-key"
export GROQ_API_KEY="your-groq-api-key"
export GITHUB_TOKEN="your-github-token"
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
    - cron: '0 12 * * *'  # UTC 12:00 = 北京 20:00（可添加多个）
```

### 手动触发

1. 打开仓库 **Actions** 页面
2. 选择 **Auto Collect & Publish**
3. 点击 **Run workflow**

## 常见问题

### Q: Gemini API 报 429 错误？

A: 免费版配额用尽，会自动切换到 Groq。等待第二天配额重置，或升级付费计划。

### Q: 文章没有发布到 hexo-blog？

A: 检查以下几点：
1. `BLOG_PUSH_TOKEN` 是否有 `repo` 权限
2. `config.yaml` 中的 `target_repo` 是否正确
3. 查看 Actions 日志中的错误信息

### Q: 如何添加新的数据源？

A: 编辑 `sources.yaml`，按格式添加 RSS 或网站源，然后提交推送。

### Q: 如何修改文章生成格式？

A: 编辑 `src/rewriter.py` 中的 `REWRITE_PROMPT` 和 `format_hexo_post` 方法。

## License

MIT
