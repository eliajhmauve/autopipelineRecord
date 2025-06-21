# 🔐 安全配置指南

本文檔說明如何安全地管理 API 金鑰和其他敏感資訊。

## 📋 重要安全原則

### ❌ 絕對不要做的事情
- **不要**在代碼中硬編碼 API 金鑰
- **不要**將 `.env` 文件提交到 Git 倉庫
- **不要**在公開場所分享 API 金鑰
- **不要**在日誌中記錄完整的 API 金鑰

### ✅ 應該做的事情
- **使用** `.env` 文件存儲敏感資訊
- **使用** `.gitignore` 防止敏感文件被提交
- **定期輪換** API 金鑰
- **監控** API 使用情況

## 🔧 環境變數設置

### 1. 創建 .env 文件

```bash
# 複製範例文件
cp .env.example .env

# 編輯 .env 文件，填入您的實際值
nano .env
```

### 2. .env 文件格式

```bash
# n8n 配置
N8N_HOST_URL=https://your-n8n-instance.com
N8N_API_KEY=your_actual_api_key_here

# 其他服務配置
LINE_CHANNEL_ACCESS_TOKEN=your_line_token
OPENAI_API_KEY=your_openai_key
```

### 3. 載入環境變數

#### 方法 1: 使用 env_loader.py
```python
from env_loader import load_env_file
load_env_file()
```

#### 方法 2: 手動載入
```bash
source .env
```

#### 方法 3: 在 shell 中設置
```bash
export N8N_HOST_URL="your_host_url"
export N8N_API_KEY="your_api_key"
```

## 🛡️ 文件權限設置

### 設置 .env 文件權限
```bash
# 只有擁有者可以讀寫
chmod 600 .env

# 檢查權限
ls -la .env
```

### 檢查 .gitignore
確保 `.gitignore` 文件包含：
```
.env
.env.local
.env.development
.env.test
.env.production
*.key
*.pem
credentials.json
```

## 🔍 安全檢查清單

### 開發環境
- [ ] `.env` 文件已創建並包含所有必要變數
- [ ] `.env` 文件權限設置為 600
- [ ] `.gitignore` 包含 `.env` 和其他敏感文件
- [ ] 代碼中沒有硬編碼的 API 金鑰

### 生產環境
- [ ] 使用不同的 API 金鑰（與開發環境分離）
- [ ] 定期輪換 API 金鑰
- [ ] 監控 API 使用情況
- [ ] 設置適當的 API 權限範圍

### Git 倉庫
- [ ] `.env` 文件未被追蹤
- [ ] 歷史提交中沒有敏感資訊
- [ ] `.env.example` 文件不包含實際的 API 金鑰

## 🚨 如果 API 金鑰洩露

### 立即行動
1. **撤銷洩露的 API 金鑰**
   - 登入相關服務控制台
   - 立即撤銷或刪除洩露的金鑰

2. **生成新的 API 金鑰**
   - 創建新的 API 金鑰
   - 更新 `.env` 文件

3. **檢查使用記錄**
   - 查看 API 使用日誌
   - 檢查是否有異常活動

4. **更新所有相關系統**
   - 更新所有使用該 API 金鑰的應用
   - 重新部署相關服務

## 🔧 工具和腳本

### 環境變數檢查工具
```bash
# 檢查環境變數狀態
python3 env_loader.py

# 測試 n8n 連接
python3 claude_n8n_cli.py test
```

### 安全掃描
```bash
# 檢查是否有硬編碼的 API 金鑰
grep -r "eyJ\|sk-\|pk_\|api.*key" --exclude-dir=.git --exclude="*.md" .

# 檢查 .env 文件是否被追蹤
git status --ignored
```

## 📚 最佳實踐

### API 金鑰管理
1. **使用最小權限原則**
   - 只授予必要的 API 權限
   - 定期審查權限設置

2. **定期輪換**
   - 每 90 天輪換一次 API 金鑰
   - 在懷疑洩露時立即輪換

3. **監控使用**
   - 設置 API 使用量警報
   - 監控異常訪問模式

### 開發流程
1. **代碼審查**
   - 審查所有涉及 API 金鑰的代碼
   - 確保沒有硬編碼的敏感資訊

2. **自動化檢查**
   - 使用 pre-commit hooks 檢查敏感資訊
   - 在 CI/CD 中加入安全掃描

3. **文檔更新**
   - 保持安全文檔的更新
   - 培訓團隊成員安全意識

## 🆘 緊急聯繫

如果發現安全問題，請立即：
1. 停止使用可能洩露的 API 金鑰
2. 聯繫相關服務提供商
3. 記錄事件詳情
4. 更新安全措施

## 📞 相關資源

- [n8n API 文檔](https://docs.n8n.io/api/)
- [LINE Developers 安全指南](https://developers.line.biz/en/docs/messaging-api/security/)
- [OpenAI API 安全最佳實踐](https://platform.openai.com/docs/guides/safety-best-practices)

---

⚠️ **記住**: 安全是一個持續的過程，不是一次性的設置！
