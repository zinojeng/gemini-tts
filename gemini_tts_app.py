import os
import wave
import streamlit as st
from google import genai
from google.genai import types
from typing import List, Dict, Optional
import json
from datetime import datetime
from dotenv import load_dotenv
import re
import file_upload_module

# 載入環境變數
load_dotenv()

# 設定頁面配置
st.set_page_config(
    page_title="Gemini TTS 多語言文字轉語音",
    page_icon="🎙️",
    layout="wide"
)

# 語音選項列表
VOICE_OPTIONS = {
    "Zephyr": "明亮 (Bright)",
    "Puck": "活潑 (Upbeat)",
    "Charon": "資訊性 (Informative)",
    "Kore": "堅定 (Firm)",
    "Fenrir": "興奮 (Excitable)",
    "Leda": "年輕 (Youthful)",
    "Orus": "堅定 (Firm)",
    "Aoede": "輕快 (Breezy)",
    "Callirrhoe": "隨和 (Easy-going)",
    "Autonoe": "明亮 (Bright)",
    "Enceladus": "氣息感 (Breathy)",
    "Iapetus": "清晰 (Clear)",
    "Umbriel": "隨和 (Easy-going)",
    "Algieba": "流暢 (Smooth)",
    "Despina": "流暢 (Smooth)",
    "Erinome": "清晰 (Clear)",
    "Algenib": "沙啞 (Gravelly)",
    "Rasalgethi": "資訊性 (Informative)",
    "Laomedeia": "活潑 (Upbeat)",
    "Achernar": "柔和 (Soft)",
    "Alnilam": "堅定 (Firm)",
    "Schedar": "平穩 (Even)",
    "Gacrux": "成熟 (Mature)",
    "Pulcherrima": "前進 (Forward)",
    "Achird": "友善 (Friendly)",
    "Zubenelgenubi": "隨意 (Casual)",
    "Vindemiatrix": "溫柔 (Gentle)",
    "Sadachbia": "活潑 (Lively)",
    "Sadaltager": "博學 (Knowledgeable)",
    "Sulafat": "溫暖 (Warm)"
}

# 支援的語言
SUPPORTED_LANGUAGES = {
    "ar-EG": "阿拉伯語 (埃及)",
    "en-US": "英語 (美國)",
    "de-DE": "德語 (德國)",
    "es-US": "西班牙語 (美國)",
    "fr-FR": "法語 (法國)",
    "hi-IN": "印地語 (印度)",
    "id-ID": "印尼語 (印尼)",
    "it-IT": "義大利語 (義大利)",
    "ja-JP": "日語 (日本)",
    "ko-KR": "韓語 (韓國)",
    "pt-BR": "葡萄牙語 (巴西)",
    "ru-RU": "俄語 (俄羅斯)",
    "nl-NL": "荷蘭語 (荷蘭)",
    "pl-PL": "波蘭語 (波蘭)",
    "th-TH": "泰語 (泰國)",
    "tr-TR": "土耳其語 (土耳其)",
    "vi-VN": "越南語 (越南)",
    "ro-RO": "羅馬尼亞語 (羅馬尼亞)",
    "uk-UA": "烏克蘭語 (烏克蘭)",
    "bn-BD": "孟加拉語 (孟加拉)",
    "en-IN": "英語 (印度)",
    "mr-IN": "馬拉地語 (印度)",
    "ta-IN": "泰米爾語 (印度)",
    "te-IN": "泰盧固語 (印度)",
    "zh-CN": "中文 (簡體)",
    "zh-TW": "中文 (繁體)"
}

# TTS 模型選項
TTS_MODELS = {
    "gemini-2.5-flash-preview-tts": "Gemini 2.5 Flash Preview TTS (價格優惠)",
    "gemini-2.5-pro-preview-tts": "Gemini 2.5 Pro Preview TTS (最強大)"
}

