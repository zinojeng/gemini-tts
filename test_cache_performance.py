"""
測試語音預覽快取性能
"""

import os
import time
from dotenv import load_dotenv
from gemini_tts_app import generate_voice_preview, save_wave_file

# 載入環境變數
load_dotenv()

# 獲取 API 金鑰
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("請設定 GEMINI_API_KEY 環境變數")
    exit(1)

# 測試語音
test_voice = "Zephyr"
test_language = "zh-TW"
preview_filename = f"preview_{test_voice}_{test_language}.wav"

print("=== 語音預覽快取性能測試 ===\n")

# 測試 1：首次生成（無快取）
if os.path.exists(preview_filename):
    os.remove(preview_filename)
    print(f"已刪除現有檔案：{preview_filename}")

print("測試 1：首次生成（無快取）")
start_time = time.time()
try:
    preview_audio = generate_voice_preview(api_key, test_voice, test_language)
    if preview_audio:
        save_wave_file(preview_filename, preview_audio)
        elapsed_time = time.time() - start_time
        print(f"✅ 生成成功，耗時：{elapsed_time:.2f} 秒")
        print(f"   檔案大小：{os.path.getsize(preview_filename):,} bytes")
except Exception as e:
    print(f"❌ 錯誤：{e}")

print("\n" + "-" * 40 + "\n")

# 測試 2：從檔案系統載入（有快取）
print("測試 2：從檔案系統載入（有快取）")
start_time = time.time()
if os.path.exists(preview_filename):
    elapsed_time = time.time() - start_time
    print(f"✅ 檔案存在，載入耗時：{elapsed_time:.4f} 秒")
    print(f"   檔案路徑：{preview_filename}")
else:
    print("❌ 檔案不存在")

print("\n" + "-" * 40 + "\n")

# 列出所有預覽檔案
print("目前的預覽檔案：")
preview_files = [f for f in os.listdir(".") 
                 if f.startswith("preview_") and f.endswith(".wav")]
for file in sorted(preview_files):
    size = os.path.getsize(file)
    print(f"  - {file} ({size:,} bytes)")

print(f"\n總計：{len(preview_files)} 個預覽檔案") 