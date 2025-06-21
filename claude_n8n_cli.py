#!/usr/bin/env python3
"""
Claude n8n Advanced CLI Tool
進階的 n8n 工作流管理工具

Usage:
    python3 claude_n8n_cli.py test
    python3 claude_n8n_cli.py list [--active]
    python3 claude_n8n_cli.py activate <WORKFLOW_ID> [--disable]
    python3 claude_n8n_cli.py executions --workflow-id <ID> --limit 10
    python3 claude_n8n_cli.py webhook <WORKFLOW_ID>
    python3 claude_n8n_cli.py update <ID> --name "New Name"
    python3 claude_n8n_cli.py deploy <JSON_FILE> [--activate]
"""

import os
import sys
import json
import requests
import argparse
from typing import Dict, List, Optional, Any
from datetime import datetime
import urllib.parse

# 嘗試載入環境變數
try:
    from env_loader import load_env_file
    load_env_file()
except ImportError:
    # 如果 env_loader 不存在，嘗試手動載入 .env
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

class ClaudeN8nCLI:
    def __init__(self):
        self.host_url = os.getenv('N8N_HOST_URL')
        self.api_key = os.getenv('N8N_API_KEY')

        if not self.host_url or not self.api_key:
            print("錯誤: 請設定必要的環境變數")
            print("💡 請確保 .env 文件包含 N8N_HOST_URL 和 N8N_API_KEY")
            print("   或手動設定環境變數:")
            print("   export N8N_HOST_URL='your_host_url'")
            print("   export N8N_API_KEY='your_api_key'")
            sys.exit(1)
        
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # 移除 URL 末尾的斜線
        self.host_url = self.host_url.rstrip('/')
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """發送 HTTP 請求到 n8n API"""
        url = f"{self.host_url}/api/v1{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data, params=params)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data, params=params)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers, params=params)
            else:
                raise ValueError(f"不支援的 HTTP 方法: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API 請求失敗: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"錯誤詳情: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
                except:
                    print(f"回應內容: {e.response.text}")
            sys.exit(1)
    
    def test_connectivity(self) -> None:
        """測試 API 連接性"""
        print("正在測試 n8n API 連接...")
        print(f"主機: {self.host_url}")
        
        try:
            # 測試基本連接
            result = self._make_request('GET', '/workflows', params={'limit': 1})
            print("✅ API 連接成功!")
            
            # 顯示基本資訊
            workflows_count = len(result.get('data', []))
            print(f"📊 可訪問的工作流數量: {workflows_count}")
            
            # 測試執行歷史訪問
            try:
                exec_result = self._make_request('GET', '/executions', params={'limit': 1})
                executions_count = len(exec_result.get('data', []))
                print(f"📈 可訪問的執行記錄數量: {executions_count}")
            except:
                print("⚠️  無法訪問執行記錄 (可能需要額外權限)")
            
            print("🎉 連接測試完成!")
            
        except Exception as e:
            print(f"❌ 連接測試失敗: {e}")
            sys.exit(1)
    
    def list_workflows(self, active_only: bool = False) -> None:
        """列出工作流 (可選擇只顯示啟用的)"""
        print("正在獲取工作流列表...")
        result = self._make_request('GET', '/workflows')
        
        workflows = result.get('data', [])
        if active_only:
            workflows = [w for w in workflows if w.get('active', False)]
            print(f"顯示啟用的工作流:")
        else:
            print(f"顯示所有工作流:")
        
        if not workflows:
            print("沒有找到符合條件的工作流")
            return
        
        print(f"\n找到 {len(workflows)} 個工作流:")
        print("-" * 90)
        print(f"{'ID':<20} {'名稱':<35} {'狀態':<8} {'節點':<6} {'標籤':<15}")
        print("-" * 90)
        
        for workflow in workflows:
            workflow_id = workflow.get('id', 'N/A')
            name = workflow.get('name', 'N/A')[:34]
            active = '🟢啟用' if workflow.get('active', False) else '🔴停用'
            node_count = len(workflow.get('nodes', []))
            tags = ', '.join(workflow.get('tags', []))[:14]
            
            print(f"{workflow_id:<20} {name:<35} {active:<8} {node_count:<6} {tags:<15}")
    
    def activate_workflow(self, workflow_id: str, disable: bool = False) -> None:
        """啟用或停用工作流"""
        action = "停用" if disable else "啟用"
        print(f"正在{action}工作流 {workflow_id}...")
        
        data = {"active": not disable}
        result = self._make_request('PATCH', f'/workflows/{workflow_id}', data)
        
        workflow = result.get('data', {})
        new_status = '啟用' if workflow.get('active', False) else '停用'
        print(f"✅ 工作流狀態已更新為: {new_status}")
        print(f"工作流名稱: {workflow.get('name', 'N/A')}")
    
    def get_executions(self, workflow_id: Optional[str] = None, limit: int = 10) -> None:
        """獲取執行歷史"""
        params = {'limit': limit}
        if workflow_id:
            params['workflowId'] = workflow_id
            print(f"正在獲取工作流 {workflow_id} 的執行歷史 (最近 {limit} 次)...")
        else:
            print(f"正在獲取所有工作流的執行歷史 (最近 {limit} 次)...")
        
        result = self._make_request('GET', '/executions', params=params)
        executions = result.get('data', [])
        
        if not executions:
            print("沒有找到執行記錄")
            return
        
        print(f"\n找到 {len(executions)} 個執行記錄:")
        print("-" * 100)
        print(f"{'執行ID':<20} {'工作流名稱':<25} {'狀態':<12} {'開始時間':<20} {'持續時間':<10}")
        print("-" * 100)
        
        for execution in executions:
            exec_id = execution.get('id', 'N/A')
            workflow_name = execution.get('workflowData', {}).get('name', 'N/A')[:24]
            status = execution.get('status', 'N/A')
            
            # 格式化狀態顯示
            status_display = {
                'success': '🟢 成功',
                'error': '🔴 錯誤', 
                'running': '🟡 執行中',
                'waiting': '🟠 等待中'
            }.get(status, f'❓ {status}')
            
            start_time = execution.get('startedAt', '')
            if start_time:
                try:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    start_display = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    start_display = start_time[:19]
            else:
                start_display = 'N/A'
            
            # 計算持續時間
            duration = 'N/A'
            if execution.get('startedAt') and execution.get('stoppedAt'):
                try:
                    start = datetime.fromisoformat(execution['startedAt'].replace('Z', '+00:00'))
                    stop = datetime.fromisoformat(execution['stoppedAt'].replace('Z', '+00:00'))
                    duration_sec = (stop - start).total_seconds()
                    duration = f"{duration_sec:.1f}s"
                except:
                    pass
            
            print(f"{exec_id:<20} {workflow_name:<25} {status_display:<12} {start_display:<20} {duration:<10}")
    
    def generate_webhook_url(self, workflow_id: str) -> None:
        """生成 webhook 測試 URL"""
        print(f"正在分析工作流 {workflow_id} 的 webhook 配置...")
        
        # 獲取工作流詳情
        result = self._make_request('GET', f'/workflows/{workflow_id}')
        workflow = result.get('data', {})
        
        # 尋找 webhook 節點
        webhook_nodes = []
        for node in workflow.get('nodes', []):
            if node.get('type') == 'n8n-nodes-base.webhook':
                webhook_nodes.append(node)
        
        if not webhook_nodes:
            print("❌ 此工作流中沒有找到 webhook 節點")
            return
        
        print(f"✅ 找到 {len(webhook_nodes)} 個 webhook 節點:")
        print("-" * 80)
        
        for i, node in enumerate(webhook_nodes, 1):
            node_name = node.get('name', f'Webhook {i}')
            params = node.get('parameters', {})
            
            # 獲取 webhook 配置
            http_method = params.get('httpMethod', 'GET')
            path = params.get('path', '')
            webhook_id = node.get('webhookId', '')
            
            # 生成 URL
            if webhook_id:
                webhook_url = f"{self.host_url}/webhook/{webhook_id}"
            elif path:
                webhook_url = f"{self.host_url}/webhook/{path}"
            else:
                webhook_url = f"{self.host_url}/webhook/[需要配置路徑]"
            
            print(f"{i}. 節點名稱: {node_name}")
            print(f"   HTTP 方法: {http_method}")
            print(f"   路徑: {path or '[未設定]'}")
            print(f"   Webhook URL: {webhook_url}")
            print(f"   測試命令: curl -X {http_method} \"{webhook_url}\"")
            print()

    def update_workflow(self, workflow_id: str, name: Optional[str] = None, **kwargs) -> None:
        """更新工作流屬性"""
        print(f"正在更新工作流 {workflow_id}...")

        # 準備更新數據
        update_data = {}
        if name:
            update_data['name'] = name

        # 添加其他可能的更新參數
        for key, value in kwargs.items():
            if value is not None:
                update_data[key] = value

        if not update_data:
            print("❌ 沒有提供要更新的數據")
            return

        result = self._make_request('PATCH', f'/workflows/{workflow_id}', update_data)
        workflow = result.get('data', {})

        print("✅ 工作流更新成功!")
        print(f"工作流ID: {workflow.get('id', 'N/A')}")
        print(f"工作流名稱: {workflow.get('name', 'N/A')}")
        print(f"狀態: {'啟用' if workflow.get('active', False) else '停用'}")

    def deploy_workflow(self, json_file: str, activate: bool = False) -> None:
        """部署工作流從 JSON 文件"""
        print(f"正在部署工作流從文件: {json_file}")

        # 讀取 JSON 文件
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
        except FileNotFoundError:
            print(f"❌ 文件不存在: {json_file}")
            return
        except json.JSONDecodeError as e:
            print(f"❌ JSON 格式錯誤: {e}")
            return

        workflow_name = workflow_data.get('name', '未命名工作流')
        print(f"工作流名稱: {workflow_name}")

        # 檢查是否已存在同名工作流
        existing_workflows = self._make_request('GET', '/workflows')
        existing_workflow = None

        for wf in existing_workflows.get('data', []):
            if wf.get('name') == workflow_name:
                existing_workflow = wf
                break

        if existing_workflow:
            workflow_id = existing_workflow['id']
            print(f"🔄 發現同名工作流，正在更新 (ID: {workflow_id})")

            # 更新現有工作流
            result = self._make_request('PUT', f'/workflows/{workflow_id}', workflow_data)
        else:
            print("🆕 創建新工作流")

            # 創建新工作流
            result = self._make_request('POST', '/workflows', workflow_data)

        deployed_workflow = result.get('data', {})
        workflow_id = deployed_workflow.get('id')

        print("✅ 工作流部署成功!")
        print(f"工作流ID: {workflow_id}")
        print(f"工作流名稱: {deployed_workflow.get('name', 'N/A')}")

        # 如果需要啟用工作流
        if activate and not deployed_workflow.get('active', False):
            print("🔄 正在啟用工作流...")
            self.activate_workflow(workflow_id, disable=False)

        print(f"狀態: {'啟用' if deployed_workflow.get('active', False) else '停用'}")

def main():
    parser = argparse.ArgumentParser(description='Claude n8n 進階 CLI 工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # test 命令
    subparsers.add_parser('test', help='測試 API 連接性')

    # list 命令
    list_parser = subparsers.add_parser('list', help='列出工作流')
    list_parser.add_argument('--active', action='store_true', help='只顯示啟用的工作流')

    # activate 命令
    activate_parser = subparsers.add_parser('activate', help='啟用或停用工作流')
    activate_parser.add_argument('workflow_id', help='工作流ID')
    activate_parser.add_argument('--disable', action='store_true', help='停用工作流')

    # executions 命令
    exec_parser = subparsers.add_parser('executions', help='獲取執行歷史')
    exec_parser.add_argument('--workflow-id', help='特定工作流ID')
    exec_parser.add_argument('--limit', type=int, default=10, help='限制結果數量')

    # webhook 命令
    webhook_parser = subparsers.add_parser('webhook', help='生成 webhook 測試 URL')
    webhook_parser.add_argument('workflow_id', help='工作流ID')

    # update 命令
    update_parser = subparsers.add_parser('update', help='更新工作流')
    update_parser.add_argument('workflow_id', help='工作流ID')
    update_parser.add_argument('--name', help='新的工作流名稱')

    # deploy 命令
    deploy_parser = subparsers.add_parser('deploy', help='部署工作流從 JSON 文件')
    deploy_parser.add_argument('json_file', help='工作流 JSON 文件路徑')
    deploy_parser.add_argument('--activate', action='store_true', help='部署後自動啟用')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 初始化 CLI
    cli = ClaudeN8nCLI()

    # 執行對應的命令
    try:
        if args.command == 'test':
            cli.test_connectivity()
        elif args.command == 'list':
            cli.list_workflows(active_only=args.active)
        elif args.command == 'activate':
            cli.activate_workflow(args.workflow_id, disable=args.disable)
        elif args.command == 'executions':
            cli.get_executions(workflow_id=getattr(args, 'workflow_id', None), limit=args.limit)
        elif args.command == 'webhook':
            cli.generate_webhook_url(args.workflow_id)
        elif args.command == 'update':
            cli.update_workflow(args.workflow_id, name=args.name)
        elif args.command == 'deploy':
            cli.deploy_workflow(args.json_file, activate=args.activate)
    except KeyboardInterrupt:
        print("\n操作被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"執行命令時發生錯誤: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
