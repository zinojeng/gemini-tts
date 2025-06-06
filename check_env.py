#!/usr/bin/env python3
"""
環境檢查腳本
檢查 Gemini TTS 的環境設定是否正確
"""

import os
import sys
from dotenv import load_dotenv

print("🔍 Gemini TTS 環境檢查")
print("=" * 40)

# 載入環境變數
load_dotenv()

# 檢查 Python 版本
print(f"\n✅ Python 版本: {sys.version}")

# 檢查 .env 檔案
if os.path.exists('.env'):
    print("✅ 找到 .env 檔案")
else:
    print("❌ 未找到 .env 檔案")

# 檢查 API 金鑰
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print(f"✅ API 金鑰已設定 (長度: {len(api_key)} 字元)")
    print(f"   前 10 個字元: {api_key[:10]}...")
    
    # 檢查是否有多餘的引號
    if api_key.startswith("'") or api_key.startswith('"'):
        print("⚠️  警告: API 金鑰包含引號，這可能會導致問題")
else:
    print("❌ 未找到 GEMINI_API_KEY 環境變數")

# 檢查套件安裝
print("\n檢查套件安裝:")
try:
    import google.genai
    print("✅ google-genai 已安裝")
except ImportError:
    print("❌ google-genai 未安裝")

try:
    import streamlit
    print("✅ streamlit 已安裝")
except ImportError:
    print("❌ streamlit 未安裝")

try:
    import dotenv
    print("✅ python-dotenv 已安裝")
except ImportError:
    print("❌ python-dotenv 未安裝")

# 測試 API 連線
if api_key and 'google.genai' in sys.modules:
    print("\n測試 API 連線...")
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        print("✅ API 客戶端初始化成功")
        
        # 簡單測試
        print("執行簡單測試...")
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents="測試",
            config={
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": "Kore"
                        }
                    }
                }
            }
        )
        print("✅ API 測試成功！TTS 功能正常")
    except Exception as e:
        print(f"❌ API 測試失敗: {e}")

print("\n" + "=" * 40)
print("檢查完成！") 