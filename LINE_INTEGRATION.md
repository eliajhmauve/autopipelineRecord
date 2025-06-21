# LINE Messaging API 整合指南

## LINE 頻道設置

1. 登入 [LINE Developers Console](https://developers.line.biz/console/)
2. 創建一個新的Provider（如果尚未有）
3. 在Provider下創建一個新的Messaging API頻道
4. 記錄以下重要信息並保存到 `.env` 文件中：
   - My user ID → `LINE_USER_ID`
   - Bot basic ID → `LINE_BOT_BASIC_ID`
   - Channel ID → `LINE_CHANNEL_ID`
   - Channel Secret → `LINE_CHANNEL_SECRET`
   - Channel Access Token → `LINE_CHANNEL_ACCESS_TOKEN`

⚠️ **重要安全提醒**: 所有實際的憑證資訊都已移至 `.env` 文件中，請勿在此文檔或代碼中硬編碼任何敏感資訊。

## 部署到Zeabur

1. LINE MCP Server代碼已推送到獨立的GitHub存儲庫：https://github.com/eliajhmauve/line-mcp-server
2. 在Zeabur控制台中：
   - 連接GitHub帳戶（Settings → Integrations）
   - 創建新項目（New Project）
   - 選擇Git Services，並選擇GitHub存儲庫 `eliajhmauve/line-mcp-server`
3. 設置環境變量（從 `.env` 文件載入）：
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`
   - `LINE_USER_ID`
   - `LINE_BOT_BASIC_ID`
   - `LINE_CHANNEL_ID`

## Webhook 設置

### Webhook URL

在LINE Developers Console中，將Webhook URL設置為：

```
https://gmgm.zeabur.app/webhook/line
```

> 注意：此URL假設我們將在n8n中創建一個名為"line"的webhook端點。如果您在n8n中使用不同的端點名稱，請相應調整URL。

### 啟用Webhook

1. 在LINE Developers Console中啟用"Use webhook"選項
2. 點擊"Verify"按鈕測試連接
3. 確保已關閉"Auto-reply messages"選項，以便由我們的系統處理所有回覆

## n8n 工作流設置

1. 登入Zeabur上的n8n實例 (https://gmgm.zeabur.app)
2. 創建新的工作流
3. 添加Webhook節點作為觸發器：
   - 設置方法為POST
   - 路徑設為`/line`
   - 響應模式設為"Last Node"
   - 啟用"Respond Immediately"選項（處理LINE的5秒超時限制）

4. 添加LINE節點進行回覆：
   - 安裝LINE節點（如果尚未安裝）
   - 配置憑證，使用 `.env` 文件中的 `LINE_CHANNEL_ACCESS_TOKEN`
   - 設置操作為"Reply to Message"

## 必要的憑證

所有憑證都應存儲在 `.env` 文件中：

1. **LINE Channel Access Token** → `LINE_CHANNEL_ACCESS_TOKEN`
2. **LINE Channel Secret** → `LINE_CHANNEL_SECRET`
3. **OpenAI API Key** → `OPENAI_API_KEY`
4. **Google API憑證** → 相關的 Google API 環境變數

## 測試Webhook

1. 在LINE應用中向您的機器人發送消息
2. 檢查n8n工作流的執行日誌，確認webhook正常接收消息
3. 確認機器人能夠回覆消息

## 故障排除

如果webhook驗證失敗：
1. 確認URL是否正確
2. 檢查n8n工作流是否已激活
3. 確認webhook節點配置正確
4. 查看n8n的錯誤日誌

## 安全注意事項

- ✅ **已實施**: 所有敏感資訊已移至 `.env` 文件
- ✅ **已實施**: `.env` 文件受 `.gitignore` 保護，不會被推送到 GitHub
- 🔄 **建議**: 定期輪換 Channel Access Token
- 📊 **建議**: 監控 API 使用情況，防止未授權訪問
- 🔐 **重要**: 使用 n8n 的憑證存儲功能時，從環境變數載入敏感資訊
- 📋 **檢查**: 確保所有團隊成員都有正確的 `.env` 文件配置
