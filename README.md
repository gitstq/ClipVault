<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Zero_Dependencies-✓-success.svg" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/Cross_Platform-✓-orange.svg" alt="Cross Platform">
  <img src="https://img.shields.io/badge/Tests-34%20Passed-brightgreen.svg" alt="Tests">
</p>

<h1 align="center">📋 ClipVault</h1>

<p align="center">
  <strong>Lightweight Cross-Platform Clipboard Intelligent Management Engine CLI</strong><br>
  轻量级跨平台剪贴板智能管理引擎 CLI
</p>

<p align="center">
  <a href="#-english">English</a> •
  <a href="#-简体中文">简体中文</a> •
  <a href="#-繁體中文">繁體中文</a>
</p>

---

<a id="-english"></a>

## 🎉 About ClipVault

**ClipVault** is a lightweight, zero-dependency clipboard intelligent management engine designed for developers. It runs entirely in your terminal, automatically monitors clipboard changes, smart-categorizes content, and provides powerful search, template, and statistics capabilities.

### 💡 Why ClipVault?

- 🔄 **Tired of losing clipboard history?** System clipboards only keep one item — ClipVault remembers everything.
- 🏷️ **Wasting time finding that code snippet you copied earlier?** Smart categorization + fuzzy search finds it instantly.
- 📋 **Need quick access to frequently used text?** The template system saves your common snippets for one-key reuse.
- 🔒 **Privacy concerns?** Everything stays local — no cloud, no network, no tracking.

### ✨ Key Differentiators

Unlike GUI clipboard managers (like Ditto, CopyQ, or GoPaste), ClipVault is:
- **Terminal-native** — designed for developers who live in the CLI
- **Zero dependencies** — pure Python, no npm/pip install needed
- **Smart categorization** — auto-detects code, links, emails, paths, JSON, SQL, and more
- **Fuzzy search** — find items even with typos or partial matches
- **Template system** — save and instantly paste frequently used content

---

<a id="-english-features"></a>

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📋 **Smart Monitoring** | Auto-detect clipboard changes with configurable polling interval |
| 🏷️ **Auto Categorization** | 16+ content types: text, code (Python/JS/Go/Rust/Java/C/C++/PHP), link, email, phone, path, image, JSON, XML, HTML, SQL, IP, hex, base64, shell command |
| 🔎 **Multi-Mode Search** | Exact, regex, and fuzzy search with relevance scoring |
| 📌 **Pin System** | Pin important items to the top of your list |
| 📝 **Template System** | Save frequently used content as named templates |
| 📊 **Statistics Dashboard** | Usage analytics by category, copy counts, trends |
| 🖥️ **TUI Browser** | Interactive terminal UI with keyboard navigation |
| 💾 **Export/Import** | JSON, CSV, TXT format support for backup and migration |
| 🌍 **Cross-Platform** | Linux (xclip/xsel/wl-clipboard), macOS (pbcopy), Windows (clip) |
| ⚙️ **Configuration** | Persistent settings stored in SQLite |
| 🧪 **34 Unit Tests** | Comprehensive test coverage for all core modules |

---

<a id="-english-quickstart"></a>

## 🚀 Quick Start

### Requirements

- Python 3.8 or higher
- A clipboard tool (most systems have one pre-installed):
  - **Linux**: `xclip` or `xsel` or `wl-clipboard` (Wayland)
  - **macOS**: Built-in `pbcopy`/`pbpaste`
  - **Windows**: Built-in `clip` command

### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/ClipVault.git
cd ClipVault

# Install (optional — you can also run directly from source)
pip install -e .
```

### Usage

```bash
# Start monitoring clipboard
clipvault watch

# List clipboard history (last 20 items)
clipvault list

# List all items in a specific category
clipvault list -c code

# Search with fuzzy matching
clipvault search "python function" --fuzzy

# Copy a stored item back to clipboard
clipvault copy 5

# Pin an important item
clipvault pin 5

# View statistics
clipvault stats

# Launch interactive TUI browser
clipvault tui

# Save current clipboard as a template
clipvault template add my-snippet

# Use a template
clipvault template use my-snippet

# Export history to JSON
clipvault export -f json -o backup.json

# Import history
clipvault import backup.json
```

---

<a id="-english-guide"></a>

## 📖 Detailed Guide

### Clipboard Monitoring

```bash
# Start with default 0.5s interval
clipvault watch

# Custom interval (1 second)
clipvault watch -i 1.0

# Silent mode (no notifications)
clipvault watch --silent
```

### Search Modes

```bash
# Exact substring search
clipvault search "error handling"

