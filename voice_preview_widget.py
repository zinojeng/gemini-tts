"""
語音預覽小工具模組
提供帶有內嵌播放按鈕的語音選擇功能
"""

import streamlit as st
from typing import List, Dict, Callable
import os


def initialize_voice_previews(
    voice_options: List[str],
    api_key: str,
    selected_language: str,
    model_name: str,
    generate_preview_func: Callable,
    save_wave_func: Callable
):
    """
    初始化並預先生成所有語音的預覽
    
    Args:
        voice_options: 語音選項列表
        api_key: Gemini API 金鑰
        selected_language: 選擇的語言
        model_name: TTS 模型名稱
        generate_preview_func: 生成預覽的函數
        save_wave_func: 儲存音訊的函數
    """
    if not api_key:
        return
    
    # 使用 session_state 來追蹤已生成的預覽
    if 'voice_previews' not in st.session_state:
        st.session_state.voice_previews = {}
    
    # 檢查語言是否改變，如果改變則清空快取
    if 'preview_language' not in st.session_state:
        st.session_state.preview_language = selected_language
    elif st.session_state.preview_language != selected_language:
        st.session_state.preview_language = selected_language
        st.session_state.voice_previews = {}
    
    # 預先生成所有語音的預覽（只生成尚未生成的）
    for voice in voice_options:
        preview_key = f"{voice}_{selected_language}"
        if preview_key not in st.session_state.voice_previews:
            preview_filename = f"preview_{voice}_{selected_language}.wav"
            
            # 檢查檔案是否已存在
            if os.path.exists(preview_filename):
                st.session_state.voice_previews[preview_key] = preview_filename
            else:
                # 生成預覽
                try:
                    preview_audio = generate_preview_func(
                        api_key,
                        voice,
                        selected_language,
                        model_name
                    )
                    if preview_audio:
                        save_wave_func(preview_filename, preview_audio)
                        st.session_state.voice_previews[preview_key] = \
                            preview_filename
                except Exception:
                    pass  # 靜默處理錯誤，避免中斷流程


def voice_selector_with_preview(
    label: str,
    voice_options: List[str],
    voice_descriptions: Dict[str, str],
    api_key: str,
    selected_language: str,
    model_name: str,
    key_prefix: str,
    generate_preview_func: Callable,
    save_wave_func: Callable,
    default_index: int = 0,
    create_columns: bool = True
) -> str:
    """
    創建一個帶有預覽播放按鈕的語音選擇器
    
    Args:
        label: 選擇器標籤
        voice_options: 語音選項列表
        voice_descriptions: 語音描述字典
        api_key: Gemini API 金鑰
        selected_language: 選擇的語言
        model_name: TTS 模型名稱
        key_prefix: Streamlit 元件的 key 前綴
        generate_preview_func: 生成預覽的函數
        save_wave_func: 儲存音訊的函數
        default_index: 預設選項索引
        create_columns: 是否創建 columns 佈局
    
    Returns:
        選擇的語音名稱
    """
    if create_columns:
        # 創建兩欄佈局：選擇器和播放按鈕
        col1, col2 = st.columns([5, 1])
        
        with col1:
            # 語音選擇器
            selected_voice = st.selectbox(
                label,
                options=voice_options,
                format_func=lambda x: f"{x} - {voice_descriptions[x]}",
                key=f"{key_prefix}_select",
                index=default_index
            )
        
        with col2:
            # 添加垂直空間來對齊按鈕
            st.markdown("<div style='height: 29px'></div>",
                        unsafe_allow_html=True)
            
            # 播放按鈕
            button_help = f"播放 {selected_voice}"
            if st.button("▶️", key=f"{key_prefix}_play", help=button_help):
                _play_preview(api_key, selected_voice, selected_language,
                              model_name, generate_preview_func,
                              save_wave_func)
    else:
        # 不創建 columns，直接顯示元件
        selected_voice = st.selectbox(
            label,
            options=voice_options,
            format_func=lambda x: f"{x} - {voice_descriptions[x]}",
            key=f"{key_prefix}_select",
            index=default_index
        )
        
        # 播放按鈕
        button_help = f"播放 {selected_voice}"
        if st.button(f"▶️ {selected_voice}", key=f"{key_prefix}_play",
                     help=button_help):
            _play_preview(api_key, selected_voice, selected_language,
                          model_name, generate_preview_func,
                          save_wave_func)
    
    return selected_voice


