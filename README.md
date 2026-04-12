<div align="center">

# NewsBot 📰

[English](#english) | [中文](#chinese)

</div>

---

## Chinese

一个自动抓取、翻译并推送最新学术论文的机器人。

### 特性

- 🤖 **自动抓取**：从 arXiv 等学术源自动获取最新论文
- 🌐 **智能翻译**：使用 LLM 将论文标题和摘要翻译为中文
- 📤 **多渠道推送**：支持 Telegram、Server酱、本地文件保存
- 🚫 **去重推送**：基于 SQLite 缓存，避免重复发送
- ⚙️ **灵活配置**：通过 YAML 配置文件自定义订阅和推送渠道
- 🔧 **多线程支持**：可配置线程数提高处理效率

### 支持的推送渠道

| 渠道           | 说明                     |
| -------------- | ------------------------ |
| `telegram_bot` | 推送到 Telegram 机器人   |
| `server_chan`  | 推送到 Server酱          |
| `save_to_file` | 保存为本地 Markdown 文件 |

### 快速开始

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置

备份示例配置文件后直接编辑：

```bash
cp configs.yaml configs.yaml.example
# 然后直接编辑 configs.yaml
```

配置项说明：

```yaml
# 线程数（可选）
thread_num: 1

# LLM 配置
llm:
  model: "gemma4:e4b"           # 模型名称
  api_base: "http://localhost:11434/v1"  # API 地址
  api_key: "ollama"              # API 密钥

# 订阅源
subscriptions:
  - name: "arxiv.cs.AI"          # 订阅名称
    url: "http://export.arxiv.org/api/query?search_query=cat:cs.AI&max_results=10"
    max_results: 10              # 每次获取论文数
    interval: 30                 # 检查间隔（分钟）

# 推送渠道
senders:
  - name: "telegram_bot"          # Telegram 推送
  - name: "save_to_file"         # 本地文件保存
    path: "outputs"
```

#### 3. 环境变量（可选）

```bash
# openai
export OPENAI_DEFAULT_MODEL="your_model_name"
export OPENAI_BASE_URL="your_api_base"
export OPENAI_API_KEY="your_api_key"

# Telegram Bot
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# Server酱
export SERVERCHAN_SENDKEY="your_sendkey"
```

#### 4. 运行

```bash
python src/main.py
```

### 项目结构

```
newsbot/
├── src/
│   ├── main.py       # 主程序入口
│   ├── configs.py    # 配置加载
│   ├── fetcher.py    # 论文抓取
│   ├── llm.py        # LLM 客户端
│   ├── senders.py    # 推送渠道
│   ├── cache.py      # 缓存管理
│   ├── paper.py      # 论文数据模型
│   └── prompts.py    # LLM 提示词
├── config.yaml       # 配置文件
├── .env              # 环境变量
├── caches/           # 缓存目录
├── logs/             # 日志目录
└── outputs/          # 输出目录
```

### 许可证

MIT License

---

## English

An automated bot that fetches, translates, and delivers the latest academic papers.

### Features

- 🤖 **Automatic Fetching**: Retrieves latest papers from arXiv and other academic sources
- 🌐 **Smart Translation**: Translates paper titles and abstracts using LLM
- 📤 **Multi-Channel Delivery**: Supports Telegram, ServerChan, and local file export
- 🚫 **Deduplication**: SQLite-based caching prevents duplicate notifications
- ⚙️ **Flexible Configuration**: Customize subscriptions and delivery channels via YAML
- 🔧 **Multi-threading Support**: Configurable thread count for improved efficiency

### Supported Delivery Channels

| Channel        | Description                 |
| -------------- | --------------------------- |
| `telegram_bot` | Send via Telegram Bot       |
| `server_chan`  | Send via ServerChan         |
| `save_to_file` | Save as local Markdown file |

### Quick Start

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Configuration

Backup the example config file and edit directly:

```bash
cp configs.yaml configs.yaml.example
# Then edit configs.yaml directly
```

Configuration options:

```yaml
# Thread count (optional)
thread_num: 1

# LLM configuration
llm:
  model: "gemma4:e4b"
  api_base: "http://localhost:11434/v1"
  api_key: "ollama"

# Subscriptions
subscriptions:
  - name: "arxiv.cs.AI"
    url: "http://export.arxiv.org/api/query?search_query=cat:cs.AI&max_results=10"
    max_results: 10              # Papers per fetch
    interval: 30                 # Check interval (minutes)

# Delivery channels
senders:
  - name: "telegram_bot"         # Telegram delivery
  - name: "save_to_file"         # Local file export
    path: "outputs"
```

#### 3. Environment Variables (Optional)

```bash
# openai
export OPENAI_DEFAULT_MODEL="your_model_name"
export OPENAI_BASE_URL="your_api_base"
export OPENAI_API_KEY="your_api_key"

# Telegram Bot
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# ServerChan
export SERVERCHAN_SENDKEY="your_sendkey"
```

#### 4. Run

```bash
python src/main.py
```

### Project Structure

```
newsbot/
├── src/
│   ├── main.py       # Main entry point
│   ├── configs.py    # Configuration loader
│   ├── fetcher.py    # Paper fetcher
│   ├── llm.py        # LLM client
│   ├── senders.py    # Delivery channels
│   ├── cache.py      # Cache manager
│   ├── paper.py      # Paper data model
│   └── prompts.py    # LLM prompts
├── config.yaml       # Configuration file
├── .env              # Environment variables
├── caches/           # Cache directory
├── logs/             # Log directory
└── outputs/          # Output directory
```

### License

MIT License