# Regex pattern search
clipvault search "def\s+\w+"

# Fuzzy search (tolerates typos)
clipvault search "pythn functon" --fuzzy

# Combine with category filter
clipvault search "api" -c link
```

### TUI Browser

Launch the interactive terminal UI with `clipvault tui`:

| Key | Action |
|-----|--------|
| `↑/↓` or `j/k` | Navigate up/down |
| `Enter` | View item details |
| `y` | Copy selected item |
| `p` | Toggle pin |
| `d` | Delete item |
| `/` | Search mode |
| `f` | Cycle category filter |
| `r` | Refresh list |
| `s` | Show statistics |
| `h` | Help |
| `q` | Quit |

### Template System

Templates let you save frequently used content for instant access:

```bash
# Save current clipboard content as a template
echo "print('Hello, World!')" | clipvault template add hello

# Use a template (copies to clipboard)
clipvault template use hello

# List all templates
clipvault template list

# Delete a template
clipvault template delete hello
```

---

<a id="-english-design"></a>

## 💡 Design Philosophy & Roadmap

### Design Principles

1. **Zero Dependencies** — Pure Python standard library only, no pip install required
2. **Developer-First** — Terminal-native, keyboard-driven workflow
3. **Privacy-First** — All data stored locally in SQLite, never leaves your machine
4. **Smart by Default** — Auto-categorization means zero configuration for most use cases
5. **Extensible** — Plugin-ready architecture for future enhancements

### Architecture

```
ClipVault/
├── core/
│   ├── engine.py        # Main orchestration engine
│   ├── clipboard.py     # Cross-platform clipboard I/O
│   ├── storage.py       # SQLite storage layer
│   ├── categorizer.py   # Smart content classification
│   └── search.py        # Multi-mode search engine
├── ui/
│   └── tui.py           # Terminal User Interface
└── utils/
    └── helpers.py       # Utility functions
```

### Roadmap

- [ ] **v1.1**: Clipboard content encryption (AES-256)
- [ ] **v1.2**: Multi-database backend support
- [ ] **v1.3**: Plugin system for custom categorizers
- [ ] **v1.4**: Remote sync via SFTP/WebDAV
- [ ] **v2.0**: Web dashboard for remote browsing
- [ ] **v2.1**: Share clipboard between machines

---

<a id="-english-deploy"></a>

## 📦 Installation & Deployment

### From Source

```bash
git clone https://github.com/gitstq/ClipVault.git
cd ClipVault
pip install -e .
```

### Run Without Installing

```bash
git clone https://github.com/gitstq/ClipVault.git
cd ClipVault
PYTHONPATH=src python -m clipvault --help
```

### Data Location

All data is stored in `~/.clipvault/`:
- `history.db` — SQLite database with all clipboard history, templates, and config

---

<a id="-english-contributing"></a>

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit with [Conventional Commits](https://www.conventionalcommits.org/)
4. Push to your fork (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

<a id="-english-license"></a>

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<a id="-简体中文"></a>

---

<h2 align="center">📋 ClipVault 简体中文文档</h2>

## 🎉 项目介绍

**ClipVault** 是一款轻量级、零依赖的剪贴板智能管理引擎，专为开发者设计。它完全运行在终端中，自动监控剪贴板变化，智能分类内容，并提供强大的搜索、模板和统计功能。

### 💡 为什么选择 ClipVault？

- 🔄 **厌倦了丢失剪贴板历史？** 系统剪贴板只能保存一条记录——ClipVault 帮你记住所有内容。
- 🏷️ **找不到之前复制的代码片段？** 智能分类 + 模糊搜索，秒级定位。
- 📋 **需要快速访问常用文本？** 模板系统让你一键粘贴常用内容。
- 🔒 **隐私担忧？** 一切数据本地存储——无云端、无网络、无追踪。

### ✨ 差异化亮点

与 GUI 剪贴板管理器（如 Ditto、CopyQ、GoPaste）不同，ClipVault：
- **终端原生** — 为生活在 CLI 中的开发者设计
- **零依赖** — 纯 Python 实现，无需安装任何第三方包
- **智能分类** — 自动识别代码、链接、邮箱、路径、JSON、SQL 等 16+ 种内容类型
- **模糊搜索** — 即使有拼写错误或部分匹配也能找到
- **模板系统** — 保存常用内容，一键粘贴

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 📋 **智能监控** | 自动检测剪贴板变化，支持自定义轮询间隔 |
| 🏷️ **自动分类** | 16+ 种内容类型：文本、代码（Python/JS/Go/Rust/Java/C/C++/PHP）、链接、邮箱、电话、路径、图片、JSON、XML、HTML、SQL、IP、十六进制、Base64、Shell 命令 |
| 🔎 **多模式搜索** | 精确搜索、正则搜索、模糊搜索，带相关性评分 |
| 📌 **置顶系统** | 将重要条目置顶显示 |
| 📝 **模板系统** | 将常用内容保存为命名模板 |
| 📊 **统计仪表盘** | 按类别统计使用情况、复制次数、趋势分析 |
| 🖥️ **TUI 浏览器** | 交互式终端界面，键盘导航 |
| 💾 **导入/导出** | 支持 JSON、CSV、TXT 格式备份和迁移 |
| 🌍 **跨平台** | Linux（xclip/xsel/wl-clipboard）、macOS（pbcopy）、Windows（clip） |
| ⚙️ **配置管理** | SQLite 持久化存储设置 |
| 🧪 **34 个单元测试** | 全核心模块综合测试覆盖 |

---

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- 剪贴板工具（大多数系统已预装）：
  - **Linux**：`xclip` 或 `xsel` 或 `wl-clipboard`（Wayland）
  - **macOS**：内置 `pbcopy`/`pbpaste`
  - **Windows**：内置 `clip` 命令

### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/ClipVault.git
cd ClipVault

# 安装（可选——也可以直接从源码运行）
pip install -e .
```

