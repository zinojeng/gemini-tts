#!/usr/bin/env python3
"""
測試語音預覽功能的腳本
展示如何使用 generate_voice_preview 函數
"""

import os
from dotenv import load_dotenv
from gemini_tts_app import generate_voice_preview, save_wave_file

# 載入環境變數
load_dotenv()

def test_voice_previews():
    """測試不同語音的預覽功能"""
    
    # 從環境變數獲取 API 金鑰
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("錯誤：請設定 GEMINI_API_KEY 環境變數")
        return
    
    # 測試的語音列表
    test_voices = ["Zephyr", "Puck", "Kore", "Enceladus", "Laomedeia"]
    
    # 測試的語言列表
    test_languages = ["zh-TW", "en-US", "ja-JP"]
    
    print("開始生成語音預覽...")
    print("-" * 50)
    
    for voice in test_voices:
        print(f"\n測試語音：{voice}")
        
        for lang in test_languages:
            print(f"  語言：{lang}")
            
            try:
                # 生成預覽
                audio_data = generate_voice_preview(
                    api_key=api_key,
                    voice_name=voice,
                    language=lang,
                    model_name="gemini-2.5-flash-preview-tts"
                )
                
                if audio_data:
                    # 儲存預覽檔案
                    filename = f"preview_{voice}_{lang}.wav"
                    save_wave_file(filename, audio_data)
                    print(f"    ✅ 成功生成：{filename}")
                else:
                    print(f"    ❌ 生成失敗")
                    
            except Exception as e:
                print(f"    ❌ 錯誤：{str(e)}")
    
    print("\n" + "-" * 50)
    print("預覽生成完成！")

if __name__ == "__main__":
    test_voice_previews() 