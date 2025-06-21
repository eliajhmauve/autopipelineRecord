# n8n Python 工具套件使用說明

這套工具提供了完整的 n8n 工作流管理功能，支持從本地開發環境到 n8n 實例的無縫部署和管理。

## 🚀 快速開始

### 1. 環境設置

運行快速設置腳本：

```bash
python3 setup_n8n_tools.py
```

或手動設置環境變數：

```bash
export N8N_HOST_URL="https://gmgm.zeabur.app"
export N8N_API_KEY="your_api_key_here"
```

### 2. 驗證設置

```bash
python3 claude_n8n_cli.py test
```

## 📁 工具說明

### 1. `n8n_integration.py` - 基本 CLI 工具

提供基本的工作流管理功能：

```bash
# 列出所有工作流
python3 n8n_integration.py list-workflows

# 獲取特定工作流詳情
python3 n8n_integration.py get-workflow <WORKFLOW_ID>

# 執行工作流
python3 n8n_integration.py execute <WORKFLOW_ID>

# 創建範例工作流
python3 n8n_integration.py create-sample
```

### 2. `claude_n8n_cli.py` - 進階 CLI 工具

提供進階管理功能：

```bash
# 測試 API 連接性
python3 claude_n8n_cli.py test

# 列出工作流（可選擇只顯示啟用的）
python3 claude_n8n_cli.py list [--active]

# 啟用/停用工作流
python3 claude_n8n_cli.py activate <WORKFLOW_ID>
python3 claude_n8n_cli.py activate <WORKFLOW_ID> --disable

# 獲取執行歷史
python3 claude_n8n_cli.py executions --workflow-id <ID> --limit 10

# 生成 webhook 測試 URL
python3 claude_n8n_cli.py webhook <WORKFLOW_ID>

# 更新工作流名稱
python3 claude_n8n_cli.py update <ID> --name "新名稱"

# 部署工作流
python3 claude_n8n_cli.py deploy <JSON_FILE> [--activate]
```

### 3. `n8n_deploy_pipeline.py` - 自動化部署管道

提供完整的部署和備份功能：

```bash
# 部署單個工作流
python3 n8n_deploy_pipeline.py deploy Line___AI______.json --activate

# 批量部署目錄中的所有工作流
python3 n8n_deploy_pipeline.py batch-deploy ./workflows --activate

# 驗證工作流 JSON 文件
python3 n8n_deploy_pipeline.py validate Line___AI______.json

# 備份所有工作流
python3 n8n_deploy_pipeline.py backup --output-dir ./backup
```

## 🔧 實際使用範例

### 部署您的 LINE Bot 工作流

```bash
# 1. 驗證工作流文件
python3 n8n_deploy_pipeline.py validate Line___AI______.json

# 2. 部署並啟用工作流
python3 n8n_deploy_pipeline.py deploy Line___AI______.json --activate

# 3. 檢查部署狀態
python3 claude_n8n_cli.py list --active

# 4. 獲取 webhook URL
python3 claude_n8n_cli.py webhook <WORKFLOW_ID>
```

### 開發工作流程

```bash
# 1. 備份現有工作流
python3 n8n_deploy_pipeline.py backup --output-dir ./backup

# 2. 在本地修改工作流 JSON 文件

# 3. 驗證修改後的工作流
python3 n8n_deploy_pipeline.py validate modified_workflow.json

# 4. 部署更新
python3 n8n_deploy_pipeline.py deploy modified_workflow.json --activate

# 5. 檢查執行歷史
python3 claude_n8n_cli.py executions --workflow-id <ID> --limit 5
```

### 批量管理工作流

```bash
# 1. 創建工作流目錄
mkdir workflows
cp *.json workflows/

# 2. 批量部署
python3 n8n_deploy_pipeline.py batch-deploy ./workflows --activate --validate

# 3. 檢查所有啟用的工作流
python3 claude_n8n_cli.py list --active
```

## 🛠️ 便捷別名設置

將以下別名添加到您的 `~/.bashrc` 或 `~/.zshrc` 文件中：

```bash
# n8n 工具別名
alias n8n-list='python3 n8n_integration.py list-workflows'
alias n8n-test='python3 claude_n8n_cli.py test'
alias n8n-deploy='python3 n8n_deploy_pipeline.py deploy'
alias n8n-backup='python3 n8n_deploy_pipeline.py backup'
alias n8n-active='python3 claude_n8n_cli.py list --active'
alias n8n-exec='python3 claude_n8n_cli.py executions'
```

使用別名：

```bash
n8n-test          # 測試連接
n8n-list          # 列出工作流
n8n-active        # 列出啟用的工作流
n8n-deploy Line___AI______.json --activate  # 部署工作流
n8n-backup        # 備份工作流
```

## 📊 功能特色

### ✅ 已實現功能

- **完整的 API 整合**: 支持所有主要的 n8n API 操作
- **工作流驗證**: 部署前自動驗證 JSON 結構
- **批量操作**: 支持批量部署和管理
- **錯誤處理**: 詳細的錯誤訊息和狀態回報
- **中文界面**: 完全中文化的用戶界面
- **備份功能**: 自動備份現有工作流
- **統計報告**: 詳細的部署統計和結果報告

### 🔄 自動化工作流程

1. **本地開發** → 編輯工作流 JSON 文件
2. **驗證** → 自動檢查工作流結構
3. **部署** → 上傳到 n8n 實例
4. **啟用** → 自動啟用工作流
5. **監控** → 檢查執行狀態和歷史

## 🚨 注意事項

1. **環境變數**: 確保正確設置 `N8N_HOST_URL` 和 `N8N_API_KEY`
2. **API 權限**: 確保 API Key 具有足夠的權限
3. **網路連接**: 確保能夠訪問 n8n 實例
4. **備份**: 部署前建議先備份現有工作流
5. **測試**: 部署後測試工作流功能是否正常

## 🔍 故障排除

### 連接問題

```bash
# 測試基本連接
python3 claude_n8n_cli.py test

# 檢查環境變數
echo $N8N_HOST_URL
echo $N8N_API_KEY
```

### 部署問題

```bash
# 驗證工作流文件
python3 n8n_deploy_pipeline.py validate <JSON_FILE>

# 檢查 API 權限
python3 claude_n8n_cli.py list
```

### 執行問題

```bash
# 檢查執行歷史
python3 claude_n8n_cli.py executions --workflow-id <ID> --limit 5

# 檢查工作流狀態
python3 n8n_integration.py get-workflow <WORKFLOW_ID>
```

## 📞 支援

如果遇到問題，請：

1. 檢查環境變數設置
2. 驗證 n8n 實例連接
3. 查看詳細錯誤訊息
4. 使用 `python3 claude_n8n_cli.py test` 診斷連接問題

這套工具完全符合您在 `CLAUDE.md` 中記錄的使用模式，並提供了更強大的自動化功能。
