#!/usr/bin/env python3
"""
批量生成所有語音預覽檔案的腳本
可以在部署前運行此腳本，預先生成所有語音的預覽檔案
"""

import os
import wave
from google import genai
from google.genai import types
from dotenv import load_dotenv
import time

# 載入環境變數
load_dotenv()

# 語音選項列表
VOICE_OPTIONS = [
    "Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda", "Orus", "Aoede",
    "Callirrhoe", "Autonoe", "Enceladus", "Iapetus", "Umbriel", "Algieba",
    "Despina", "Erinome", "Algenib", "Rasalgethi", "Laomedeia", "Achernar",
    "Alnilam", "Schedar", "Gacrux", "Pulcherrima", "Achird", "Zubenelgenubi",
    "Vindemiatrix", "Sadachbia", "Sadaltager", "Sulafat"
]

# 支援的語言（選擇主要語言）
LANGUAGES = [
    "zh-TW",  # 中文繁體
    "zh-CN",  # 中文簡體
    "en-US",  # 英語
    "ja-JP",  # 日語
    "ko-KR",  # 韓語
]

# 預覽文本
PREVIEW_TEXTS = {
    "zh-TW": lambda voice: f"您好，我是 {voice}。這是我的聲音預覽，希望您喜歡。",
    "zh-CN": lambda voice: f"您好，我是 {voice}。这是我的声音预览，希望您喜欢。",
    "en-US": lambda voice: f"Hello, I am {voice}. This is a preview of my voice. I hope you like it.",
    "ja-JP": lambda voice: f"こんにちは、私は{voice}です。これは私の声のプレビューです。",
    "ko-KR": lambda voice: f"안녕하세요, 저는 {voice}입니다. 제 목소리 미리듣기입니다.",
}


def save_wave_file(filename: str, pcm_data: bytes, channels: int = 1,
                   rate: int = 24000, sample_width: int = 2):
    """儲存 PCM 資料為 WAV 檔案"""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)


def generate_voice_preview(api_key: str, voice_name: str, language: str,
                          model_name: str = "gemini-2.5-flash-preview-tts") -> bytes:
    """生成語音預覽"""
    preview_text = PREVIEW_TEXTS.get(language, PREVIEW_TEXTS["en-US"])(voice_name)
    
    try:
        client = genai.Client(api_key=api_key)
        
        config = types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name
                    )
                )
            )
        )
        
        response = client.models.generate_content(
            model=model_name,
            contents=preview_text,
            config=config
        )
        
        if response and response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            return response.candidates[0].content.parts[0].inline_data.data
        else:
            return None
            
    except Exception as e:
        print(f"生成 {voice_name} ({language}) 失敗：{str(e)}")
        return None


def main():
    # 獲取 API 金鑰
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("錯誤：請在 .env 檔案中設定 GEMINI_API_KEY")
        return
    
    # 創建預覽檔案目錄
    preview_dir = "voice_previews"
    if not os.path.exists(preview_dir):
        os.makedirs(preview_dir)
    
    total_files = len(VOICE_OPTIONS) * len(LANGUAGES)
    generated = 0
    skipped = 0
    failed = 0
    
    print(f"開始生成語音預覽檔案...")
    print(f"總共需要生成：{total_files} 個檔案")
    print(f"語音數量：{len(VOICE_OPTIONS)}")
    print(f"語言數量：{len(LANGUAGES)}")
    print("-" * 50)
    
    start_time = time.time()
    
    for voice in VOICE_OPTIONS:
        for language in LANGUAGES:
            filename = f"{preview_dir}/preview_{voice}_{language}.wav"
            
            # 檢查檔案是否已存在
            if os.path.exists(filename):
                print(f"✓ 跳過（已存在）：{voice} - {language}")
                skipped += 1
                continue
            
            print(f"生成中：{voice} - {language}...", end="", flush=True)
            
            # 生成預覽
            audio_data = generate_voice_preview(api_key, voice, language)
            
            if audio_data:
                # 儲存檔案
                save_wave_file(filename, audio_data)
                print(f" ✓ 完成")
                generated += 1
            else:
                print(f" ✗ 失敗")
                failed += 1
            
            # 避免 API 速率限制
            time.sleep(0.5)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print("-" * 50)
    print(f"生成完成！")
    print(f"總耗時：{elapsed_time:.1f} 秒")
    print(f"成功生成：{generated} 個檔案")
    print(f"跳過（已存在）：{skipped} 個檔案")
    print(f"生成失敗：{failed} 個檔案")
    print(f"預覽檔案儲存在：{os.path.abspath(preview_dir)}")


if __name__ == "__main__":
    main() 