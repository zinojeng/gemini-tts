"""
背景預覽生成器模組
在應用程式啟動時自動生成所有語音預覽
"""

import streamlit as st
import os
from typing import List, Dict, Callable
import threading
import time


def start_background_generation(
    voice_options: List[str],
    api_key: str,
    language: str,
    model_name: str,
    generate_preview_func: Callable,
    save_wave_func: Callable
):
    """
    在背景執行緒中生成所有語音預覽
    
    Args:
        voice_options: 語音選項列表
        api_key: Gemini API 金鑰
        language: 語言代碼
        model_name: TTS 模型名稱
        generate_preview_func: 生成預覽的函數
        save_wave_func: 儲存音訊的函數
    """
    def generate_all_previews():
        """在背景執行緒中生成預覽"""
        for voice in voice_options:
            preview_key = f"{voice}_{language}"
            preview_filename = f"preview_{voice}_{language}.wav"
            
            # 檢查是否已存在
            if not os.path.exists(preview_filename):
                try:
                    # 生成預覽
                    preview_audio = generate_preview_func(
                        api_key,
                        voice,
                        language,
                        model_name
                    )
                    if preview_audio:
                        # 儲存檔案
                        save_wave_func(preview_filename, preview_audio)
                        
                        # 更新 session_state（如果可用）
                        if hasattr(st, 'session_state'):
                            if 'voice_previews' not in st.session_state:
                                st.session_state.voice_previews = {}
                            st.session_state.voice_previews[preview_key] = \
                                preview_filename
                        
                        # 短暫延遲，避免過度使用 API
                        time.sleep(0.5)
                        
                except Exception as e:
                    print(f"生成 {voice} 預覽時發生錯誤：{e}")
    
    # 啟動背景執行緒
    thread = threading.Thread(target=generate_all_previews, daemon=True)
    thread.start()
    
    return thread


def check_generation_status(voice_options: List[str],
                            language: str) -> Dict[str, int]:
    """
    檢查預覽生成狀態
    
    Args:
        voice_options: 語音選項列表
        language: 語言代碼
    
    Returns:
        包含 'total' 和 'completed' 的字典
    """
    total = len(voice_options)
    completed = sum(1 for voice in voice_options
                    if os.path.exists(f"preview_{voice}_{language}.wav"))
    
    return {
        'total': total,
        'completed': completed,
        'percentage': int((completed / total) * 100) if total > 0 else 0
    }


def ensure_all_previews_ready(
    voice_options: List[str],
    api_key: str,
    language: str,
    model_name: str,
    generate_preview_func: Callable,
    save_wave_func: Callable,
    show_ui: bool = True
) -> bool:
    """
    確保所有預覽都已準備就緒
    
    Args:
        voice_options: 語音選項列表
        api_key: Gemini API 金鑰
        language: 語言代碼
        model_name: TTS 模型名稱
        generate_preview_func: 生成預覽的函數
        save_wave_func: 儲存音訊的函數
        show_ui: 是否顯示 UI 元素
    
    Returns:
        是否所有預覽都已準備就緒
    """
    if not api_key:
        return False
    
    # 檢查當前狀態
    status = check_generation_status(voice_options, language)
    
    if status['completed'] == status['total']:
        return True
    
    # 如果尚未開始生成，啟動背景生成
    if 'preview_generation_thread' not in st.session_state:
        st.session_state.preview_generation_thread = \
            start_background_generation(
                voice_options,
                api_key,
                language,
                model_name,
                generate_preview_func,
                save_wave_func
            )
    
    # 顯示進度（如果需要）
    if show_ui and status['completed'] < status['total']:
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 🎵 語音預覽")
            st.progress(status['percentage'] / 100)
            st.info(f"正在背景生成預覽... ({status['completed']}/{status['total']})")
    
    return status['completed'] == status['total'] 