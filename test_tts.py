#!/usr/bin/env python3
"""
Gemini TTS 快速測試腳本
"""

import os
from google import genai
from google.genai import types
import wave

def quick_test():
    # 從環境變數讀取 API 金鑰
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("請設定環境變數 GEMINI_API_KEY")
        return
    
    client = genai.Client(api_key=api_key)
    
    # 測試單一講者
    print("測試單一講者 TTS...")
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents="你好！歡迎使用 Gemini 文字轉語音功能。這是一個測試訊息。",
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Kore"
                    )
                )
            )
        )
    )
    
    # 儲存音訊
    audio_data = response.candidates[0].content.parts[0].inline_data.data
    with wave.open("test_single.wav", "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(audio_data)
    
    print("✅ 單一講者測試完成：test_single.wav")
    
    # 測試多講者
    print("\n測試多講者 TTS...")
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents="""TTS 以下對話：
A：你好！今天天氣真好。
B：是啊！很適合出去走走。
A：要不要一起去公園？
B：好主意！""",
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=[
                        types.SpeakerVoiceConfig(
                            speaker="A",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name="Kore"
                                )
                            )
                        ),
                        types.SpeakerVoiceConfig(
                            speaker="B",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name="Puck"
                                )
                            )
                        )
                    ]
                )
            )
        )
    )
    
    # 儲存音訊
    audio_data = response.candidates[0].content.parts[0].inline_data.data
    with wave.open("test_multi.wav", "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(audio_data)
    
    print("✅ 多講者測試完成：test_multi.wav")

if __name__ == "__main__":
    quick_test() 