import streamlit as st
import google.generativeai as genai
from google.generativeai import types
import os
from dotenv import load_dotenv
import re
import wave
from datetime import datetime
from typing import List, Tuple, Optional

# 載入環境變數
load_dotenv()

# TTS 模型配置
TTS_MODELS = {
    "gemini-2.0-flash-exp": "Gemini 2.0 Flash (實驗版)"
}

# 語音選項
VOICE_OPTIONS = {
    "Zephyr": "男聲 - 深沉穩重",
    "Puck": "男聲 - 活潑有趣",
    "Charon": "男聲 - 成熟專業",
    "Kore": "女聲 - 溫柔親切",
    "Fenrir": "男聲 - 有力威嚴",
    "Aoede": "女聲 - 優雅知性"
}

# 支援的語言
SUPPORTED_LANGUAGES = {
    "en-US": "英語 (美國)",
    "zh-TW": "中文 (台灣)",
    "zh-CN": "中文 (中國)",
    "ja-JP": "日語",
    "ko-KR": "韓語",
    "es-ES": "西班牙語",
    "fr-FR": "法語",
    "de-DE": "德語",
    "it-IT": "義大利語",
    "pt-BR": "葡萄牙語 (巴西)",
    "ru-RU": "俄語",
    "ar-XA": "阿拉伯語",
    "hi-IN": "印地語",
    "th-TH": "泰語",
    "vi-VN": "越南語"
}


def parse_srt_file(content: str) -> List[Tuple[str, str]]:
    """解析 SRT 檔案內容，返回 (講者, 文本) 的列表"""
    dialogues = []
    blocks = content.strip().split('\n\n')
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:  # SRT 格式至少有 3 行：序號、時間、文本
            # 跳過序號和時間行，獲取文本
            text_lines = lines[2:]
            text = ' '.join(text_lines)
            
            # 嘗試識別講者
            speaker = identify_speaker(text)
            dialogues.append((speaker, text))
    
    return dialogues


def parse_text_file(content: str) -> List[Tuple[str, str]]:
    """解析文本檔案，自動識別講者和對話"""
    dialogues = []
    lines = content.strip().split('\n')
    
    # 預設講者名稱
    speaker1_name = "講者1"
    speaker2_name = "講者2"
    current_speaker = None
    speaker_map = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 檢查是否有講者標記（如 "A:", "B:", "講者1:", "客服:" 等）
        speaker_match = re.match(r'^([^:：]+)[：:](.*)$', line)
        
        if speaker_match:
            speaker_label = speaker_match.group(1).strip()
            text = speaker_match.group(2).strip()
            
            # 映射講者標籤到講者1或講者2
            if speaker_label not in speaker_map:
                if len(speaker_map) == 0:
                    speaker_map[speaker_label] = speaker1_name
                elif len(speaker_map) == 1:
                    speaker_map[speaker_label] = speaker2_name
                else:
                    # 如果有超過兩個講者，循環使用
                    speaker_map[speaker_label] = speaker1_name if len(speaker_map) % 2 == 0 else speaker2_name
            
            current_speaker = speaker_map[speaker_label]
            if text:  # 如果同一行有文本
                dialogues.append((current_speaker, text))
        else:
            # 沒有講者標記的行
            if current_speaker:
                # 延續上一個講者
                dialogues.append((current_speaker, line))
            else:
                # 如果還沒有講者，預設為講者1
                current_speaker = speaker1_name
                dialogues.append((current_speaker, line))
    
    return dialogues, list(speaker_map.keys())


def identify_speaker(text: str) -> str:
    """從文本中識別講者，返回講者1或講者2"""
    # 這是一個簡單的實現，可以根據需要擴展
    # 例如：根據說話風格、內容等判斷
    return "講者1"  # 預設返回講者1


def save_wave_file(filename: str, pcm_data: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2):
    """將 PCM 資料儲存為 WAV 檔案"""
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)


