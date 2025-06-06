#!/usr/bin/env python3
"""
Gemini TTS 命令列工具
支援單一講者和多講者文字轉語音
"""

import os
import sys
import wave
import argparse
import json
from google import genai
from google.genai import types
from typing import List, Dict
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 語音選項
VOICES = [
    "Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda", "Orus", "Aoede",
    "Callirrhoe", "Autonoe", "Enceladus", "Iapetus", "Umbriel", "Algieba",
    "Despina", "Erinome", "Algenib", "Rasalgethi", "Laomedeia", "Achernar",
    "Alnilam", "Schedar", "Gacrux", "Pulcherrima", "Achird", "Zubenelgenubi",
    "Vindemiatrix", "Sadachbia", "Sadaltager", "Sulafat"
]

def save_wave_file(filename: str, pcm_data: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2):
    """儲存 PCM 資料為 WAV 檔案"""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)

def single_speaker_tts(client, model: str, text: str, voice: str, output_file: str):
    """單一講者 TTS"""
    print(f"使用語音 {voice} 生成單一講者語音...")
    
    response = client.models.generate_content(
        model=model,
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice
                    )
                )
            )
        )
    )
    
    audio_data = response.candidates[0].content.parts[0].inline_data.data
    save_wave_file(output_file, audio_data)
    print(f"✅ 語音已儲存至：{output_file}")

def multi_speaker_tts(client, model: str, dialogue_file: str, output_file: str):
    """多講者 TTS"""
    # 讀取對話檔案
    with open(dialogue_file, 'r', encoding='utf-8') as f:
        dialogue_data = json.load(f)
    
    speakers = dialogue_data.get("speakers", [])
    content = dialogue_data.get("content", "")
    
    if len(speakers) < 2:
        raise ValueError("需要至少 2 個講者")
    
    print(f"生成多講者對話，講者：{[s['name'] for s in speakers]}")
    
    # 建立講者配置
    speaker_voice_configs = []
    for speaker in speakers:
        speaker_voice_configs.append(
            types.SpeakerVoiceConfig(
                speaker=speaker["name"],
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=speaker["voice"]
                    )
                )
            )
        )
    
    # 生成語音
    response = client.models.generate_content(
        model=model,
        contents=f"TTS 以下對話：\n{content}",
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=speaker_voice_configs
                )
            )
        )
    )
    
    audio_data = response.candidates[0].content.parts[0].inline_data.data
    save_wave_file(output_file, audio_data)
    print(f"✅ 語音已儲存至：{output_file}")

def generate_prompt(prompt_type: str, style: str = None) -> str:
    """生成提示範例"""
    prompts = {
        "podcast": "用熱情的播客主持人語氣說：歡迎各位聽眾！今天我們有一個超級精彩的話題要和大家分享。讓我們一起探索人工智慧的奇妙世界！",
        "audiobook": "用沉穩的敘事語氣朗讀：月光灑在寧靜的湖面上，微風輕拂著岸邊的蘆葦。遠處傳來夜鶯的歌聲，為這個夏夜增添了一絲詩意。",
        "education": "用清晰的教學語氣說：今天我們要學習的是機器學習的基本概念。機器學習是人工智慧的一個分支，它讓電腦能夠從資料中學習，而不需要明確的程式設計。",
        "customer": "用友善、專業的語氣說：您好！歡迎致電客戶服務中心。我是您的專屬客服代表，很高興為您提供協助。請問有什麼可以幫助您的嗎？"
    }
    
    prompt = prompts.get(prompt_type, "")
    if style:
        prompt = f"{style}地說：" + prompt.split("：", 1)[1] if "：" in prompt else prompt
    
    return prompt

def main():
    parser = argparse.ArgumentParser(description="Gemini TTS 命令列工具")
    
    # API 金鑰 - 可從環境變數讀取
    default_api_key = os.getenv("GEMINI_API_KEY")
    parser.add_argument("--api-key", 
                       default=default_api_key,
                       help="Gemini API 金鑰 (預設從 GEMINI_API_KEY 環境變數讀取)")
    parser.add_argument("--model", default="gemini-2.5-flash-preview-tts", 
                       choices=["gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts"],
                       help="TTS 模型")
    parser.add_argument("--mode", choices=["single", "multi"], default="single", help="TTS 模式")
    parser.add_argument("--output", "-o", default="output.wav", help="輸出檔案名稱")
    
    # 單一講者參數
    parser.add_argument("--text", "-t", help="要轉換的文字（單一講者模式）")
    parser.add_argument("--voice", "-v", choices=VOICES, default="Kore", help="語音選擇")
    parser.add_argument("--prompt-type", choices=["podcast", "audiobook", "education", "customer"],
                       help="使用預設提示類型")
    parser.add_argument("--style", help="語音風格（如：興奮的、平靜的、神秘的）")
    
    # 多講者參數
    parser.add_argument("--dialogue", "-d", help="對話 JSON 檔案路徑（多講者模式）")
    parser.add_argument("--create-dialogue-template", action="store_true", 
                       help="建立對話範本檔案")
    
    # 其他參數
    parser.add_argument("--list-voices", action="store_true", help="列出所有可用語音")
    
    args = parser.parse_args()
    
    # 列出語音選項
    if args.list_voices:
        print("可用語音選項：")
        for i, voice in enumerate(VOICES, 1):
            print(f"{i:2d}. {voice}")
        return
    
    # 建立對話範本
    if args.create_dialogue_template:
        template = {
            "speakers": [
                {"name": "主持人", "voice": "Kore"},
                {"name": "嘉賓", "voice": "Puck"}
            ],
            "content": """主持人：歡迎來到我們的節目！今天我們有一位特別的嘉賓。
嘉賓：謝謝邀請！很高興能來到這裡。
主持人：讓我們開始今天的話題吧。
嘉賓：好的，我已經準備好了！"""
        }
        
        with open("dialogue_template.json", "w", encoding="utf-8") as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        
        print("✅ 對話範本已建立：dialogue_template.json")
        return
    
    # 檢查 API 金鑰
    if not args.api_key:
        print("❌ 未提供 API 金鑰")
        print("💡 請使用 --api-key 參數或設定 GEMINI_API_KEY 環境變數")
        print("   範例：export GEMINI_API_KEY=your_api_key_here")
        return
    
    # 檢查 API 金鑰
    if not args.api_key:
        print("❌ 錯誤：未提供 API 金鑰")
        print("請使用以下方式之一提供 API 金鑰：")
        print("1. 使用 --api-key 參數")
        print("2. 設定環境變數 GEMINI_API_KEY")
        print("3. 在 .env 檔案中設定 GEMINI_API_KEY")
        return
    
    # 初始化客戶端
    try:
        client = genai.Client(api_key=args.api_key)
    except Exception as e:
        print(f"❌ 無法初始化 Gemini 客戶端：{e}")
        return
    
    # 執行 TTS
    try:
        if args.mode == "single":
            # 單一講者模式
            if args.prompt_type:
                text = generate_prompt(args.prompt_type, args.style)
            elif args.text:
                text = args.text
                if args.style:
                    text = f"{args.style}地說：{text}"
            else:
                print("❌ 請提供 --text 參數或使用 --prompt-type")
                return
            
            single_speaker_tts(client, args.model, text, args.voice, args.output)
            
        else:
            # 多講者模式
            if not args.dialogue:
                print("❌ 多講者模式需要提供 --dialogue 參數")
                print("💡 提示：使用 --create-dialogue-template 建立範本")
                return
            
            multi_speaker_tts(client, args.model, args.dialogue, args.output)
    
    except Exception as e:
        print(f"❌ 生成失敗：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 