def _play_preview(api_key: str, selected_voice: str, selected_language: str,
                  model_name: str, generate_preview_func: Callable,
                  save_wave_func: Callable):
    """播放預覽（從快取或即時生成）"""
    if not api_key:
        st.error("請先輸入 API 金鑰")
        return
    
    preview_key = f"{selected_voice}_{selected_language}"
    preview_filename = f"preview_{selected_voice}_{selected_language}.wav"
    
    # 檢查是否已有快取
    if ('voice_previews' in st.session_state and
            preview_key in st.session_state.voice_previews):
        # 直接播放快取的檔案
        st.audio(st.session_state.voice_previews[preview_key])
    elif os.path.exists(preview_filename):
        # 檔案存在但不在快取中，加入快取並播放
        if 'voice_previews' not in st.session_state:
            st.session_state.voice_previews = {}
        st.session_state.voice_previews[preview_key] = preview_filename
        st.audio(preview_filename)
    else:
        # 需要生成預覽
        with st.spinner("生成中..."):
            try:
                preview_audio = generate_preview_func(
                    api_key,
                    selected_voice,
                    selected_language,
                    model_name
                )
                if preview_audio:
                    # 儲存預覽音訊
                    save_wave_func(preview_filename, preview_audio)
                    
                    # 加入快取
                    if 'voice_previews' not in st.session_state:
                        st.session_state.voice_previews = {}
                    st.session_state.voice_previews[preview_key] = \
                        preview_filename
                    
                    # 播放音訊
                    st.audio(preview_filename)
            except Exception as e:
                st.error(f"生成失敗：{str(e)}")


def multi_speaker_voice_selector(
    num_speakers: int,
    api_key: str,
    selected_language: str,
    model_name: str,
    voice_options_dict: Dict[str, str],
    generate_preview_func: Callable,
    save_wave_func: Callable
) -> tuple:
    """
    為多講者模式創建語音選擇器
    
    Args:
        num_speakers: 講者數量
        api_key: Gemini API 金鑰
        selected_language: 選擇的語言
        model_name: TTS 模型名稱
        voice_options_dict: 語音選項字典
        generate_preview_func: 生成預覽的函數
        save_wave_func: 儲存音訊的函數
    
    Returns:
        (speakers, voice_configs, speaker_styles) 元組
    """
    speakers = []
    voice_configs = []
    speaker_styles = []
    
    speaker_cols = st.columns(num_speakers)
    
    for i in range(num_speakers):
        with speaker_cols[i]:
            st.markdown(f"#### 講者 {i+1}")
            
            # 講者名稱
            speaker_name = st.text_input(
                "講者名稱",
                value=f"講者{i+1}",
                key=f"speaker_{i}"
            )
            
            # 語音選擇（使用新的小工具）
            voice_options = list(voice_options_dict.keys())
            default_index = 0 if i == 0 else 1  # 不同講者使用不同預設語音
            
            selected_voice = voice_selector_with_preview(
                "選擇語音",
                voice_options,
                voice_options_dict,
                api_key,
                selected_language,
                model_name,
                f"speaker_{i}_voice",
                generate_preview_func,
                save_wave_func,
                default_index,
                create_columns=False  # 在多講者模式中不創建嵌套的 columns
            )
            
            # 風格選擇
            style = st.selectbox(
                "風格",
                ["無", "自訂", "興奮的", "平靜的", "友善的",
                 "嚴肅的", "幽默的", "溫柔的"],
                key=f"speaker_{i}_main_style"
            )
            
            # 自訂風格輸入
            if style == "自訂":
                custom_style = st.text_input(
                    "輸入自訂風格",
                    placeholder="例如：神秘的、熱情的、疲憊的...",
                    key=f"speaker_{i}_custom_style"
                )
                if custom_style:
                    style = custom_style
                else:
                    style = None
            
            speakers.append(speaker_name)
            voice_configs.append(selected_voice)
            speaker_styles.append(style if style != "無" else None)
    
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