# 提示範例
PROMPT_EXAMPLES = {
    "播客對話": {
        "single": "用興奮的語氣說：歡迎來到我們的科技播客！今天我們要討論人工智慧的未來發展。",
        "multi": """主持人A和主持人B的播客對話：
主持人A：歡迎回到我們的節目！今天有什麼特別的話題嗎？
主持人B：當然有！我們要討論最新的AI技術突破。
主持人A：聽起來很有趣！讓我們開始吧。"""
    },
    "有聲書朗讀": {
        "single": "用平靜、敘事的語氣朗讀：在一個寧靜的夜晚，月光灑在古老的城堡上，彷彿訴說著千年的故事。",
        "multi": """旁白和角色的對話：
旁白：夜深了，城堡裡傳來腳步聲。
騎士：誰在那裡？
公主：是我，我需要你的幫助。"""
    },
    "客服對話": {
        "single": "用友善、專業的語氣說：您好！感謝您致電客服中心。我是您的服務專員，很高興為您服務。",
        "multi": """客服和顧客的對話：
客服：您好，請問有什麼可以幫助您的嗎？
顧客：我想查詢我的訂單狀態。
客服：好的，請提供您的訂單編號。"""
    },
    "教育內容": {
        "single": "用清晰、教學的語氣說：今天我們要學習的是光合作用。植物通過葉綠素吸收陽光，將二氧化碳和水轉化為葡萄糖。",
        "multi": """老師和學生的對話：
老師：同學們，誰能告訴我光合作用的過程？
學生：老師，是植物利用陽光製造食物的過程嗎？
老師：非常好！讓我們深入了解一下。"""
    }
}

# 風格提示建議
STYLE_SUGGESTIONS = {
    "語氣": ["興奮的", "平靜的", "嚴肅的", "友善的", "神秘的", "幽默的"],
    "速度": ["快速地", "緩慢地", "正常速度", "有節奏地"],
    "情感": ["開心地", "悲傷地", "憤怒地", "驚訝地", "害怕地"],
    "特殊效果": ["低聲細語", "大聲喊叫", "帶著笑意", "帶著哭腔"]
}

def save_wave_file(filename: str, pcm_data: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2):
    """儲存 PCM 資料為 WAV 檔案"""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)

def clean_dialogue_text(text: str, speakers: List[str]) -> tuple:
    """清理多講者對話文本，移除描述性文字，只保留實際對話"""
    lines = text.strip().split('\n')
    cleaned_lines = []
    
    # 如果講者名稱是預設的"講者1"、"講者2"，嘗試從文本中提取實際的講者名稱
    actual_speakers = []
    if speakers == ["講者1", "講者2"]:
        # 掃描文本找出實際的講者名稱
        for line in lines:
            line = line.strip()
            if '：' in line or ':' in line:
                # 提取冒號前的部分作為講者名稱
                parts = line.split('：') if '：' in line else line.split(':')
                if len(parts) >= 2 and parts[1].strip():  # 確保冒號後有內容
                    speaker = parts[0].strip()
                    if speaker and speaker not in actual_speakers:
                        actual_speakers.append(speaker)
        
        # 如果找到實際的講者名稱，使用它們
        if len(actual_speakers) >= 2:
            speakers = actual_speakers[:2]
    
    # 清理對話文本
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 檢查是否為講者的對話
        for speaker in speakers:
            if line.startswith(f"{speaker}：") or line.startswith(f"{speaker}:"):
                cleaned_lines.append(line)
                break
    
    return '\n'.join(cleaned_lines), speakers

def apply_styles_to_dialogue(text: str, speakers: List[str], speaker_styles: List[List[str]]) -> str:
    """為每個講者的對話應用各自的風格"""
    lines = text.strip().split('\n')
    styled_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 檢查是哪個講者的對話
        for i, speaker in enumerate(speakers):
            if line.startswith(f"{speaker}：") or line.startswith(f"{speaker}:"):
                # 如果該講者有風格設定，在講者名稱前加入風格指令
                if i < len(speaker_styles) and speaker_styles[i]:
                    style_instruction = f"[{', '.join(speaker_styles[i])}] "
                    styled_line = f"{style_instruction}{line}"
                else:
                    styled_line = line
                
                styled_lines.append(styled_line)
                break
    
    return '\n'.join(styled_lines)