### 使用

```bash
# 开始监控剪贴板
clipvault watch

# 列出剪贴板历史（最近 20 条）
clipvault list

# 按类别列出
clipvault list -c code

# 模糊搜索
clipvault search "python 函数" --fuzzy

# 将存储的条目复制回剪贴板
clipvault copy 5

# 置顶重要条目
clipvault pin 5

# 查看统计信息
clipvault stats

# 启动交互式 TUI 浏览器
clipvault tui

# 将当前剪贴板保存为模板
clipvault template add 我的代码片段

# 使用模板
clipvault template use 我的代码片段

# 导出历史为 JSON
clipvault export -f json -o backup.json

# 导入历史
clipvault import backup.json
```

---

## 📖 详细使用指南

### 剪贴板监控

```bash
# 默认 0.5 秒间隔
clipvault watch

# 自定义间隔（1 秒）
clipvault watch -i 1.0

# 静默模式（无通知）
clipvault watch --silent
```

### 搜索模式

```bash
# 精确子串搜索
clipvault search "错误处理"

# 正则表达式搜索
clipvault search "def\s+\w+"

# 模糊搜索（容忍拼写错误）
clipvault search "pythn 函数" --fuzzy

# 结合类别过滤
clipvault search "api" -c link
```

### TUI 浏览器

使用 `clipvault tui` 启动交互式终端界面：

| 按键 | 操作 |
|------|------|
| `↑/↓` 或 `j/k` | 上下导航 |
| `Enter` | 查看条目详情 |
| `y` | 复制选中条目 |
| `p` | 切换置顶 |
| `d` | 删除条目 |
| `/` | 搜索模式 |
| `f` | 切换类别过滤 |
| `r` | 刷新列表 |
| `s` | 查看统计 |
| `h` | 帮助 |
| `q` | 退出 |

### 模板系统

模板让你保存常用内容，随时快速访问：

```bash
# 将当前剪贴板内容保存为模板
echo "print('Hello, World!')" | clipvault template add hello

# 使用模板（复制到剪贴板）
clipvault template use hello

# 列出所有模板
clipvault template list

# 删除模板
clipvault template delete hello
```

---

## 💡 设计思路与迭代规划

### 设计原则

1. **零依赖** — 仅使用 Python 标准库，无需 pip install
2. **开发者优先** — 终端原生，键盘驱动的工作流
3. **隐私优先** — 所有数据存储在本地 SQLite，永不离开你的机器
4. **智能默认** — 自动分类意味着大多数场景零配置
5. **可扩展** — 插件就绪的架构，便于未来增强

### 架构

```
ClipVault/
├── core/
│   ├── engine.py        # 主编排引擎
│   ├── clipboard.py     # 跨平台剪贴板 I/O
│   ├── storage.py       # SQLite 存储层
│   ├── categorizer.py   # 智能内容分类
│   └── search.py        # 多模式搜索引擎
├── ui/
│   └── tui.py           # 终端用户界面
└── utils/
    └── helpers.py       # 工具函数
```

### 迭代规划

