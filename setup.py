#!/usr/bin/env python3
"""
Gemini TTS 設定助手
幫助使用者快速設定環境
"""

import os
import sys
import subprocess

def check_env_file():
    """檢查 .env 檔案是否存在"""
    if os.path.exists('.env'):
        print("✅ 找到 .env 檔案")
        return True
    else:
        print("❌ 未找到 .env 檔案")
        return False

def create_env_file():
    """建立 .env 檔案"""
    print("\n讓我們建立 .env 檔案...")
    api_key = input("請輸入您的 Gemini API 金鑰: ").strip()
    
    if not api_key:
        print("❌ API 金鑰不能為空")
        return False
    
    with open('.env', 'w') as f:
        f.write(f"# Gemini API Configuration\n")
        f.write(f"GEMINI_API_KEY={api_key}\n\n")
        f.write(f"# Optional: Default Model Selection\n")
        f.write(f"# GEMINI_TTS_MODEL=gemini-2.5-flash-preview-tts\n\n")
        f.write(f"# Optional: Default Voice\n")
        f.write(f"# GEMINI_DEFAULT_VOICE=Kore\n\n")
        f.write(f"# Optional: Default Language\n")
        f.write(f"# GEMINI_DEFAULT_LANGUAGE=zh-TW\n")
    
    print("✅ .env 檔案已建立")
    return True

def install_dependencies():
    """安裝相依套件"""
    print("\n正在安裝相依套件...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 相依套件安裝完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 安裝相依套件失敗")
        return False

def test_api_connection():
    """測試 API 連線"""
    print("\n測試 Gemini API 連線...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ 無法從 .env 讀取 API 金鑰")
            return False
        
        from google import genai
        client = genai.Client(api_key=api_key)
        
        # 簡單測試
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
        
        print("✅ API 連線成功！")
        return True
    except Exception as e:
        print(f"❌ API 連線失敗: {e}")
        return False

def main():
    print("🎙️ Gemini TTS 設定助手")
    print("=" * 40)
    
    # 檢查 Python 版本
    if sys.version_info < (3, 7):
        print("❌ 需要 Python 3.7 或更高版本")
        sys.exit(1)
    
    # 步驟 1: 檢查/建立 .env 檔案
    if not check_env_file():
        if input("\n是否要建立 .env 檔案？(y/n): ").lower() == 'y':
            if not create_env_file():
                sys.exit(1)
        else:
            print("請手動建立 .env 檔案並加入 GEMINI_API_KEY")
            sys.exit(1)
    
    # 步驟 2: 安裝相依套件
    if input("\n是否要安裝相依套件？(y/n): ").lower() == 'y':
        if not install_dependencies():
            print("請手動執行: pip install -r requirements.txt")
            sys.exit(1)
    
    # 步驟 3: 測試 API 連線
    if input("\n是否要測試 API 連線？(y/n): ").lower() == 'y':
        test_api_connection()
    
    print("\n✅ 設定完成！")
    print("\n接下來您可以：")
    print("1. 執行網頁介面: streamlit run gemini_tts_app.py")
    print("2. 使用命令列: python gemini_tts_cli.py --text '測試文字' -o output.wav")
    print("3. 執行測試腳本: python test_tts.py")

if __name__ == "__main__":
    main() 