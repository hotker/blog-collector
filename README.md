# Blog Collector

AI文章自动采集系统 - 每天定时采集全球优秀AI资讯，通过Gemini AI改写后自动发布到Hexo博客。

## 功能特点

- 多源采集：RSS订阅、Reddit API、网站爬虫
- AI改写：使用Gemini Pro进行内容二次创作
- 自动发布：通过GitHub API推送到hexo-blog仓库
- 防重复：记录已发布文章，避免重复采集
- 定时运行：GitHub Actions每天北京时间8:00自动执行

## 项目结构

```
blog-collector/
├── .github/workflows/
│   └── collect.yml       # GitHub Actions定时任务
├── src/
│   ├── collector.py      # 采集器模块
│   ├── rewriter.py       # AI改写模块
│   └── publisher.py      # 发布模块
├── state/
│   └── published.json    # 已发布文章记录
├── sources.yaml          # 数据源配置
├── config.yaml           # 全局配置
├── main.py               # 入口文件
└── requirements.txt      # Python依赖
```

## 配置

### 1. GitHub Secrets

在仓库 Settings → Secrets and variables → Actions 中添加：

- `GEMINI_API_KEY`: Gemini API密钥
- `BLOG_PUSH_TOKEN`: GitHub Personal Access Token（需要repo权限）

### 2. 数据源配置

编辑 `sources.yaml` 添加或修改数据源。

### 3. 全局配置

编辑 `config.yaml` 调整每日发布数量等参数。

## 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export GEMINI_API_KEY="your-api-key"
export GITHUB_TOKEN="your-github-token"

# 运行
python main.py
```

## 手动触发

在GitHub仓库的Actions页面，选择"Auto Collect & Publish"工作流，点击"Run workflow"。