- [ ] **v1.1**：剪贴板内容加密（AES-256）
- [ ] **v1.2**：多数据库后端支持
- [ ] **v1.3**：自定义分类器插件系统
- [ ] **v1.4**：通过 SFTP/WebDAV 远程同步
- [ ] **v2.0**：Web 仪表盘远程浏览
- [ ] **v2.1**：多机剪贴板共享

---

## 📦 安装与部署

### 从源码安装

```bash
git clone https://github.com/gitstq/ClipVault.git
cd ClipVault
pip install -e .
```

### 免安装运行

```bash
git clone https://github.com/gitstq/ClipVault.git
cd ClipVault
PYTHONPATH=src python -m clipvault --help
```

### 数据存储位置

所有数据存储在 `~/.clipvault/` 目录下：
- `history.db` — SQLite 数据库，包含所有剪贴板历史、模板和配置

---

## 🤝 贡献指南

欢迎贡献！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解指南。

1. Fork 本仓库
2. 创建功能分支（`git checkout -b feature/amazing-feature`）
3. 使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范提交
4. 推送到你的 Fork（`git push origin feature/amazing-feature`）
5. 发起 Pull Request

---

## 📄 开源协议

本项目基于 MIT 协议开源。详见 [LICENSE](LICENSE)。

---

<a id="-繁體中文"></a>

---

<h2 align="center">📋 ClipVault 繁體中文文檔</h2>

## 🎉 專案介紹

**ClipVault** 是一款輕量級、零依賴的剪貼簿智慧管理引擎，專為開發者設計。它完全運行在終端中，自動監控剪貼簿變化，智慧分類內容，並提供強大的搜尋、模板和統計功能。

### 💡 為什麼選擇 ClipVault？

- 🔄 **厭倦了遺失剪貼簿歷史？** 系統剪貼簿只能保存一條記錄——ClipVault 幫你記住所有內容。
- 🏷️ **找不到之前複製的程式碼片段？** 智慧分類 + 模糊搜尋，秒級定位。
- 📋 **需要快速存取常用文字？** 模板系統讓你一鍵貼上常用內容。
- 🔒 **隱私擔憂？** 一切資料本地儲存——無雲端、無網路、無追蹤。

### ✨ 差異化亮點

與 GUI 剪貼簿管理器（如 Ditto、CopyQ、GoPaste）不同，ClipVault：
- **終端原生** — 為生活在 CLI 中的開發者設計
- **零依賴** — 純 Python 實現，無需安裝任何第三方套件
- **智慧分類** — 自動識別程式碼、連結、信箱、路徑、JSON、SQL 等 16+ 種內容類型
- **模糊搜尋** — 即使有拼寫錯誤或部分匹配也能找到
- **模板系統** — 保存常用內容，一鍵貼上

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 📋 **智慧監控** | 自動偵測剪貼簿變化，支援自訂輪詢間隔 |
| 🏷️ **自動分類** | 16+ 種內容類型：文字、程式碼（Python/JS/Go/Rust/Java/C/C++/PHP）、連結、信箱、電話、路徑、圖片、JSON、XML、HTML、SQL、IP、十六進位、Base64、Shell 命令 |
| 🔎 **多模式搜尋** | 精確搜尋、正則搜尋、模糊搜尋，帶相關性評分 |
| 📌 **置頂系統** | 將重要條目置頂顯示 |
| 📝 **模板系統** | 將常用內容保存為命名模板 |
| 📊 **統計儀表板** | 按類別統計使用情況、複製次數、趨勢分析 |
| 🖥️ **TUI 瀏覽器** | 互動式終端介面，鍵盤導航 |
| 💾 **匯入/匯出** | 支援 JSON、CSV、TXT 格式備份和遷移 |
| 🌍 **跨平台** | Linux（xclip/xsel/wl-clipboard）、macOS（pbcopy）、Windows（clip） |
| ⚙️ **設定管理** | SQLite 持久化儲存設定 |
| 🧪 **34 個單元測試** | 全核心模組綜合測試覆蓋 |

---

## 🚀 快速開始

### 環境要求

- Python 3.8 或更高版本
- 剪貼簿工具（大多數系統已預裝）：
  - **Linux**：`xclip` 或 `xsel` 或 `wl-clipboard`（Wayland）
  - **macOS**：內建 `pbcopy`/`pbpaste`
  - **Windows**：內建 `clip` 命令

### 安裝

```bash
# 克隆倉庫
git clone https://github.com/gitstq/ClipVault.git
cd ClipVault

# 安裝（可選——也可以直接從原始碼運行）
pip install -e .
```

### 使用

