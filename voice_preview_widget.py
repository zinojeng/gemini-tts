"""
語音預覽小工具模組
提供整合語音選擇和預覽功能的 Streamlit 元件
"""

import streamlit as st
import os
from typing import List, Callable, Dict, Tuple


def _play_preview_with_placeholder(
    voice_name: str,
    language: str,
    api_key: str,
    model_name: str,
    generate_func: Callable,
    save_func: Callable,
    key_suffix: str
) -> None:
    """使用 placeholder 播放預覽，確保音訊播放器在同一位置"""
    # 創建一個 placeholder 用於音訊播放器
    audio_placeholder = st.empty()
    
    # 檢查預先生成的檔案
    preview_dir = "voice_previews"
    pregenerated_file = f"{preview_dir}/preview_{voice_name}_{language}.wav"
    
    # 優先使用預先生成的檔案
    if os.path.exists(pregenerated_file):
        # 直接播放預先生成的檔案
        with open(pregenerated_file, 'rb') as f:
            audio_data = f.read()
        audio_placeholder.audio(audio_data, format='audio/wav')
        return
    
    # 如果沒有預先生成的檔案，則使用原有的快取機制
    preview_key = f"{voice_name}_{language}"
    cache_file = f"preview_{preview_key}.wav"
    
    # 檢查記憶體快取
    if 'voice_previews' not in st.session_state:
        st.session_state.voice_previews = {}
    
    # 如果已有快取，直接播放
    if preview_key in st.session_state.voice_previews:
        audio_placeholder.audio(
            st.session_state.voice_previews[preview_key],
            format='audio/wav'
        )
        return
    
    # 檢查檔案快取
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            audio_data = f.read()
        st.session_state.voice_previews[preview_key] = audio_data
        audio_placeholder.audio(audio_data, format='audio/wav')
        return
    
    # 生成預覽（不顯示任何提示）
    audio_data = generate_func(
        api_key, voice_name, language, model_name
    )
    
    if audio_data:
        # 儲存到檔案
        save_func(cache_file, audio_data)
        # 儲存到記憶體快取
        st.session_state.voice_previews[preview_key] = audio_data
        # 在 placeholder 中播放音訊
        audio_placeholder.audio(audio_data, format='audio/wav')


def voice_selector_with_preview(
    label: str,
    voice_options: List[str],
    voice_descriptions: Dict[str, str],
    api_key: str,
    language: str,
    model_name: str,
    key_suffix: str,
    generate_func: Callable,
    save_func: Callable,
    default_index: int = 0
) -> str:
    """創建帶有預覽功能的語音選擇器
    
    Args:
        label: 選擇器標籤
        voice_options: 語音選項列表
        voice_descriptions: 語音描述字典
        api_key: API 金鑰
        language: 語言代碼
        model_name: 模型名稱
        key_suffix: 用於區分不同選擇器的後綴
        generate_func: 生成語音預覽的函數
        save_func: 儲存音訊檔案的函數
        default_index: 預設選項索引
    
    Returns:
        選擇的語音名稱
    """
    col1, col2 = st.columns([5, 1])
    
    with col1:
        voice_name = st.selectbox(
            label,
            options=voice_options,
            format_func=lambda x: f"{x} - {voice_descriptions[x]}",
            index=default_index,
            key=f"voice_select_{key_suffix}"
        )
    
    with col2:
        # 使用更小的按鈕
        st.markdown("<div style='margin-top: 28px;'></div>",
                    unsafe_allow_html=True)
        if st.button("▶️", key=f"preview_{key_suffix}",
                     help=f"預覽 {voice_name} 的聲音"):
            _play_preview_with_placeholder(
                voice_name, language, api_key, model_name,
                generate_func, save_func, key_suffix
            )
    
    return voice_name


def multi_speaker_voice_selector(
    num_speakers: int,
    api_key: str,
    language: str,
    model_name: str,
    voice_options: Dict[str, str],
    generate_func: Callable,
    save_func: Callable
) -> Tuple[List[str], List[str], List[str]]:
    """多講者語音選擇器
    
    Returns:
        (speakers, voice_configs, speaker_styles) 元組
    """
    speakers = []
    voice_configs = []
    speaker_styles = []
    
    # 風格選項
    style_options = ["無", "自訂", "興奮的", "平靜的", "嚴肅的", "友善的",
                     "神秘的", "幽默的", "溫柔的", "活潑的", "專業的"]
    
    for i in range(num_speakers):
        st.markdown(f"#### 講者 {i+1}")
        
        # 講者名稱
        speaker_name = st.text_input(
            "講者名稱",
            value=f"講者{i+1}",
            key=f"speaker_name_{i}"
        )
        speakers.append(speaker_name)
        
        # 語音選擇（帶預覽）
        voice_name = voice_selector_with_preview(
            "選擇語音",
            list(voice_options.keys()),
            voice_options,
            api_key,
            language,
            model_name,
            f"speaker_{i}",
            generate_func,
            save_func,
            default_index=i % len(voice_options)
        )
        voice_configs.append(voice_name)
        
        # 風格選擇
        style_choice = st.selectbox(
            "風格設定",
            options=style_options,
            key=f"style_{i}"
        )
        
        if style_choice == "自訂":
            custom_style = st.text_input(
                "輸入自訂風格",
                placeholder="例如：溫柔地、激動地",
                key=f"custom_style_{i}"
            )
            if custom_style:
                speaker_styles.append(custom_style)
            else:
                speaker_styles.append("")
        elif style_choice != "無":
            speaker_styles.append(style_choice)
        else:
            speaker_styles.append("")
    
    return speakers, voice_configs, speaker_styles


def create_preview_sidebar():
    """
    在側邊欄創建預覽區域
    """
    with st.sidebar:
        st.markdown("### 🎵 語音預覽")
        st.markdown("點擊語音選擇旁的 ▶️ 按鈕來預覽語音效果")
        
        # 預覽歷史（可選）
        if 'preview_history' not in st.session_state:
            st.session_state.preview_history = []
        
        if st.session_state.preview_history:
            st.markdown("#### 最近預覽")
            for preview in st.session_state.preview_history[-3:]:  # 顯示最近3個
                st.text(f"• {preview}") 