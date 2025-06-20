# Gemini TTS 開發進度記錄

## 2024-12-19 更新

### 問題描述
在多講者模式下，當使用範例類別（如「有聲書朗讀」、「客服對話」等）時，系統會將描述性文字和講者標籤都唸出來，而不是只唸出實際的對話內容。

**具體問題：**
- 輸入文本包含「客服和顧客的對話：」這類描述時，TTS 會將其當作語音內容
- 講者標籤（如「客服：」、「顧客：」）也會被唸出來
- 講者名稱不匹配導致 API 回應錯誤

### 解決方案

#### 1. 實現文本預處理功能
- 創建 `clean_dialogue_text()` 函數來清理對話文本
- 自動過濾掉不包含實際對話的描述性文字
- 只保留以講者名稱開頭且包含對話內容的行

#### 2. 自動識別講者名稱
- 當使用預設的「講者1」、「講者2」時，自動從範例文本中提取實際講者名稱
- 智能識別對話格式，排除只有冒號但沒有內容的描述行
- 支援中文冒號（：）和英文冒號（:）

#### 3. 改善使用者體驗
- 為講者 2 設定不同的預設語音（Puck），與講者 1（Zephyr）區分
- 添加調試信息展示區，顯示清理後的文本和識別的講者
- 提供詳細的錯誤訊息和提示

#### 4. 錯誤處理
- 檢查清理後的文本是否為空
- 驗證 API 回應的有效性
- 提供有用的錯誤訊息幫助使用者排除問題

### 技術實現細節

```python
def clean_dialogue_text(text: str, speakers: List[str]) -> tuple:
    """
    清理多講者對話文本
    - 自動識別文本中的實際講者名稱
    - 過濾掉描述性文字
    - 返回清理後的文本和實際講者列表
    """
```

### 測試結果
✅ 「播客對話」範例正常運作
✅ 「有聲書朗讀」範例成功過濾描述文字
✅ 「客服對話」範例正確識別講者
✅ 「教育內容」範例正常生成語音

### 後續優化建議
1. 支援更多講者（目前限制為 2 個）
2. 添加講者語音預覽功能
3. 支援自定義講者語音映射
4. 優化講者識別算法，支援更多格式

### 相關檔案
- `gemini_tts_app.py` - 主要應用程式（已更新）
- `gemini_tts_cli.py` - 命令列版本（待同步更新）

### Git 提交記錄
- Commit: 3d9fa1e
- Message: 修正多講者模式：自動識別講者名稱並過濾描述性文字
- Date: 2024-12-19 

## 2024-12-26

### 問題：多講者模式會將 Style instructions 內容唸出來

**問題描述：**
當使用多講者模式時，系統會將以下內容都當作語音唸出來：
- "客服和顧客的對話："
- "客服："、"顧客："等講者標籤
- Style instructions 的內容

**解決方案：**

1. **文本預處理功能**
   - 在 `clean_dialogue_text` 函數中實現了智能文本清理
   - 自動識別並過濾掉描述性文字（如"客服和顧客的對話："）
   - 只保留實際的對話內容

2. **講者識別改進**
   - 實現了自動從範例文本中提取講者名稱
   - 修正了講者順序問題（從字母排序改為出現順序）
   - 支援冒號的全形（：）和半形（:）格式

3. **風格設定簡化**
   - 從複雜的多選風格改為單一風格選擇
   - 添加了「自訂」選項，讓用戶輸入個性化風格
   - 風格指令格式：`講者名用風格語氣說話`

4. **調試信息增強**
   - 顯示清理後的對話文本
   - 顯示實際傳送給 API 的內容
   - 顯示每個講者的語音和風格配置

### 累積生成對話功能

**功能描述：**
用戶可以通過多次點擊「生成對話建議」按鈕，在現有對話基礎上累積生成更多內容。

**實現細節：**

1. **修改 `generate_prompt_suggestion` 函數**
   - 添加 `existing_text` 參數來接收現有文本
   - 根據現有對話的長度（對話輪數）生成不同的後續內容
   - 支援所有範例類別：播客對話、有聲書朗讀、客服對話、教育內容

2. **使用 Streamlit session_state**
   - 單一講者模式使用 `single_text_content` 鍵
   - 多講者模式使用 `multi_text_content` 鍵
   - 保持文本框內容在按鈕點擊後不會重置

3. **智能內容生成**
   - 0-6 句對話：生成開場和基礎互動
   - 6-10 句對話：深入主題討論
   - 10+ 句對話：總結和結束語
   - 每個階段的內容都與前文連貫

