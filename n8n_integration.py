#!/usr/bin/env python3
"""
n8n Integration Basic CLI Tool
基本的 n8n 工作流管理工具

Usage:
    python3 n8n_integration.py list-workflows
    python3 n8n_integration.py get-workflow <WORKFLOW_ID>
    python3 n8n_integration.py execute <WORKFLOW_ID>
    python3 n8n_integration.py create-sample
"""

import os
import sys
import json
import requests
import argparse
from typing import Dict, List, Optional, Any

class N8nIntegration:
    def __init__(self):
        self.host_url = os.getenv('N8N_HOST_URL', 'https://gmgm.zeabur.app')
        self.api_key = os.getenv('N8N_API_KEY')
        
        if not self.api_key:
            print("錯誤: 請設定 N8N_API_KEY 環境變數")
            print("export N8N_API_KEY='your_api_key_here'")
            sys.exit(1)
        
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # 移除 URL 末尾的斜線
        self.host_url = self.host_url.rstrip('/')
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """發送 HTTP 請求到 n8n API"""
        url = f"{self.host_url}/api/v1{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers)
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
    
    def list_workflows(self) -> None:
        """列出所有工作流"""
        print("正在獲取工作流列表...")
        result = self._make_request('GET', '/workflows')
        
        workflows = result.get('data', [])
        if not workflows:
            print("沒有找到任何工作流")
            return
        
        print(f"\n找到 {len(workflows)} 個工作流:")
        print("-" * 80)
        print(f"{'ID':<20} {'名稱':<30} {'狀態':<10} {'節點數':<8}")
        print("-" * 80)
        
        for workflow in workflows:
            workflow_id = workflow.get('id', 'N/A')
            name = workflow.get('name', 'N/A')
            active = '啟用' if workflow.get('active', False) else '停用'
            node_count = len(workflow.get('nodes', []))
            
            print(f"{workflow_id:<20} {name:<30} {active:<10} {node_count:<8}")
    
    def get_workflow(self, workflow_id: str) -> None:
        """獲取特定工作流的詳細資訊"""
        print(f"正在獲取工作流 {workflow_id} 的詳細資訊...")
        result = self._make_request('GET', f'/workflows/{workflow_id}')
        
        workflow = result.get('data', {})
        print(f"\n工作流詳細資訊:")
        print("-" * 50)
        print(f"ID: {workflow.get('id', 'N/A')}")
        print(f"名稱: {workflow.get('name', 'N/A')}")
        print(f"狀態: {'啟用' if workflow.get('active', False) else '停用'}")
        print(f"節點數量: {len(workflow.get('nodes', []))}")
        print(f"連接數量: {len(workflow.get('connections', {}))}")
        print(f"版本ID: {workflow.get('versionId', 'N/A')}")
        
        # 顯示節點資訊
        nodes = workflow.get('nodes', [])
        if nodes:
            print(f"\n節點列表:")
            for i, node in enumerate(nodes, 1):
                node_type = node.get('type', 'N/A')
                node_name = node.get('name', 'N/A')
                print(f"  {i}. {node_name} ({node_type})")
    
    def execute_workflow(self, workflow_id: str) -> None:
        """執行指定的工作流"""
        print(f"正在執行工作流 {workflow_id}...")
        result = self._make_request('POST', f'/workflows/{workflow_id}/execute')
        
        execution_id = result.get('data', {}).get('executionId')
        if execution_id:
            print(f"工作流執行成功!")
            print(f"執行ID: {execution_id}")
        else:
            print("工作流執行完成，但沒有返回執行ID")
    
    def create_sample_workflow(self) -> None:
        """創建一個範例工作流"""
        sample_workflow = {
            "name": "範例工作流 - 基本測試",
            "nodes": [
                {
                    "parameters": {},
                    "type": "n8n-nodes-base.start",
                    "typeVersion": 1,
                    "position": [240, 300],
                    "id": "start-node",
                    "name": "Start"
                },
                {
                    "parameters": {
                        "values": {
                            "string": [
                                {
                                    "name": "message",
                                    "value": "Hello from n8n API!"
                                }
                            ]
                        }
                    },
                    "type": "n8n-nodes-base.set",
                    "typeVersion": 1,
                    "position": [460, 300],
                    "id": "set-node",
                    "name": "Set Message"
                }
            ],
            "connections": {
                "Start": {
                    "main": [
                        [
                            {
                                "node": "Set Message",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            },
            "active": False,
            "settings": {},
            "tags": []
        }
        
        print("正在創建範例工作流...")
        result = self._make_request('POST', '/workflows', sample_workflow)
        
        workflow = result.get('data', {})
        workflow_id = workflow.get('id')
        workflow_name = workflow.get('name')
        
        print(f"範例工作流創建成功!")
        print(f"工作流ID: {workflow_id}")
        print(f"工作流名稱: {workflow_name}")
        print(f"狀態: {'啟用' if workflow.get('active', False) else '停用'}")

def main():
    parser = argparse.ArgumentParser(description='n8n 基本整合工具')
    parser.add_argument('command', choices=['list-workflows', 'get-workflow', 'execute', 'create-sample'],
                       help='要執行的命令')
    parser.add_argument('workflow_id', nargs='?', help='工作流ID (用於 get-workflow 和 execute 命令)')
    
    args = parser.parse_args()
    
    # 驗證參數
    if args.command in ['get-workflow', 'execute'] and not args.workflow_id:
        print(f"錯誤: {args.command} 命令需要提供 workflow_id 參數")
        sys.exit(1)
    
    # 初始化 n8n 整合
    n8n = N8nIntegration()
    
    # 執行對應的命令
    try:
        if args.command == 'list-workflows':
            n8n.list_workflows()
        elif args.command == 'get-workflow':
            n8n.get_workflow(args.workflow_id)
        elif args.command == 'execute':
            n8n.execute_workflow(args.workflow_id)
        elif args.command == 'create-sample':
            n8n.create_sample_workflow()
    except KeyboardInterrupt:
        print("\n操作被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"執行命令時發生錯誤: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
