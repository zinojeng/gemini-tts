#!/usr/bin/env python3
"""
測試預先生成的語音預覽功能
生成幾個語音預覽檔案到 voice_previews 目錄
"""

import os
import wave
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 測試用的語音和語言
TEST_VOICES = ["Zephyr", "Puck", "Charon"]
TEST_LANGUAGES = ["zh-TW", "en-US"]


def save_wave_file(filename: str, pcm_data: bytes, channels: int = 1,
                   rate: int = 24000, sample_width: int = 2):
    """儲存 PCM 資料為 WAV 檔案"""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)


def generate_voice_preview(api_key: str, voice_name: str, language: str,
                          model_name: str = "gemini-2.5-flash-preview-tts"):
    """生成語音預覽"""
    # 預覽文本
    preview_texts = {
        "zh-TW": f"您好，我是 {voice_name}。這是我的聲音預覽，希望您喜歡。",
        "en-US": f"Hello, I am {voice_name}. This is a preview of my voice."
    }
    
    preview_text = preview_texts.get(language, preview_texts["en-US"])
    
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
        
        if (response and response.candidates and 
            response.candidates[0].content and 
            response.candidates[0].content.parts):
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
    
    print("開始生成測試用的語音預覽檔案...")
    print(f"語音：{', '.join(TEST_VOICES)}")
    print(f"語言：{', '.join(TEST_LANGUAGES)}")
    print("-" * 50)
    
    generated = 0
    failed = 0
    
    for voice in TEST_VOICES:
        for language in TEST_LANGUAGES:
            filename = f"{preview_dir}/preview_{voice}_{language}.wav"
            
            # 檢查檔案是否已存在
            if os.path.exists(filename):
                print(f"✓ 跳過（已存在）：{voice} - {language}")
                continue
            
            print(f"生成中：{voice} - {language}...", end="", flush=True)
            
            # 生成預覽
            audio_data = generate_voice_preview(api_key, voice, language)
            
            if audio_data:
                # 儲存檔案
                save_wave_file(filename, audio_data)
                print(" ✓ 完成")
                generated += 1
            else:
                print(" ✗ 失敗")
                failed += 1
    
    print("-" * 50)
    print(f"生成完成！")
    print(f"成功生成：{generated} 個檔案")
    print(f"生成失敗：{failed} 個檔案")
    print(f"預覽檔案儲存在：{os.path.abspath(preview_dir)}")


if __name__ == "__main__":
    main() 