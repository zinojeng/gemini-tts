#!/usr/bin/env python3
"""
測試語音預覽功能
"""

import os
from dotenv import load_dotenv
from gemini_tts_app import generate_voice_preview, save_wave_file

# 載入環境變數
load_dotenv()

# 獲取 API 金鑰
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("請設定 GEMINI_API_KEY 環境變數")
    exit(1)

# 測試生成預覽
print("測試生成語音預覽...")

test_voices = ["Zephyr", "Puck", "Charon"]
test_language = "zh-TW"

for voice in test_voices:
    print(f"生成 {voice} 的預覽...")
    try:
        preview_audio = generate_voice_preview(
            api_key,
            voice,
            test_language
        )
        
        if preview_audio:
            filename = f"preview_{voice}_{test_language}.wav"
            save_wave_file(filename, preview_audio)
            print(f"✅ 成功生成並儲存：{filename}")
            
            # 檢查檔案大小
            file_size = os.path.getsize(filename)
            print(f"   檔案大小：{file_size:,} bytes")
        else:
            print(f"❌ 生成失敗：{voice}")
            
    except Exception as e:
        print(f"❌ 錯誤：{e}")

print("\n測試完成！")

# 列出所有生成的預覽檔案
print("\n已生成的預覽檔案：")
for file in os.listdir("."):
    if file.startswith("preview_") and file.endswith(".wav"):
        print(f"  - {file}") 