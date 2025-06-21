#!/usr/bin/env python3
"""
環境變數載入工具
用於安全地載入 .env 文件中的環境變數
"""

import os
import sys

def load_env_file(env_file='.env'):
    """
    載入 .env 文件中的環境變數
    
    Args:
        env_file (str): .env 文件路徑，預設為 '.env'
    
    Returns:
        bool: 是否成功載入
    """
    if not os.path.exists(env_file):
        return False
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # 跳過空行和註釋
                if not line or line.startswith('#'):
                    continue
                
                # 檢查是否包含等號
                if '=' not in line:
                    print(f"⚠️  警告: .env 文件第 {line_num} 行格式不正確: {line}")
                    continue
                
                # 分割 key 和 value
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # 移除引號（如果有）
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # 設置環境變數
                os.environ[key] = value
        
        return True
        
    except Exception as e:
        print(f"❌ 載入 .env 文件時發生錯誤: {e}")
        return False

def get_required_env_vars():
    """
    獲取必要的環境變數
    
    Returns:
        dict: 環境變數字典，如果缺少必要變數則返回 None
    """
    required_vars = ['N8N_HOST_URL', 'N8N_API_KEY']
    env_vars = {}
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            env_vars[var] = value
        else:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少必要的環境變數: {', '.join(missing_vars)}")
        print("💡 請確保 .env 文件包含所有必要的變數")
        return None
    
    return env_vars

def validate_env_vars():
    """
    驗證環境變數的有效性
    
    Returns:
        bool: 環境變數是否有效
    """
    env_vars = get_required_env_vars()
    if not env_vars:
        return False
    
    # 驗證 URL 格式
    host_url = env_vars['N8N_HOST_URL']
    if not host_url.startswith(('http://', 'https://')):
        print(f"❌ N8N_HOST_URL 格式不正確: {host_url}")
        print("💡 URL 應該以 http:// 或 https:// 開頭")
        return False
    
    # 驗證 API Key 不為空
    api_key = env_vars['N8N_API_KEY']
    if len(api_key) < 10:
        print("❌ N8N_API_KEY 似乎太短，請檢查是否正確")
        return False
    
    return True

def setup_environment():
    """
    設置環境變數的完整流程
    
    Returns:
        tuple: (host_url, api_key) 或 (None, None) 如果設置失敗
    """
    print("🔧 正在設置環境變數...")
    
    # 嘗試載入 .env 文件
    if load_env_file():
        print("✅ 已從 .env 文件載入環境變數")
        
        # 驗證環境變數
        if validate_env_vars():
            env_vars = get_required_env_vars()
            return env_vars['N8N_HOST_URL'], env_vars['N8N_API_KEY']
        else:
            print("❌ 環境變數驗證失敗")
            return None, None
    else:
        print("⚠️  未找到 .env 文件")
        print("💡 請複製 .env.example 到 .env 並填入您的實際值")
        print("   cp .env.example .env")
        return None, None

def print_env_status():
    """
    顯示當前環境變數狀態
    """
    print("\n📊 環境變數狀態:")
    print("-" * 40)
    
    # 檢查 .env 文件
    if os.path.exists('.env'):
        print("✅ .env 文件: 存在")
    else:
        print("❌ .env 文件: 不存在")
    
    # 檢查必要的環境變數
    required_vars = ['N8N_HOST_URL', 'N8N_API_KEY']
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # 對於敏感資訊，只顯示前幾個字符
            if 'KEY' in var or 'TOKEN' in var or 'SECRET' in var:
                display_value = f"{value[:10]}..." if len(value) > 10 else value
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: 未設置")

if __name__ == '__main__':
    # 如果直接執行此腳本，顯示環境變數狀態
    print("🔍 環境變數檢查工具")
    print("=" * 50)
    
    # 載入 .env 文件
    if load_env_file():
        print("✅ .env 文件載入成功")
    else:
        print("❌ .env 文件載入失敗或不存在")
    
    # 顯示狀態
    print_env_status()
    
    # 驗證環境變數
    if validate_env_vars():
        print("\n🎉 所有環境變數設置正確!")
    else:
        print("\n❌ 環境變數設置有問題，請檢查 .env 文件")
        sys.exit(1)