def format_dialogues_for_tts(dialogues: List[Tuple[str, str]], speaker_names: List[str]) -> str:
    """將對話格式化為 TTS 輸入格式"""
    formatted_lines = []
    
    # 建立講者映射
    speaker_map = {}
    if len(speaker_names) >= 2:
        speaker_map["講者1"] = speaker_names[0]
        speaker_map["講者2"] = speaker_names[1]
    
    for speaker, text in dialogues:
        # 如果有自定義講者名稱，使用它
        display_speaker = speaker_map.get(speaker, speaker)
        formatted_lines.append(f"{display_speaker}：{text}")
    
    return '\n'.join(formatted_lines)


def main():
    st.title("📄 檔案上傳 TTS 轉換系統")
    st.markdown("上傳 SRT 或文字檔案，自動識別講者並轉換為語音")
    
    # 側邊欄設定
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # API 金鑰
        default_api_key = os.getenv("GEMINI_API_KEY", "")
        
        if default_api_key:
            st.success("✅ 已從環境變數載入 API 金鑰")
            api_key = st.text_input(
                "Gemini API 金鑰（選填）", 
                type="password",
                help="已從 .env 檔案載入 API 金鑰"
            )
            if not api_key:
                api_key = default_api_key
        else:
            api_key = st.text_input(
                "Gemini API 金鑰", 
                type="password",
                help="請輸入您的 Gemini API 金鑰"
            )
        
        # 模型選擇
        model_name = st.selectbox(
            "選擇 TTS 模型",
            options=list(TTS_MODELS.keys()),
            format_func=lambda x: TTS_MODELS[x]
        )
        
        # 語言選擇
        selected_language = st.selectbox(
            "選擇語言",
            options=list(SUPPORTED_LANGUAGES.keys()),
            format_func=lambda x: SUPPORTED_LANGUAGES[x],
            index=list(SUPPORTED_LANGUAGES.keys()).index("zh-TW")
        )
    
    # 主要內容區域
    st.header("📤 上傳檔案")
    
    # 檔案上傳
    uploaded_file = st.file_uploader(
        "選擇檔案",
        type=['srt', 'txt', 'text'],
        help="支援 SRT 字幕檔或純文字檔案"
    )
    
    if uploaded_file is not None:
        # 讀取檔案內容
        content = uploaded_file.read().decode('utf-8')
        
        # 顯示檔案資訊
        st.info(f"已上傳：{uploaded_file.name} ({len(content)} 字元)")
        
        # 解析檔案
        with st.spinner("正在解析檔案..."):
            if uploaded_file.name.endswith('.srt'):
                dialogues = parse_srt_file(content)
                original_speakers = []
            else:
                dialogues, original_speakers = parse_text_file(content)
        
        # 顯示解析結果
        st.header("📝 解析結果")
        
        # 講者設定
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("講者1 設定")
            speaker1_name = st.text_input(
                "講者1 名稱",
                value=original_speakers[0] if len(original_speakers) > 0 else "講者1"
            )
            speaker1_voice = st.selectbox(
                "講者1 語音",
                options=list(VOICE_OPTIONS.keys()),
                format_func=lambda x: f"{x} - {VOICE_OPTIONS[x]}",
                key="speaker1_voice"
            )
            speaker1_style = st.selectbox(
                "講者1 風格",
                ["無", "自訂", "興奮的", "平靜的", "友善的", "嚴肅的", "幽默的", "溫柔的"],
                key="speaker1_style"
            )
            if speaker1_style == "自訂":
                speaker1_custom_style = st.text_input("自訂風格", key="speaker1_custom")
                if speaker1_custom_style:
                    speaker1_style = speaker1_custom_style
        
        with col2:
            st.subheader("講者2 設定")
            speaker2_name = st.text_input(
                "講者2 名稱",
                value=original_speakers[1] if len(original_speakers) > 1 else "講者2"
            )
            speaker2_voice = st.selectbox(
                "講者2 語音",
                options=list(VOICE_OPTIONS.keys()),
                format_func=lambda x: f"{x} - {VOICE_OPTIONS[x]}",
                key="speaker2_voice",
                index=1  # 預設選擇不同的語音
            )
            speaker2_style = st.selectbox(
                "講者2 風格",
                ["無", "自訂", "興奮的", "平靜的", "友善的", "嚴肅的", "幽默的", "溫柔的"],
                key="speaker2_style"
            )
            if speaker2_style == "自訂":
                speaker2_custom_style = st.text_input("自訂風格", key="speaker2_custom")
                if speaker2_custom_style:
                    speaker2_style = speaker2_custom_style
        
        # 顯示對話預覽
        st.subheader("對話預覽")
        formatted_text = format_dialogues_for_tts(dialogues, [speaker1_name, speaker2_name])
        
        # 可編輯的文本區域
        edited_text = st.text_area(
            "編輯對話內容（可選）",
            value=formatted_text,
            height=300,
            help="您可以在此編輯對話內容後再生成語音"
        )
        
        # 進階設定
        with st.expander("進階設定"):
            sample_rate = st.selectbox("採樣率", [24000, 16000, 8000], index=0)
            channels = st.selectbox("聲道", [1, 2], index=0)
            output_format = st.selectbox("輸出格式", ["WAV", "PCM"], index=0)
        
        # 生成按鈕
        if st.button("🎤 生成語音", type="primary"):
            if not api_key:
                st.error("請輸入 Gemini API 金鑰")
            else:
                try:
                    with st.spinner("正在生成語音..."):
                        # 初始化 Gemini 客戶端
                        client = genai.Client(api_key=api_key)
                        
                        # 準備講者配置
                        speaker_voice_configs = [
                            types.SpeakerVoiceConfig(
                                speaker=speaker1_name,
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name=speaker1_voice
                                    )
                                )
                            ),
                            types.SpeakerVoiceConfig(
                                speaker=speaker2_name,
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name=speaker2_voice
                                    )
                                )
                            )
                        ]
                        
                        # 準備風格指令
                        style_instructions = []
                        if speaker1_style and speaker1_style != "無":
                            style_instructions.append(f"{speaker1_name}用{speaker1_style}語氣說話")
                        if speaker2_style and speaker2_style != "無":
                            style_instructions.append(f"{speaker2_name}用{speaker2_style}語氣說話")
                        
                        # 組合提示
                        if style_instructions:
                            prompt = "；".join(style_instructions) + "。\n\n" + edited_text
                        else:
                            prompt = f"TTS 以下對話：\n{edited_text}"
                        
                        # 配置
                        config = types.GenerateContentConfig(
                            response_modalities=["AUDIO"],
                            speech_config=types.SpeechConfig(
                                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                                    speaker_voice_configs=speaker_voice_configs
                                )
                            )
                        )
                        
                        # 生成語音
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=config
                        )
                        
                        # 檢查回應
                        if not response or not response.candidates:
                            st.error("API 未返回有效的回應")
                            return
                        
                        if not response.candidates[0].content or not response.candidates[0].content.parts:
                            st.error("API 回應中沒有音訊資料")
                            return
                        
                        # 獲取音訊資料
                        audio_data = response.candidates[0].content.parts[0].inline_data.data
                        
                        # 儲存檔案
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"file_tts_{timestamp}.wav"
                        
                        if output_format == "WAV":
                            save_wave_file(filename, audio_data, channels, sample_rate)
                        else:
                            filename = f"file_tts_{timestamp}.pcm"
                            with open(filename, "wb") as f:
                                f.write(audio_data)
                        
                        st.success(f"✅ 語音生成成功！")
                        
                        # 顯示音訊播放器
                        if output_format == "WAV":
                            st.audio(filename)
                        
                        # 下載按鈕
                        with open(filename, "rb") as f:
                            st.download_button(
                                label="📥 下載音訊檔案",
                                data=f.read(),
                                file_name=filename,
                                mime="audio/wav" if output_format == "WAV" else "audio/pcm"
                            )
                
                except Exception as e:
                    st.error(f"生成失敗：{str(e)}")
                    st.exception(e)


if __name__ == "__main__":
    main() 