def generate_prompt_suggestion(prompt_type: str, speakers: List[str] = None, existing_text: str = "") -> str:
    """生成提示建議，可以在現有文本基礎上添加更多內容"""
    # 將範例類別映射到提示類型
    type_mapping = {
        "播客對話": "podcast",
        "有聲書朗讀": "audiobook", 
        "客服對話": "customer_service",
        "教育內容": "education"
    }
    
    # 如果傳入的是中文類別名稱，轉換為英文
    if prompt_type in type_mapping:
        prompt_type = type_mapping[prompt_type]
    
    if prompt_type == "podcast":
        if speakers:
            if not existing_text:
                return f"""製作一段播客對話，{speakers[0]}是主持人，{speakers[1]}是嘉賓：
{speakers[0]}：歡迎來到我們的節目！
{speakers[1]}：謝謝邀請，很高興來到這裡。"""
            else:
                # 根據現有內容長度生成不同的後續對話
                lines = existing_text.strip().split('\n')
                dialogue_count = len([l for l in lines if '：' in l or ':' in l])
                
                if dialogue_count < 6:
                    return existing_text + f"""
{speakers[0]}：今天我們要討論的主題非常有趣。
{speakers[1]}：是的，我對這個話題也很感興趣。"""
                elif dialogue_count < 10:
                    return existing_text + f"""
{speakers[0]}：能否分享一下您的經驗？
{speakers[1]}：當然，我記得有一次特別的經歷...
{speakers[0]}：聽起來很精彩！"""
                else:
                    return existing_text + f"""
{speakers[1]}：總結來說，這是一個很有意義的討論。
{speakers[0]}：非常感謝您今天的分享！
{speakers[1]}：謝謝您的邀請，期待下次再見！"""
        else:
            if not existing_text:
                return "用熱情的播客主持人語氣說：歡迎各位聽眾！今天我們有一個超級精彩的話題要和大家分享。"
            else:
                return existing_text + " 讓我們深入探討這個話題，看看它如何影響我們的日常生活。"
    
    elif prompt_type == "audiobook":
        if speakers:
            if not existing_text:
                return f"""朗讀一段小說，包含旁白和角色對話：
旁白：夜幕降臨，城市的燈光逐漸亮起。
{speakers[0]}：我們必須在天亮前找到答案。
{speakers[1]}：我知道一個地方，也許能找到線索。"""
            else:
                lines = existing_text.strip().split('\n')
                dialogue_count = len([l for l in lines if '：' in l or ':' in l])
                
                if dialogue_count < 6:
                    return existing_text + f"""
旁白：他們快步走向那座古老的建築。
{speakers[0]}：你確定是這裡嗎？
{speakers[1]}：相信我，線索就在裡面。"""
                elif dialogue_count < 10:
                    return existing_text + f"""
旁白：推開沉重的大門，一股神秘的氣息撲面而來。
{speakers[0]}：這裡看起來很久沒人來過了。
{speakers[1]}：小心，我們不知道會遇到什麼。"""
                else:
                    return existing_text + f"""
旁白：終於，他們找到了一直在尋找的東西。
{speakers[0]}：原來答案一直在這裡！
{speakers[1]}：是的，一切都說得通了。"""
        else:
            if not existing_text:
                return "用沉穩的敘事語氣朗讀：很久很久以前，在一個遙遠的王國裡，住著一位勇敢的騎士。"
            else:
                return existing_text + " 他的冒險故事傳遍了整個王國，激勵著無數年輕人追求自己的夢想。"
    
    elif prompt_type == "customer_service":
        if speakers:
            if not existing_text:
                return f"""客服和顧客的對話：
{speakers[0]}：您好，很高興為您服務，請問有什麼可以幫助您的嗎？
{speakers[1]}：我想詢問一下關於產品退換貨的政策。"""
            else:
                lines = existing_text.strip().split('\n')
                dialogue_count = len([l for l in lines if '：' in l or ':' in l])
                
                if dialogue_count < 6:
                    return existing_text + f"""
{speakers[0]}：當然可以，我們的退換貨政策是30天內無條件退換。
{speakers[1]}：那需要保留原包裝嗎？"""
                elif dialogue_count < 10:
                    return existing_text + f"""
{speakers[0]}：是的，請盡量保持商品的原始包裝和配件完整。
{speakers[1]}：好的，我明白了。還有其他注意事項嗎？
{speakers[0]}：請記得攜帶購買憑證，這樣處理會更快速。"""
                else:
                    return existing_text + f"""
{speakers[1]}：非常感謝您的詳細說明！
{speakers[0]}：不客氣，還有其他問題嗎？
{speakers[1]}：沒有了，謝謝您的幫助！"""
        else:
            return "用專業友善的客服語氣說：歡迎致電客戶服務中心，我是您的專屬客服代表。"
    
    elif prompt_type == "education":
        if speakers:
            if not existing_text:
                return f"""教學對話：
{speakers[0]}：今天我們要學習的主題是人工智慧。
{speakers[1]}：老師，AI和機器學習有什麼區別嗎？
{speakers[0]}：很好的問題！讓我來解釋一下。"""
            else:
                lines = existing_text.strip().split('\n')
                dialogue_count = len([l for l in lines if '：' in l or ':' in l])
                
                if dialogue_count < 6:
                    return existing_text + f"""
{speakers[0]}：AI是一個更廣泛的概念，包含了機器學習。
{speakers[1]}：那深度學習又是什麼呢？
{speakers[0]}：深度學習是機器學習的一個子集。"""
                elif dialogue_count < 10:
                    return existing_text + f"""
{speakers[1]}：能舉個實際的例子嗎？
{speakers[0]}：當然！比如語音識別就是一個很好的例子。
{speakers[1]}：原來如此，我開始理解了！"""
                else:
                    return existing_text + f"""
{speakers[0]}：今天的課程就到這裡，有問題嗎？
{speakers[1]}：謝謝老師，講解得很清楚！
{speakers[0]}：很高興能幫助你們理解這個概念。"""
        else:
            if not existing_text:
                return "用清晰的教學語氣說：歡迎來到今天的課程。我們將學習如何使用人工智慧技術來解決實際問題。"
            else:
                return existing_text + " 接下來，讓我們通過一些實際案例來深入理解這些概念。"
    
    return ""

