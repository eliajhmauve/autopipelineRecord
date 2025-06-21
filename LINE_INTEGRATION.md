# LINE Messaging API 整合指南

## LINE 頻道設置

1. 登入 [LINE Developers Console](https://developers.line.biz/console/)
2. 創建一個新的Provider（如果尚未有）
3. 在Provider下創建一個新的Messaging API頻道
4. 記錄以下重要信息：
   - My user ID `Uea70d34f1cdf75eefc9477fbb3b6de03`
   - Bot basic ID `@826nylpb`
   - Channel ID `2007612302`
   - Channel Secret `2e017b804f5eb49f37d335214e1cf2ea`
   - Channel Access Token (長期)：已提供 `/45UU+ULabECHjdlRvD2enNgh9ha3QWrEzCPhCAutlYycIcnatAnEqrK9T6i8pKJs7VOLFJXYZGXKKE85kQEAhikH8VLbzWahavHJJQ54trx/aKX4T0Z0vWr/IzjfEpOvSkQw2dNRTeToWfqAef9LQdB04t89/1O/w1cDnyilFU=`

## 部署到Zeabur

1. LINE MCP Server代碼已推送到獨立的GitHub存儲庫：https://github.com/eliajhmauve/line-mcp-server
2. 在Zeabur控制台中：
   - 連接GitHub帳戶（Settings → Integrations）
   - 創建新項目（New Project）
   - 選擇Git Services，並選擇GitHub存儲庫 `eliajhmauve/line-mcp-server`
3. 設置環境變量：
   - `CHANNEL_ACCESS_TOKEN`
   - `CHANNEL_SECRET`
   - `MY_USER_ID`
   - `BOT_BASIC_ID`
   - `CHANNEL_ID`

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
   - 配置憑證，使用提供的Channel Access Token
   - 設置操作為"Reply to Message"

## 必要的憑證

1. **LINE Channel Access Token**：已提供
2. **LINE Channel Secret**：需要從LINE Developers Console獲取
3. **OpenAI API Key**：用於o4-mini模型
4. **Google API憑證**：用於Calendar、Sheets和Gmail整合

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

- 不要在代碼或工作流中硬編碼任何API密鑰或令牌
- 使用n8n的憑證存儲功能安全地存儲所有敏感信息
- 定期輪換Channel Access Token
- 監控API使用情況，防止未授權訪問
