#!/usr/bin/env python3
"""
n8n 自動化部署管道
支持從本地開發環境自動部署工作流到 n8n 實例

Usage:
    python3 n8n_deploy_pipeline.py deploy <JSON_FILE> [--activate] [--validate]
    python3 n8n_deploy_pipeline.py batch-deploy <DIRECTORY> [--activate] [--validate]
    python3 n8n_deploy_pipeline.py validate <JSON_FILE>
    python3 n8n_deploy_pipeline.py backup [--output-dir DIRECTORY]
    python3 n8n_deploy_pipeline.py sync <LOCAL_DIR> <REMOTE_BACKUP>
"""

import os
import sys
import json
import requests
import argparse
import glob
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import shutil
from pathlib import Path

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

class N8nDeployPipeline:
    def __init__(self):
        self.host_url = os.getenv('N8N_HOST_URL')
        self.api_key = os.getenv('N8N_API_KEY')

        if not self.host_url or not self.api_key:
            print("錯誤: 請設定必要的環境變數")
            print("💡 請確保 .env 文件包含 N8N_HOST_URL 和 N8N_API_KEY")
            print("   或手動設定環境變數:")
            print("   export N8N_HOST_URL='your_host_url'")
            print("   export N8N_API_KEY='your_actual_api_key_here'")
            sys.exit(1)
        
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        self.host_url = self.host_url.rstrip('/')
        
        # 部署統計
        self.deploy_stats = {
            'created': 0,
            'updated': 0,
            'activated': 0,
            'errors': 0,
            'skipped': 0
        }
    
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
            else:
                raise ValueError(f"不支援的 HTTP 方法: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 請求失敗: {e}")
    
    def validate_workflow(self, workflow_data: Dict) -> Tuple[bool, List[str]]:
        """驗證工作流 JSON 結構"""
        errors = []
        
        # 檢查必要欄位
        required_fields = ['name', 'nodes', 'connections']
        for field in required_fields:
            if field not in workflow_data:
                errors.append(f"缺少必要欄位: {field}")
        
        # 檢查節點結構
        if 'nodes' in workflow_data:
            nodes = workflow_data['nodes']
            if not isinstance(nodes, list):
                errors.append("nodes 必須是陣列")
            else:
                for i, node in enumerate(nodes):
                    if not isinstance(node, dict):
                        errors.append(f"節點 {i} 必須是物件")
                        continue
                    
                    # 檢查節點必要欄位
                    node_required = ['type', 'typeVersion', 'position', 'id', 'name']
                    for field in node_required:
                        if field not in node:
                            errors.append(f"節點 {i} 缺少必要欄位: {field}")
        
        # 檢查連接結構
        if 'connections' in workflow_data:
            connections = workflow_data['connections']
            if not isinstance(connections, dict):
                errors.append("connections 必須是物件")
        
        # 檢查工作流名稱
        if 'name' in workflow_data:
            name = workflow_data['name']
            if not isinstance(name, str) or len(name.strip()) == 0:
                errors.append("工作流名稱不能為空")
        
        return len(errors) == 0, errors
    
    def deploy_single_workflow(self, json_file: str, activate: bool = False, validate: bool = True) -> bool:
        """部署單個工作流"""
        print(f"\n📁 正在處理文件: {json_file}")
        
        # 讀取 JSON 文件
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
        except FileNotFoundError:
            print(f"❌ 文件不存在: {json_file}")
            self.deploy_stats['errors'] += 1
            return False
        except json.JSONDecodeError as e:
            print(f"❌ JSON 格式錯誤: {e}")
            self.deploy_stats['errors'] += 1
            return False
        
        workflow_name = workflow_data.get('name', '未命名工作流')
        print(f"🏷️  工作流名稱: {workflow_name}")
        
        # 驗證工作流
        if validate:
            print("🔍 正在驗證工作流結構...")
            is_valid, validation_errors = self.validate_workflow(workflow_data)
            if not is_valid:
                print("❌ 工作流驗證失敗:")
                for error in validation_errors:
                    print(f"   - {error}")
                self.deploy_stats['errors'] += 1
                return False
            print("✅ 工作流結構驗證通過")
        
        try:
            # 檢查是否已存在同名工作流
            print("🔍 檢查現有工作流...")
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
                self.deploy_stats['updated'] += 1
                action = "更新"
            else:
                print("🆕 創建新工作流")
                
                # 創建新工作流
                result = self._make_request('POST', '/workflows', workflow_data)
                self.deploy_stats['created'] += 1
                action = "創建"
            
            deployed_workflow = result.get('data', {})
            workflow_id = deployed_workflow.get('id')
            
            print(f"✅ 工作流{action}成功! (ID: {workflow_id})")
            
            # 如果需要啟用工作流
            if activate and not deployed_workflow.get('active', False):
                print("🔄 正在啟用工作流...")
                try:
                    self._make_request('PATCH', f'/workflows/{workflow_id}', {"active": True})
                    print("✅ 工作流已啟用")
                    self.deploy_stats['activated'] += 1
                except Exception as e:
                    print(f"⚠️  啟用工作流失敗: {e}")
            
            current_status = '啟用' if deployed_workflow.get('active', False) or activate else '停用'
            print(f"📊 當前狀態: {current_status}")
            
            return True
            
        except Exception as e:
            print(f"❌ 部署失敗: {e}")
            self.deploy_stats['errors'] += 1
            return False
    
    def batch_deploy(self, directory: str, activate: bool = False, validate: bool = True) -> None:
        """批量部署目錄中的所有工作流"""
        print(f"📂 正在掃描目錄: {directory}")
        
        # 尋找所有 JSON 文件
        json_files = glob.glob(os.path.join(directory, "*.json"))
        
        if not json_files:
            print("❌ 目錄中沒有找到 JSON 文件")
            return
        
        print(f"📋 找到 {len(json_files)} 個 JSON 文件")
        
        # 重置統計
        self.deploy_stats = {key: 0 for key in self.deploy_stats}
        
        successful_deployments = 0
        
        for json_file in json_files:
            if self.deploy_single_workflow(json_file, activate, validate):
                successful_deployments += 1
        
        # 顯示部署統計
        print("\n" + "="*60)
        print("📊 部署統計報告")
        print("="*60)
        print(f"總文件數: {len(json_files)}")
        print(f"成功部署: {successful_deployments}")
        print(f"創建新工作流: {self.deploy_stats['created']}")
        print(f"更新現有工作流: {self.deploy_stats['updated']}")
        print(f"啟用工作流: {self.deploy_stats['activated']}")
        print(f"錯誤數量: {self.deploy_stats['errors']}")
        print(f"跳過數量: {self.deploy_stats['skipped']}")
        
        if self.deploy_stats['errors'] > 0:
            print(f"\n⚠️  有 {self.deploy_stats['errors']} 個文件部署失敗，請檢查上述錯誤訊息")
        else:
            print(f"\n🎉 所有工作流部署完成!")
    
    def backup_workflows(self, output_dir: str = "n8n_backup") -> None:
        """備份所有工作流到本地目錄"""
        print(f"💾 正在備份工作流到目錄: {output_dir}")
        
        # 創建備份目錄
        Path(output_dir).mkdir(exist_ok=True)
        
        try:
            # 獲取所有工作流
            result = self._make_request('GET', '/workflows')
            workflows = result.get('data', [])
            
            if not workflows:
                print("❌ 沒有找到任何工作流")
                return
            
            print(f"📋 找到 {len(workflows)} 個工作流")
            
            backup_count = 0
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for workflow in workflows:
                workflow_id = workflow.get('id')
                workflow_name = workflow.get('name', 'unnamed_workflow')
                
                # 清理文件名中的特殊字符
                safe_name = "".join(c for c in workflow_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_name = safe_name.replace(' ', '_')
                
                filename = f"{safe_name}_{workflow_id}_{timestamp}.json"
                filepath = os.path.join(output_dir, filename)
                
                try:
                    # 獲取完整的工作流數據
                    full_workflow = self._make_request('GET', f'/workflows/{workflow_id}')
                    workflow_data = full_workflow.get('data', {})
                    
                    # 保存到文件
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(workflow_data, f, indent=2, ensure_ascii=False)
                    
                    print(f"✅ 已備份: {workflow_name} -> {filename}")
                    backup_count += 1
                    
                except Exception as e:
                    print(f"❌ 備份失敗 {workflow_name}: {e}")
            
            print(f"\n🎉 備份完成! 成功備份 {backup_count} 個工作流到 {output_dir}")
            
        except Exception as e:
            print(f"❌ 備份過程失敗: {e}")

def main():
    parser = argparse.ArgumentParser(description='n8n 自動化部署管道')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # deploy 命令
    deploy_parser = subparsers.add_parser('deploy', help='部署單個工作流')
    deploy_parser.add_argument('json_file', help='工作流 JSON 文件路徑')
    deploy_parser.add_argument('--activate', action='store_true', help='部署後自動啟用')
    deploy_parser.add_argument('--validate', action='store_true', default=True, help='部署前驗證工作流')
    
    # batch-deploy 命令
    batch_parser = subparsers.add_parser('batch-deploy', help='批量部署目錄中的工作流')
    batch_parser.add_argument('directory', help='包含 JSON 文件的目錄路徑')
    batch_parser.add_argument('--activate', action='store_true', help='部署後自動啟用所有工作流')
    batch_parser.add_argument('--validate', action='store_true', default=True, help='部署前驗證所有工作流')
    
    # validate 命令
    validate_parser = subparsers.add_parser('validate', help='驗證工作流 JSON 文件')
    validate_parser.add_argument('json_file', help='要驗證的 JSON 文件路徑')
    
    # backup 命令
    backup_parser = subparsers.add_parser('backup', help='備份所有工作流')
    backup_parser.add_argument('--output-dir', default='n8n_backup', help='備份輸出目錄')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 初始化部署管道
    pipeline = N8nDeployPipeline()
    
    # 執行對應的命令
    try:
        if args.command == 'deploy':
            pipeline.deploy_single_workflow(args.json_file, activate=args.activate, validate=args.validate)
        elif args.command == 'batch-deploy':
            pipeline.batch_deploy(args.directory, activate=args.activate, validate=args.validate)
        elif args.command == 'validate':
            with open(args.json_file, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            is_valid, errors = pipeline.validate_workflow(workflow_data)
            if is_valid:
                print("✅ 工作流驗證通過")
            else:
                print("❌ 工作流驗證失敗:")
                for error in errors:
                    print(f"   - {error}")
                sys.exit(1)
        elif args.command == 'backup':
            pipeline.backup_workflows(args.output_dir)
    except KeyboardInterrupt:
        print("\n操作被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"執行命令時發生錯誤: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