def main():
    st.title("🎙️ Gemini TTS 多語言文字轉語音系統")
    st.markdown("使用 Google Gemini API 將文字轉換為自然的語音")
    
    # 側邊欄設定
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # API 金鑰 - 從環境變數讀取預設值
        default_api_key = os.getenv("GEMINI_API_KEY", "")
        
        # 如果有預設金鑰，顯示提示但不顯示實際值
        if default_api_key:
            st.success("✅ 已從環境變數載入 API 金鑰")
            api_key = st.text_input(
                "Gemini API 金鑰（選填，留空使用環境變數）", 
                type="password",
                help="已從 .env 檔案載入 API 金鑰。如需使用其他金鑰，請在此輸入"
            )
            # 如果使用者沒有輸入新的金鑰，使用環境變數的金鑰
            if not api_key:
                api_key = default_api_key
        else:
            api_key = st.text_input(
                "Gemini API 金鑰", 
                type="password",
                help="請輸入您的 Gemini API 金鑰，或在 .env 檔案中設定 GEMINI_API_KEY"
            )
        
        # 模型選擇
        model_name = st.selectbox(
            "選擇 TTS 模型",
            options=list(TTS_MODELS.keys()),
            format_func=lambda x: TTS_MODELS[x]
        )
        
        # TTS 模式選擇
        tts_mode = st.radio("TTS 模式", ["單一講者", "多講者對話"])
        
        st.markdown("---")
        st.markdown("### 📚 使用說明")
        st.markdown("""
        1. 輸入您的 Gemini API 金鑰
        2. 選擇 TTS 模式（單一或多講者）
        3. 選擇語音和設定參數
        4. 輸入或生成文字內容
        5. 點擊「生成語音」
        """)
    
    # 主要內容區域
    col1, col2 = st.columns([2, 1])
    
    # 初始化變數
    selected_styles = []
    
    with col1:
        st.header("📝 文字內容")
        
        # 提示範例選擇
        example_category = st.selectbox(
            "選擇範例類別",
            ["自訂內容", "播客對話", "有聲書朗讀", "客服對話", "教育內容"]
        )
        
        if example_category != "自訂內容":
            example_key = example_category
            if tts_mode == "單一講者":
                default_text = PROMPT_EXAMPLES[example_key]["single"]
            else:
                default_text = PROMPT_EXAMPLES[example_key]["multi"]
        else:
            default_text = ""
        
        # 文字輸入區域
        if tts_mode == "單一講者":
            st.subheader("單一講者設定")
            
            # 語音選擇
            voice_name = st.selectbox(
                "選擇語音",
                options=list(VOICE_OPTIONS.keys()),
                format_func=lambda x: f"{x} - {VOICE_OPTIONS[x]}"
            )
            
            # 風格提示
            st.markdown("#### 風格提示建議")
            style_cols = st.columns(4)
            
            for i, (category, options) in enumerate(STYLE_SUGGESTIONS.items()):
                with style_cols[i % 4]:
                    selected = st.selectbox(f"{category}", ["無"] + options)
                    if selected != "無":
                        selected_styles.append(selected)
            
            # 生成提示建議
            if st.button("生成提示建議"):
                # 獲取當前文本框的內容
                current_text = st.session_state.get('single_text_content', '')
                prompt_suggestion = generate_prompt_suggestion(
                    example_category,  # 直接傳遞範例類別
                    None,
                    current_text
                )
                st.session_state.single_text_content = prompt_suggestion
            
            # 文字內容
            text_content = st.text_area(
                "輸入文字內容",
                value=st.session_state.get('single_text_content', default_text),
                height=200,
                help="輸入要轉換為語音的文字",
                key="single_text_content"
            )
            
            # 如果有選擇風格，加入到提示中
            if selected_styles and text_content:
                style_prompt = "，".join(selected_styles) + "地說："
                if not text_content.startswith(style_prompt):
                    full_prompt = style_prompt + text_content
                else:
                    full_prompt = text_content
            else:
                full_prompt = text_content
        
        else:  # 多講者模式
            st.subheader("多講者對話設定")
            
            # 添加檔案上傳選項
            input_method = st.radio(
                "輸入方式",
                ["手動輸入", "上傳檔案"],
                horizontal=True
            )
            
            # 講者數量
            num_speakers = st.number_input("講者數量", min_value=2, max_value=2, value=2)
            
            speakers = []
            voice_configs = []
            speaker_styles = []  # 儲存每個講者的風格
            
            # 講者設定
            speaker_cols = st.columns(num_speakers)
            for i in range(num_speakers):
                with speaker_cols[i]:
                    st.markdown(f"#### 講者 {i+1}")
                    speaker_name = st.text_input(f"講者名稱", value=f"講者{i+1}", key=f"speaker_{i}")
                    
                    # 為不同講者設定不同的預設語音
                    voice_options = list(VOICE_OPTIONS.keys())
                    if i == 0:
                        default_index = 0  # 第一個講者使用第一個語音 (Zephyr)
                    else:
                        default_index = 1  # 第二個講者使用第二個語音 (Puck)
                    
                    voice_name = st.selectbox(
                        f"選擇語音",
                        options=voice_options,
                        format_func=lambda x: f"{x} - {VOICE_OPTIONS[x]}",
                        key=f"voice_{i}",
                        index=default_index
                    )
                    
                    # 簡化的風格選擇 - 只選擇一個主要風格
                    style = st.selectbox(
                        "風格",
                        ["無", "自訂", "興奮的", "平靜的", "友善的", "嚴肅的", "幽默的", "溫柔的"],
                        key=f"speaker_{i}_main_style"
                    )
                    
                    # 如果選擇自訂，顯示輸入框
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
                    voice_configs.append(voice_name)
                    speaker_styles.append(style if style != "無" else None)
            
            # 根據輸入方式顯示不同的介面
            if input_method == "手動輸入":
                # 生成對話提示建議
                if st.button("生成對話建議"):
                    # 獲取當前文本框的內容
                    current_text = st.session_state.get('multi_text_content', '')
                    prompt_suggestion = generate_prompt_suggestion(
                        example_category,  # 直接傳遞範例類別
                        speakers,
                        current_text
                    )
                    st.session_state.multi_text_content = prompt_suggestion
                
                # 對話內容
                text_content = st.text_area(
                    "輸入對話內容",
                    value=st.session_state.get('multi_text_content', default_text),
                    height=300,
                    help=f"格式範例：\n{speakers[0]}：說話內容\n{speakers[1]}：回應內容",
                    key="multi_text_content"
                )
            
            else:  # 上傳檔案
                uploaded_file = st.file_uploader(
                    "選擇檔案",
                    type=['srt', 'txt', 'text'],
                    help="支援 SRT 字幕檔或純文字檔案"
                )
                
                if uploaded_file is not None:
                    # 讀取檔案內容
                    file_content = uploaded_file.read().decode('utf-8')
                    
                    # 處理上傳的檔案
                    dialogues, original_speakers = file_upload_module.process_uploaded_file(
                        file_content, uploaded_file.name
                    )
                    
                    # 如果識別到原始講者，更新講者名稱
                    if original_speakers:
                        st.info(f"從檔案中識別到講者：{', '.join(original_speakers)}")
                        # 可以選擇是否使用原始講者名稱
                        use_original = st.checkbox("使用檔案中的講者名稱", value=True)
                        if use_original and len(original_speakers) >= 2:
                            speakers[0] = original_speakers[0]
                            speakers[1] = original_speakers[1]
                    
                    # 格式化對話內容
                    formatted_text = file_upload_module.format_dialogues_for_display(
                        dialogues, speakers
                    )
                    
                    # 顯示並允許編輯
                    text_content = st.text_area(
                        "編輯對話內容（可選）",
                        value=formatted_text,
                        height=300,
                        help="您可以在此編輯對話內容後再生成語音"
                    )
                else:
                    text_content = ""
                    st.info("請上傳 SRT 或文字檔案")
    
    with col2:
        st.header("🎯 生成設定")
        
        # 語言選擇
        selected_language = st.selectbox(
            "選擇語言",
            options=list(SUPPORTED_LANGUAGES.keys()),
            format_func=lambda x: SUPPORTED_LANGUAGES[x],
            index=list(SUPPORTED_LANGUAGES.keys()).index("zh-TW")
        )
        
        # 進階設定
        with st.expander("進階設定"):
            st.markdown("### 音訊參數")
            sample_rate = st.selectbox("採樣率", [24000, 16000, 8000], index=0)
            channels = st.selectbox("聲道", [1, 2], index=0)
            
            st.markdown("### 輸出設定")
            output_format = st.selectbox("輸出格式", ["WAV", "PCM"], index=0)
    
    # 生成按鈕
    st.markdown("---")
    col_generate, col_download = st.columns([1, 1])
    
    with col_generate:
        generate_button = st.button("🎤 生成語音", type="primary", use_container_width=True)
    
    # 生成語音
    if generate_button:
        if not api_key:
            st.error("請輸入 Gemini API 金鑰")
            return
        
        if not text_content:
            st.error("請輸入文字內容")
            return
        
        try:
            with st.spinner("正在生成語音..."):
                # 初始化 Gemini 客戶端
                client = genai.Client(api_key=api_key)
                
                # 準備生成配置
                if tts_mode == "單一講者":
                    # 單一講者配置
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
                    prompt = full_prompt if 'full_prompt' in locals() else text_content
                else:
                    # 多講者配置
                    # 清理多講者對話文本
                    cleaned_text, actual_speakers = clean_dialogue_text(text_content, speakers)
                    
                    # 檢查清理後的文本是否為空
                    if not cleaned_text.strip():
                        st.error(f"清理後的對話文本為空。請確保對話格式正確，講者名稱後需要有冒號（：）。\n當前講者：{', '.join(speakers)}")
                        st.info("提示：對話格式應該是「講者名稱：對話內容」")
                        return
                    
                    # 顯示清理後的文本（調試用）
                    with st.expander("調試信息 - 清理後的對話文本"):
                        st.text(cleaned_text)
                        if actual_speakers != speakers:
                            st.info(f"自動識別的講者：{', '.join(actual_speakers)}")
                        
                        # 顯示語音配置
                        st.markdown("---")
                        st.markdown("**語音配置：**")
                        for i, (speaker, voice) in enumerate(zip(actual_speakers, voice_configs)):
                            st.write(f"- {speaker}：{voice}")
                        
                        # 顯示風格設定
                        if any(speaker_styles):
                            st.markdown("---")
                            st.markdown("**風格設定：**")
                            for i, (speaker, style) in enumerate(zip(actual_speakers, speaker_styles)):
                                if i < len(speaker_styles) and style:
                                    st.write(f"- {speaker}：{style}")
                                else:
                                    st.write(f"- {speaker}：無")
                    
                    speaker_voice_configs = []
                    for i in range(len(actual_speakers)):
                        speaker_voice_configs.append(
                            types.SpeakerVoiceConfig(
                                speaker=actual_speakers[i],
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name=voice_configs[i]
                                    )
                                )
                            )
                        )
                    
                    config = types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                                speaker_voice_configs=speaker_voice_configs
                            )
                        )
                    )
                    
                    # 加入提示前綴
                    # 嘗試在提示中加入風格指令
                    if any(speaker_styles):
                        style_lines = []
                        for i, (speaker, style) in enumerate(zip(actual_speakers, speaker_styles)):
                            if style:
                                style_lines.append(f"{speaker}用{style}語氣說話")
                        
                        if style_lines:
                            style_instruction = "；".join(style_lines) + "。"
                            prompt = f"{style_instruction}\n\n{cleaned_text}"
                        else:
                            prompt = f"TTS 以下對話：\n{cleaned_text}"
                    else:
                        prompt = f"TTS 以下對話：\n{cleaned_text}"
                
                # 顯示最終提示（調試用）
                with st.expander("調試信息 - 發送給 API 的提示"):
                    st.text(prompt)
                
                # 生成語音
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
                
                # 檢查回應是否有效
                if not response or not response.candidates:
                    st.error("API 未返回有效的回應。請檢查您的輸入內容。")
                    return
                
                if not response.candidates[0].content or not response.candidates[0].content.parts:
                    st.error("API 回應中沒有音訊資料。可能是因為文本格式不正確或講者名稱不匹配。")
                    st.info(f"當前講者設定：{speakers}")
                    return
                
                # 獲取音訊資料
                audio_data = response.candidates[0].content.parts[0].inline_data.data
                
                # 儲存檔案
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"gemini_tts_{timestamp}.wav"
                
                if output_format == "WAV":
                    save_wave_file(filename, audio_data, channels, sample_rate)
                else:
                    # 儲存為 PCM
                    filename = f"gemini_tts_{timestamp}.pcm"
                    with open(filename, "wb") as f:
                        f.write(audio_data)
                
                st.success(f"✅ 語音生成成功！檔案已儲存為：{filename}")
                
                # 顯示音訊播放器
                if output_format == "WAV":
                    st.audio(filename)
                
                # 下載按鈕
                with col_download:
                    with open(filename, "rb") as f:
                        st.download_button(
                            label="📥 下載音訊檔案",
                            data=f.read(),
                            file_name=filename,
                            mime="audio/wav" if output_format == "WAV" else "audio/pcm",
                            use_container_width=True
                        )
                
                # 顯示生成資訊
                with st.expander("生成資訊"):
                    st.json({
                        "模型": model_name,
                        "模式": tts_mode,
                        "語言": SUPPORTED_LANGUAGES[selected_language],
                        "語音": voice_name if tts_mode == "單一講者" else voice_configs,
                        "檔案名稱": filename,
                        "採樣率": sample_rate,
                        "聲道": channels
                    })
        
        except Exception as e:
            st.error(f"生成失敗：{str(e)}")
            st.exception(e)

if __name__ == "__main__":
    main() 