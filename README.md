# 🚀 n8n Python 工具套件 & LINE Bot 自動化管道

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![n8n](https://img.shields.io/badge/n8n-Compatible-green.svg)](https://n8n.io)
[![LINE Bot](https://img.shields.io/badge/LINE-Bot-00C300.svg)](https://developers.line.biz/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

完整的 n8n 工作流管理和 LINE Bot 自動化解決方案，支持從本地開發環境到雲端部署的無縫整合。

## 📋 目錄

- [功能特色](#-功能特色)
- [快速開始](#-快速開始)
- [工具說明](#-工具說明)
- [使用範例](#-使用範例)
- [文檔](#-文檔)
- [環境配置](#-環境配置)
- [貢獻](#-貢獻)

## ✨ 功能特色

### 🔧 n8n 工具套件
- **完整的 API 整合** - 支持所有主要的 n8n API 操作
- **工作流管理** - 列出、獲取、執行、啟用/停用工作流
- **自動化部署** - 批量部署、驗證、備份工作流
- **執行監控** - 查看執行歷史和狀態
- **Webhook 管理** - 生成和測試 webhook URL

### 🤖 LINE Bot 整合
- **AI 收據辨識** - 自動記帳系統
- **智能助手** - FastGPT 整合
- **行事曆管理** - Google Calendar 整合
- **天氣通知** - 台灣天氣每日推送

### 🛠️ 開發工具
- **中文界面** - 完全中文化的用戶體驗
- **錯誤處理** - 詳細的錯誤訊息和診斷
- **批量操作** - 支持批量部署和管理
- **備份功能** - 自動備份現有工作流

## 🚀 快速開始

### 1. 環境設置

```bash
# 克隆倉庫
git clone https://github.com/eliajhmauve/autopipelineRecord.git
cd autopipelineRecord

# 運行快速設置
python3 setup_n8n_tools.py
```

### 2. 配置環境變數

```bash
export N8N_HOST_URL="https://gmgm.zeabur.app"
export N8N_API_KEY="your_api_key_here"
```

### 3. 測試連接

```bash
python3 claude_n8n_cli.py test
```

## 🔧 工具說明

### 📁 核心工具

| 工具 | 功能 | 使用場景 |
|------|------|----------|
| `n8n_integration.py` | 基本 CLI 工具 | 日常工作流管理 |
| `claude_n8n_cli.py` | 進階 CLI 工具 | 高級功能和監控 |
| `n8n_deploy_pipeline.py` | 自動化部署管道 | CI/CD 和批量操作 |
| `setup_n8n_tools.py` | 快速設置腳本 | 初始環境配置 |

### 📚 文檔文件

| 文件 | 內容 | 用途 |
|------|------|------|
| `CLAUDE.md` | n8n + Claude 整合配置 | API 配置參考 |
| `LINE_INTEGRATION.md` | LINE Bot 整合說明 | LINE 開發指南 |
| `N8N_TOOLS_README.md` | 詳細使用說明 | 完整操作手冊 |

## 💡 使用範例

### 基本工作流管理

```bash
# 列出所有工作流
python3 n8n_integration.py list-workflows

# 獲取工作流詳情
python3 n8n_integration.py get-workflow <WORKFLOW_ID>

# 執行工作流
python3 n8n_integration.py execute <WORKFLOW_ID>
```

### 進階功能

```bash
# 測試 API 連接
python3 claude_n8n_cli.py test

# 列出啟用的工作流
python3 claude_n8n_cli.py list --active

# 獲取執行歷史
python3 claude_n8n_cli.py executions --workflow-id <ID> --limit 10

# 生成 webhook URL
python3 claude_n8n_cli.py webhook <WORKFLOW_ID>
```

### 自動化部署

```bash
# 部署單個工作流
python3 n8n_deploy_pipeline.py deploy Line___AI______.json --activate

# 批量部署
python3 n8n_deploy_pipeline.py batch-deploy ./workflows --activate

# 備份所有工作流
python3 n8n_deploy_pipeline.py backup --output-dir ./backup
```

## 📖 文檔

### 🔗 快速連結

- [**完整使用說明**](N8N_TOOLS_README.md) - 詳細的工具使用指南
- [**n8n 配置**](CLAUDE.md) - API 配置和最佳實踐
- [**LINE Bot 整合**](LINE_INTEGRATION.md) - LINE 開發和部署指南

### 📊 工作流範例

- [**LINE 收據AI辨識**](Line___AI______.json) - 自動記帳系統工作流

## ⚙️ 環境配置

### 必要需求

- Python 3.7+
- requests 套件
- 有效的 n8n API Key
- 網路連接到 n8n 實例

### 支援的 n8n 版本

- n8n 0.190.0+
- 支援所有主要的 n8n API 端點

### 整合服務

- **n8n**: 工作流自動化平台
- **LINE Messaging API**: LINE Bot 開發
- **Google APIs**: Calendar, Gmail, Sheets
- **OpenAI API**: AI 功能整合
- **FastGPT**: 智能對話系統

## 🛡️ 安全注意事項

- 🔐 **API Key 安全**: 使用環境變數存儲敏感信息
- 🔄 **定期輪換**: 定期更新 API 金鑰
- 📊 **監控使用**: 監控 API 使用情況
- 🚫 **避免硬編碼**: 不在代碼中硬編碼憑證

## 🔍 故障排除

### 常見問題

1. **連接失敗**
   ```bash
   python3 claude_n8n_cli.py test
   ```

2. **環境變數未設置**
   ```bash
   echo $N8N_HOST_URL
   echo $N8N_API_KEY
   ```

3. **工作流驗證失敗**
   ```bash
   python3 n8n_deploy_pipeline.py validate <JSON_FILE>
   ```

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

### 開發流程

1. Fork 此倉庫
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 📄 授權

此專案採用 MIT 授權 - 查看 [LICENSE](LICENSE) 文件了解詳情。

## 🙏 致謝

- [n8n](https://n8n.io) - 強大的工作流自動化平台
- [LINE Developers](https://developers.line.biz/) - LINE Bot 開發支援
- [OpenAI](https://openai.com) - AI 功能支援

## 📞 聯繫

- **作者**: WenKai Shi
- **GitHub**: [@eliajhmauve](https://github.com/eliajhmauve)
- **專案連結**: [https://github.com/eliajhmauve/autopipelineRecord](https://github.com/eliajhmauve/autopipelineRecord)

---

⭐ 如果這個專案對您有幫助，請給個星星！
