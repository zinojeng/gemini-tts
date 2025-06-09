# Gemini TTS 多語言文字轉語音系統

這是一個使用 Google Gemini API 的文字轉語音（TTS）應用程式，支援單一講者和多講者模式，以及多種語言。

## 功能特點

- 🎙️ **單一講者模式**：使用 30 種不同的語音選項
- 👥 **多講者對話模式**：支援最多 2 個講者的對話
- 🌍 **多語言支援**：支援 24 種語言，包括中文、英文、日文等
- 🎨 **風格控制**：透過自然語言控制語音的風格、語氣、速度等
- 📝 **提示範例**：內建播客、有聲書、客服、教育等場景範例
- 💻 **雙介面**：提供 Streamlit 網頁介面和命令列工具
- 📄 **檔案上傳**：支援上傳 SRT 字幕檔和文字檔案（多講者模式）
- 🤖 **智能識別**：自動識別檔案中的講者並映射到語音設定
- 🔊 **語音預覽**：選擇語音時可先試聽效果，幫助選擇最適合的語音

## 安裝

### 快速開始（最推薦）

使用啟動腳本自動完成所有設定：

```bash
./start.sh
```

如果是第一次執行，可能需要先設定執行權限：
```bash
chmod +x start.sh run.sh
```

啟動腳本會自動：
- ✅ 檢查 Python 版本
- ✅ 建立並啟動虛擬環境
- ✅ 安裝所有相依套件
- ✅ 檢查/建立 .env 檔案
- ✅ 提供互動式選單

### 快速執行（已設定好環境）

如果已經完成初始設定，可以使用快速執行腳本：

```bash
./run.sh
```

這會直接啟動 Streamlit 網頁介面。

### 使用設定助手

執行設定助手來手動完成設定：

```bash
python setup.py
```

### 手動設定

1. 安裝相依套件：
```bash
pip install -r requirements.txt
```

2. 取得 Gemini API 金鑰：
   - 前往 [Google AI Studio](https://makersuite.google.com/app/apikey)
   - 建立新的 API 金鑰

3. 設定環境變數：
   - 建立 `.env` 檔案並加入您的 API 金鑰：
   ```bash
   GEMINI_API_KEY=your_actual_api_key_here
   ```
   - 或者設定系統環境變數：
   ```bash
   export GEMINI_API_KEY=your_actual_api_key_here
   ```

## 使用方式

### 網頁介面（Streamlit）

```bash
streamlit run gemini_tts_app.py
```

然後在瀏覽器中開啟顯示的網址。

#### 檔案上傳功能（多講者模式）

1. 選擇「多講者對話」模式
2. 選擇「上傳檔案」輸入方式
3. 支援的檔案格式：
   - **SRT 字幕檔**：自動解析時間軸和對話內容
   - **TXT 文字檔**：智能識別講者標記（支援「講者：」格式）
4. 系統會自動識別檔案中的講者名稱
5. 可選擇是否使用原始講者名稱或自訂名稱

### 命令列介面

#### 單一講者模式

```bash
# 使用預設提示（API 金鑰從 .env 讀取）
python gemini_tts_cli.py --prompt-type podcast --voice Kore -o podcast.wav

# 自訂文字
python gemini_tts_cli.py --text "歡迎使用 Gemini TTS！" --voice Puck -o welcome.wav

# 加入風格
python gemini_tts_cli.py --text "這是一個測試" --voice Enceladus --style "神秘的" -o mystery.wav

# 手動指定 API 金鑰（如果需要）
python gemini_tts_cli.py --api-key YOUR_API_KEY --text "測試" --voice Kore -o test.wav
```

#### 多講者模式

1. 建立對話範本：
```bash
python gemini_tts_cli.py --create-dialogue-template
```

2. 編輯 `dialogue_template.json` 檔案

3. 生成多講者語音：
```bash
python gemini_tts_cli.py --mode multi --dialogue dialogue_template.json -o dialogue.wav
```

#### 其他指令

```bash
# 列出所有可用語音
python gemini_tts_cli.py --list-voices

# 使用 Pro 模型
python gemini_tts_cli.py --model gemini-2.5-pro-preview-tts --text "測試" -o test.wav
```

## 支援的語音

系統提供 30 種不同風格的語音選項：

- **明亮型**：Zephyr, Autonoe
- **活潑型**：Puck, Laomedeia
- **資訊型**：Charon, Rasalgethi
- **堅定型**：Kore, Orus, Alnilam
- **其他風格**：Fenrir（興奮）、Enceladus（氣息感）、Algieba（流暢）等

## 支援的語言

- 中文（繁體/簡體）
- 英語（美國/印度）
- 日語、韓語
- 歐洲語言：法語、德語、西班牙語、義大利語等
- 亞洲語言：印尼語、泰語、越南語等
- 其他：阿拉伯語、印地語、孟加拉語等

## 對話檔案格式

多講者模式使用 JSON 格式：

```json
{
  "speakers": [
    {"name": "講者1", "voice": "Kore"},
    {"name": "講者2", "voice": "Puck"}
  ],
  "content": "講者1：對話內容\n講者2：回應內容"
}
```

## 注意事項

- TTS 模型目前為預覽版本，可能有使用限制
- 每次請求最多支援 8,000 個輸入 token
- 輸出音訊格式為 24kHz PCM，可儲存為 WAV 檔案
- 多講者模式最多支援 2 個講者

## 授權

MIT License 