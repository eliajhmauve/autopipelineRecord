#!/usr/bin/env python3
"""
安全檢查工具
檢查代碼庫中是否有硬編碼的敏感資訊
"""

import os
import re
import sys
import glob
from typing import List, Tuple, Dict

class SecurityChecker:
    def __init__(self):
        self.sensitive_patterns = {
            'API Keys': [
                r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',  # JWT tokens
                r'sk-[A-Za-z0-9]{48}',  # OpenAI API keys
                r'pk_[A-Za-z0-9]{24}',  # Stripe public keys
                r'rk_[A-Za-z0-9]{24}',  # Stripe restricted keys
                r'AKIA[0-9A-Z]{16}',    # AWS Access Key ID
            ],
            'Tokens': [
                r'ghp_[A-Za-z0-9]{36}',  # GitHub Personal Access Token
                r'gho_[A-Za-z0-9]{36}',  # GitHub OAuth Token
                r'ghu_[A-Za-z0-9]{36}',  # GitHub User Token
                r'ghs_[A-Za-z0-9]{36}',  # GitHub Server Token
                r'ghr_[A-Za-z0-9]{36}',  # GitHub Refresh Token
            ],
            'LINE Bot': [
                r'[A-Za-z0-9+/]{86}=',  # LINE Channel Access Token pattern
                r'[a-f0-9]{32}',        # LINE Channel Secret pattern (32 hex chars)
                r'U[a-f0-9]{32}',       # LINE User ID pattern
                r'@[a-z0-9]{8}',        # LINE Bot Basic ID pattern
            ],
            'URLs with credentials': [
                r'https?://[^:]+:[^@]+@[^/]+',  # URLs with username:password
            ],
            'Common secrets': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
                r'key\s*=\s*["\'][^"\']+["\']',
            ]
        }
        
        self.exclude_patterns = [
            r'your_.*_here',
            r'your_actual_.*_here',
            r'example_.*',
            r'placeholder_.*',
            r'dummy_.*',
            r'test_.*',
            r'fake_.*',
            r'\{.*\}',  # 排除模板變數如 {api_key}
            r'f["\'].*\{.*\}.*["\']',  # 排除 f-string
        ]
        
        self.exclude_files = {
            '.env.example',
            'security_check.py',
            '.gitignore',
            'SECURITY.md',
        }
        
        self.exclude_dirs = {
            '.git',
            '__pycache__',
            'node_modules',
            '.vscode',
            '.idea',
        }
    
    def is_excluded_content(self, content: str) -> bool:
        """檢查內容是否為排除的範例內容"""
        for pattern in self.exclude_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def scan_file(self, file_path: str) -> List[Tuple[str, str, int, str]]:
        """
        掃描單個文件
        返回: [(category, pattern, line_number, matched_content), ...]
        """
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                for category, patterns in self.sensitive_patterns.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            matched_content = match.group()
                            
                            # 跳過排除的內容
                            if self.is_excluded_content(matched_content):
                                continue
                            
                            findings.append((category, pattern, line_num, matched_content))
        
        except Exception as e:
            print(f"⚠️  無法讀取文件 {file_path}: {e}")
        
        return findings
    
    def scan_directory(self, directory: str = '.') -> Dict[str, List[Tuple]]:
        """掃描整個目錄"""
        all_findings = {}
        
        for root, dirs, files in os.walk(directory):
            # 排除特定目錄
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                
                # 排除特定文件
                if file in self.exclude_files:
                    continue
                
                # 只掃描文本文件
                if self.is_text_file(file_path):
                    findings = self.scan_file(file_path)
                    if findings:
                        all_findings[relative_path] = findings
        
        return all_findings
    
    def is_text_file(self, file_path: str) -> bool:
        """檢查是否為文本文件"""
        text_extensions = {
            '.py', '.js', '.ts', '.json', '.md', '.txt', '.yml', '.yaml',
            '.env', '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat',
            '.html', '.css', '.xml', '.sql', '.conf', '.ini', '.cfg'
        }
        
        _, ext = os.path.splitext(file_path)
        return ext.lower() in text_extensions or os.path.basename(file_path).startswith('.env')
    
    def generate_report(self, findings: Dict[str, List[Tuple]]) -> None:
        """生成安全檢查報告"""
        if not findings:
            print("🎉 安全檢查通過！沒有發現硬編碼的敏感資訊。")
            return
        
        print("🚨 安全檢查發現問題！")
        print("=" * 60)
        
        total_issues = sum(len(file_findings) for file_findings in findings.values())
        print(f"總共發現 {total_issues} 個潛在的安全問題在 {len(findings)} 個文件中：\n")
        
        for file_path, file_findings in findings.items():
            print(f"📁 文件: {file_path}")
            print("-" * 40)
            
            for category, pattern, line_num, content in file_findings:
                print(f"  ⚠️  第 {line_num} 行 [{category}]")
                print(f"     模式: {pattern}")
                print(f"     內容: {content[:50]}{'...' if len(content) > 50 else ''}")
                print()
        
        print("🔧 建議修復措施:")
        print("1. 將敏感資訊移至 .env 文件")
        print("2. 更新代碼使用環境變數")
        print("3. 確保 .env 文件在 .gitignore 中")
        print("4. 檢查 Git 歷史記錄是否包含敏感資訊")
    
    def check_env_file_security(self) -> None:
        """檢查 .env 文件安全性"""
        print("\n🔍 檢查 .env 文件安全性...")
        
        if not os.path.exists('.env'):
            print("❌ .env 文件不存在")
            return
        
        # 檢查文件權限
        stat_info = os.stat('.env')
        permissions = oct(stat_info.st_mode)[-3:]
        
        if permissions != '600':
            print(f"⚠️  .env 文件權限不安全: {permissions}")
            print("   建議執行: chmod 600 .env")
        else:
            print("✅ .env 文件權限正確 (600)")
        
        # 檢查是否在 .gitignore 中
        if os.path.exists('.gitignore'):
            with open('.gitignore', 'r') as f:
                gitignore_content = f.read()
            
            if '.env' in gitignore_content:
                print("✅ .env 文件已在 .gitignore 中")
            else:
                print("❌ .env 文件未在 .gitignore 中")
        else:
            print("❌ .gitignore 文件不存在")

def main():
    print("🔐 代碼庫安全檢查工具")
    print("=" * 50)
    
    checker = SecurityChecker()
    
    # 掃描目錄
    print("🔍 正在掃描代碼庫...")
    findings = checker.scan_directory()
    
    # 生成報告
    checker.generate_report(findings)
    
    # 檢查 .env 文件安全性
    checker.check_env_file_security()
    
    # 返回適當的退出碼
    if findings:
        sys.exit(1)
    else:
        print("\n✅ 安全檢查完成，沒有發現問題！")
        sys.exit(0)

if __name__ == '__main__':
    main()