```bash
# 開始監控剪貼簿
clipvault watch

# 列出剪貼簿歷史（最近 20 條）
clipvault list

# 按類別列出
clipvault list -c code

# 模糊搜尋
clipvault search "python 函數" --fuzzy

# 將儲存的條目複製回剪貼簿
clipvault copy 5

# 置頂重要條目
clipvault pin 5

# 查看統計資訊
clipvault stats

# 啟動互動式 TUI 瀏覽器
clipvault tui

# 將當前剪貼簿保存為模板
clipvault template add 我的程式碼片段

# 使用模板
clipvault template use 我的程式碼片段

# 匯出歷史為 JSON
clipvault export -f json -o backup.json

# 匯入歷史
clipvault import backup.json
```

---

## 📖 詳細使用指南

### 剪貼簿監控

```bash
# 預設 0.5 秒間隔
clipvault watch

# 自訂間隔（1 秒）
clipvault watch -i 1.0

# 靜默模式（無通知）
clipvault watch --silent
```

### 搜尋模式

```bash
# 精確子字串搜尋
clipvault search "錯誤處理"

# 正則表達式搜尋
clipvault search "def\s+\w+"

# 模糊搜尋（容忍拼寫錯誤）
clipvault search "pythn 函數" --fuzzy

# 結合類別過濾
clipvault search "api" -c link
```

### TUI 瀏覽器

使用 `clipvault tui` 啟動互動式終端介面：

| 按鍵 | 操作 |
|------|------|
| `↑/↓` 或 `j/k` | 上下導航 |
| `Enter` | 查看條目詳情 |
| `y` | 複製選中條目 |
| `p` | 切換置頂 |
| `d` | 刪除條目 |
| `/` | 搜尋模式 |
| `f` | 切換類別過濾 |
| `r` | 重新整理列表 |
| `s` | 查看統計 |
| `h` | 說明 |
| `q` | 離開 |

### 模板系統

模板讓你保存常用內容，隨時快速存取：

```bash
# 將當前剪貼簿內容保存為模板
echo "print('Hello, World!')" | clipvault template add hello

# 使用模板（複製到剪貼簿）
clipvault template use hello

# 列出所有模板
clipvault template list

# 刪除模板
clipvault template delete hello
```

---

## 💡 設計理念與迭代規劃

### 設計原則

1. **零依賴** — 僅使用 Python 標準函式庫，無需 pip install
2. **開發者優先** — 終端原生，鍵盤驅動的工作流程
3. **隱私優先** — 所有資料儲存在本地 SQLite，永遠不會離開你的機器
4. **智慧預設** — 自動分類意味著大多數場景零配置
5. **可擴展** — 插件就緒的架構，便於未來增強

### 架構

```
ClipVault/
├── core/
│   ├── engine.py        # 主編排引擎
│   ├── clipboard.py     # 跨平台剪貼簿 I/O
│   ├── storage.py       # SQLite 儲存層
│   ├── categorizer.py   # 智慧內容分類
│   └── search.py        # 多模式搜尋引擎
├── ui/
│   └── tui.py           # 終端使用者介面
└── utils/
    └── helpers.py       # 工具函式
```

### 迭代規劃

- [ ] **v1.1**：剪貼簿內容加密（AES-256）
- [ ] **v1.2**：多資料庫後端支援
- [ ] **v1.3**：自訂分類器插件系統
- [ ] **v1.4**：透過 SFTP/WebDAV 遠端同步
- [ ] **v2.0**：Web 儀表板遠端瀏覽
- [ ] **v2.1**：多機剪貼簿共享

---

## 📦 安裝與部署

### 從原始碼安裝

```bash
git clone https://github.com/gitstq/ClipVault.git
cd ClipVault
pip install -e .
```

### 免安裝運行

```bash
git clone https://github.com/gitstq/ClipVault.git
cd ClipVault
PYTHONPATH=src python -m clipvault --help
```

### 資料儲存位置

所有資料儲存在 `~/.clipvault/` 目錄下：
- `history.db` — SQLite 資料庫，包含所有剪貼簿歷史、模板和設定

---

## 🤝 貢獻指南

歡迎貢獻！請參閱 [CONTRIBUTING.md](CONTRIBUTING.md) 了解指南。

1. Fork 本倉庫
2. 建立功能分支（`git checkout -b feature/amazing-feature`）
3. 使用 [Conventional Commits](https://www.conventionalcommits.org/) 規範提交
4. 推送到你的 Fork（`git push origin feature/amazing-feature`）
5. 發起 Pull Request

---

## 📄 開源協議

本專案基於 MIT 協議開源。詳見 [LICENSE](LICENSE)。

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">ClipVault Team</a>
</p>
