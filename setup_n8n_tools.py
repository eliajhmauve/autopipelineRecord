#!/usr/bin/env python3
"""
n8n 工具快速設置腳本
自動設置環境變數並測試連接

Usage:
    python3 setup_n8n_tools.py
"""

import os
import sys
import subprocess
import requests

def check_python_version():
    """檢查 Python 版本"""
    if sys.version_info < (3, 7):
        print("❌ 需要 Python 3.7 或更高版本")
        print(f"當前版本: {sys.version}")
        return False
    print(f"✅ Python 版本: {sys.version.split()[0]}")
    return True

def install_requirements():
    """安裝必要的 Python 套件"""
    required_packages = ['requests']
    
    print("📦 檢查必要套件...")
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安裝")
        except ImportError:
            print(f"📥 正在安裝 {package}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} 安裝成功")
            except subprocess.CalledProcessError:
                print(f"❌ {package} 安裝失敗")
                return False
    
    return True

def setup_environment():
    """設置環境變數"""
    print("\n🔧 設置環境變數...")
    
    # 從 CLAUDE.md 讀取預設值
    default_host = "https://gmgm.zeabur.app"
    default_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkOWRhNjcyNS1kMTJjLTQzYzItOGJkOC04Y2Y5NjNjYzA4NmMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzUwNDg4MjI2fQ.P-b1xY34XA4EjC2NMNMdquYc_gKXJYGRGsBtNkQy3Oo"
    
    # 檢查現有環境變數
    current_host = os.getenv('N8N_HOST_URL')
    current_api_key = os.getenv('N8N_API_KEY')
    
    if current_host and current_api_key:
        print(f"✅ 環境變數已設置:")
        print(f"   N8N_HOST_URL: {current_host}")
        print(f"   N8N_API_KEY: {current_api_key[:20]}...")
        return current_host, current_api_key
    
    # 設置環境變數
    host_url = input(f"請輸入 n8n 主機 URL (預設: {default_host}): ").strip() or default_host
    api_key = input(f"請輸入 n8n API Key (預設: 使用 CLAUDE.md 中的 key): ").strip() or default_api_key
    
    # 設置到當前 session
    os.environ['N8N_HOST_URL'] = host_url
    os.environ['N8N_API_KEY'] = api_key
    
    print("✅ 環境變數已設置到當前 session")
    print("\n💡 要永久設置環境變數，請將以下命令添加到您的 shell 配置文件 (~/.bashrc, ~/.zshrc 等):")
    print(f'export N8N_HOST_URL="{host_url}"')
    print(f'export N8N_API_KEY="{api_key}"')
    
    return host_url, api_key

def test_connection(host_url, api_key):
    """測試 n8n API 連接"""
    print("\n🔍 測試 n8n API 連接...")
    
    headers = {
        'X-N8N-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{host_url.rstrip('/')}/api/v1/workflows", headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        workflow_count = len(data.get('data', []))
        
        print("✅ n8n API 連接成功!")
        print(f"📊 可訪問的工作流數量: {workflow_count}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ n8n API 連接失敗: {e}")
        print("\n🔧 請檢查:")
        print("1. n8n 實例是否正在運行")
        print("2. API Key 是否正確")
        print("3. 網路連接是否正常")
        return False

def create_shell_aliases():
    """創建便捷的 shell 別名"""
    print("\n🔗 建議的 shell 別名:")
    print("# 添加到您的 ~/.bashrc 或 ~/.zshrc 文件中")
    print("alias n8n-list='python3 n8n_integration.py list-workflows'")
    print("alias n8n-test='python3 claude_n8n_cli.py test'")
    print("alias n8n-deploy='python3 n8n_deploy_pipeline.py deploy'")
    print("alias n8n-backup='python3 n8n_deploy_pipeline.py backup'")

def show_usage_examples():
    """顯示使用範例"""
    print("\n📚 使用範例:")
    print("\n1. 基本工作流管理:")
    print("   python3 n8n_integration.py list-workflows")
    print("   python3 n8n_integration.py get-workflow <WORKFLOW_ID>")
    print("   python3 n8n_integration.py execute <WORKFLOW_ID>")
    print("   python3 n8n_integration.py create-sample")
    
    print("\n2. 進階功能:")
    print("   python3 claude_n8n_cli.py test")
    print("   python3 claude_n8n_cli.py list --active")
    print("   python3 claude_n8n_cli.py activate <WORKFLOW_ID>")
    print("   python3 claude_n8n_cli.py executions --workflow-id <ID> --limit 10")
    print("   python3 claude_n8n_cli.py webhook <WORKFLOW_ID>")
    
    print("\n3. 自動化部署:")
    print("   python3 n8n_deploy_pipeline.py deploy Line___AI______.json --activate")
    print("   python3 n8n_deploy_pipeline.py batch-deploy ./workflows --activate")
    print("   python3 n8n_deploy_pipeline.py backup --output-dir ./backup")
    print("   python3 n8n_deploy_pipeline.py validate Line___AI______.json")

def main():
    print("🚀 n8n 工具快速設置")
    print("=" * 50)
    
    # 檢查 Python 版本
    if not check_python_version():
        sys.exit(1)
    
    # 安裝必要套件
    if not install_requirements():
        sys.exit(1)
    
    # 設置環境變數
    host_url, api_key = setup_environment()
    
    # 測試連接
    if test_connection(host_url, api_key):
        print("\n🎉 設置完成! n8n 工具已準備就緒")
        
        # 顯示使用範例
        show_usage_examples()
        
        # 顯示 shell 別名建議
        create_shell_aliases()
        
        print("\n💡 提示:")
        print("1. 確保將環境變數添加到您的 shell 配置文件中")
        print("2. 重新啟動終端或執行 'source ~/.bashrc' 來載入環境變數")
        print("3. 使用 'python3 claude_n8n_cli.py test' 來驗證設置")
        
    else:
        print("\n❌ 設置未完成，請檢查連接問題後重試")
        sys.exit(1)

if __name__ == '__main__':
    main()
