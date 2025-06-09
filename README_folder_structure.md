# 資料夾結構說明

## 專案目錄結構

```
geminitts/
├── output/                    # 所有生成的音訊檔案
│   ├── gemini_tts_*.wav      # TTS 生成的語音檔案
│   └── gemini_tts_*.pcm      # PCM 格式的語音檔案
│
├── voice_previews/           # 語音預覽檔案
│   └── preview_*.wav         # 各種語音的預覽檔案（35個）
│
├── gemini_tts_app.py         # 主應用程式
├── voice_preview_widget.py   # 語音預覽小工具
├── file_upload_module.py     # 檔案上傳模組
├── background_preview_generator.py  # 背景預覽生成器
│
├── generate_all_voice_previews.py   # 批量生成預覽腳本
├── test_pregenerated_previews.py    # 測試預覽生成腳本
│
├── .env                      # 環境變數（包含 API 金鑰）
├── .gitignore               # Git 忽略檔案
└── requirements.txt         # Python 依賴套件
```

## 資料夾用途說明

### output/
- **用途**：存放所有使用者生成的 TTS 音訊檔案
- **內容**：WAV 或 PCM 格式的語音檔案
- **命名**：`gemini_tts_YYYYMMDD_HHMMSS.wav`
- **Git**：已加入 .gitignore，不會被提交

### voice_previews/
- **用途**：存放語音預覽檔案，用於快速預覽功能
- **內容**：各種語音和語言的預覽音訊（目前有 35 個檔案）
- **命名**：`preview_{語音名稱}_{語言代碼}.wav`
- **功能**：實現零延遲的語音預覽播放
- **Git**：可以選擇提交到倉庫或使用 Git LFS

## 檔案管理建議

1. **定期清理**：
   - `output/` 資料夾：定期清理生成的 TTS 檔案
2. **備份重要檔案**：重要的生成檔案請及時下載或備份
3. **預覽檔案**：
   - `voice_previews/` 中的檔案應該保留，提供快速預覽功能
   - 可以使用 `generate_all_voice_previews.py` 生成更多語言的預覽

## 遷移說明

如果您有舊的音訊檔案在根目錄，可以手動移動到 output/ 資料夾：

```bash
# 移動所有 WAV 檔案到 output 資料夾
mv gemini_tts_*.wav output/ 2>/dev/null

# 移動所有 PCM 檔案到 output 資料夾  
mv gemini_tts_*.pcm output/ 2>/dev/null
``` 