4. **支援的範例類別**
   - **播客對話**：從歡迎到深入討論再到感謝結束
   - **有聲書朗讀**：從場景設定到情節發展再到高潮結局
   - **客服對話**：從問題提出到解答再到確認結束
   - **教育內容**：從概念介紹到深入解釋再到總結回顧

**使用方式：**
1. 選擇範例類別
2. 點擊「生成對話建議」生成初始對話
3. 再次點擊按鈕，在現有內容基礎上添加更多對話
4. 可以多次點擊，直到生成完整的對話內容

### 檔案上傳功能整合

**功能描述：**
在主程式的多講者模式中整合了檔案上傳功能，用戶可以上傳 SRT 或文字檔案來生成語音。

**架構設計：**

1. **模組化設計**
   - `file_upload_module.py`：獨立的檔案處理模組
   - 提供檔案解析和格式化功能
   - 可被主程式呼叫，保持代碼整潔

2. **主程式整合**
   - 在多講者模式中添加「輸入方式」選項
   - 支援「手動輸入」和「上傳檔案」兩種方式
   - 保持原有功能不受影響

3. **檔案處理功能**
   - **SRT 檔案**：自動解析字幕格式，識別對話內容
   - **文字檔案**：智能識別講者標記（支援中英文冒號）
   - **講者映射**：自動將檔案中的講者映射到講者1和講者2

4. **用戶體驗優化**
   - 顯示從檔案中識別到的原始講者名稱
   - 提供選項讓用戶決定是否使用原始講者名稱
   - 允許編輯解析後的對話內容
   - 保留所有講者設定功能（語音、風格等）

**使用流程：**
1. 選擇「多講者對話」模式
2. 選擇「上傳檔案」輸入方式
3. 上傳 SRT 或 TXT 檔案
4. 系統自動識別講者並顯示對話
5. 可選擇使用原始講者名稱
6. 編輯對話內容（可選）
7. 設定每個講者的語音和風格
8. 生成語音

## 技術要點

- 使用正則表達式匹配講者格式
- 支援中英文冒號
- 自動過濾非對話行
- 保持對話的連貫性和邏輯性
- 模組化設計便於維護和擴展

## 2024-12-XX - 整合檔案上傳功能

### 實施內容
1. 將檔案上傳功能整合到主程式
2. 創建 `file_upload_module.py` 作為獨立模組
3. 在多講者模式中添加「輸入方式」選項
4. 支援 SRT 字幕檔和文字檔案的解析
5. 自動識別檔案中的講者標記

### 技術細節
- 使用模組化設計，便於維護和擴展
- 支援中英文冒號的講者標記
- 提供選項讓用戶決定是否使用原始講者名稱

### 清理工作
- 刪除了獨立的 `file_upload_tts.py`
- 刪除了相關的 README 文件
- 統一使用主程式入口

## 2024-12-XX - 添加內嵌播放按鈕功能

### 需求背景
用戶希望在語音選擇時能有更便捷的預覽方式，最好是在選擇器旁邊直接有播放按鈕。

### 實施內容
1. **創建語音預覽小工具模組**
   - 新建 `voice_preview_widget.py` 作為獨立的延伸功能模組
   - 提供 `voice_selector_with_preview` 函數，整合語音選擇和預覽功能
   - 提供 `multi_speaker_voice_selector` 函數，處理多講者模式

2. **內嵌播放按鈕設計**
   - 使用 5:1 的欄位比例，選擇器佔 5，播放按鈕佔 1
   - 播放按鈕使用 ▶️ 圖標，簡潔明瞭
   - 添加 hover 提示顯示將要預覽的語音名稱

3. **主程式整合**
   - 最小化對主程式的修改
   - 單一講者模式直接使用新的小工具
   - 多講者模式完全替換為新的實現
   - 移除了重複的講者設定代碼

4. **預覽體驗優化**
   - 預覽音訊直接在當前位置播放
   - 顯示成功訊息確認預覽生成
   - 維護預覽歷史記錄（最多保留5個）

### 技術細節
- 避免在模組導入時使用 Streamlit 元件，防止 `set_page_config` 錯誤
- 使用模組化設計，便於未來擴展和維護
- 保持與原有功能的完全相容性

### 使用效果
- 用戶可以在選擇語音的同時快速預覽
- 介面更加簡潔，操作更加直觀
- 預覽按鈕位置固定，易於點擊
- 支援單一講者和多講者模式
