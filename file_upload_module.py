"""
檔案上傳處理模組
提供 SRT 和文字檔案的解析功能
"""
import re
from typing import List, Tuple, Optional


def parse_srt_file(content: str) -> List[Tuple[str, str]]:
    """
    解析 SRT 檔案內容
    返回: [(講者, 文本), ...] 的列表
    """
    dialogues = []
    blocks = content.strip().split('\n\n')
    
    # 用於追蹤講者
    current_speaker = "講者1"
    speaker_toggle = {"講者1": "講者2", "講者2": "講者1"}
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:  # SRT 格式至少有 3 行：序號、時間、文本
            # 跳過序號和時間行，獲取文本
            text_lines = lines[2:]
            text = ' '.join(text_lines).strip()
            
            if text:
                # 檢查文本中是否有講者標記
                speaker_match = re.match(r'^([^:：]+)[：:](.*)$', text)
                if speaker_match:
                    # 如果有講者標記，使用標記的講者
                    speaker_label = speaker_match.group(1).strip()
                    text = speaker_match.group(2).strip()
                    # 這裡可以根據需要映射講者標籤
                    dialogues.append((speaker_label, text))
                else:
                    # 沒有講者標記，使用交替講者
                    dialogues.append((current_speaker, text))
                    # 切換到下一個講者
                    current_speaker = speaker_toggle[current_speaker]
    
    return dialogues


def parse_text_file(content: str) -> Tuple[List[Tuple[str, str]], List[str]]:
    """
    解析文本檔案，自動識別講者和對話
    返回: ([(講者標籤, 文本), ...], [原始講者名稱列表])
    """
    dialogues = []
    lines = content.strip().split('\n')
    
    # 預設講者名稱
    speaker1_name = "講者1"
    speaker2_name = "講者2"
    current_speaker = None
    speaker_map = {}
    original_speakers = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 檢查是否有講者標記（如 "A:", "B:", "講者1:", "客服:" 等）
        speaker_match = re.match(r'^([^:：]+)[：:](.*)$', line)
        
        if speaker_match:
            speaker_label = speaker_match.group(1).strip()
            text = speaker_match.group(2).strip()
            
            # 記錄原始講者名稱
            if speaker_label not in speaker_map:
                original_speakers.append(speaker_label)
                # 映射講者標籤到講者1或講者2
                if len(speaker_map) == 0:
                    speaker_map[speaker_label] = speaker1_name
                elif len(speaker_map) == 1:
                    speaker_map[speaker_label] = speaker2_name
                else:
                    # 如果有超過兩個講者，循環使用
                    speaker_map[speaker_label] = (speaker1_name 
                                                 if len(speaker_map) % 2 == 0 
                                                 else speaker2_name)
            
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
    
    return dialogues, original_speakers


def format_dialogues_for_display(dialogues: List[Tuple[str, str]], 
                               speaker_names: List[str]) -> str:
    """
    將對話格式化為顯示格式
    
    Args:
        dialogues: [(講者標籤, 文本), ...] 的列表
        speaker_names: [自定義講者1名稱, 自定義講者2名稱]
    
    Returns:
        格式化的對話文本
    """
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


def process_uploaded_file(file_content: str, file_name: str) -> Tuple[List[Tuple[str, str]], List[str]]:
    """
    處理上傳的檔案
    
    Args:
        file_content: 檔案內容
        file_name: 檔案名稱
    
    Returns:
        (對話列表, 原始講者名稱列表)
    """
    if file_name.endswith('.srt'):
        dialogues = parse_srt_file(file_content)
        # SRT 檔案通常沒有明確的講者標記，返回空列表
        return dialogues, []
    else:
        # 處理為文本檔案
        return parse_text_file(file_content) 