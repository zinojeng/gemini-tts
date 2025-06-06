# Gemini TTS 專案結構

## 檔案說明

### 核心程式
- `gemini_tts_app.py` - Streamlit 網頁介面主程式
- `gemini_tts_cli.py` - 命令列工具
- `test_tts.py` - 快速測試腳本

### 設定檔案
- `.env` - 環境變數檔案（包含 API 金鑰）
- `requirements.txt` - Python 套件相依性
- `dialogue_example.json` - 多講者對話範例

### 啟動腳本
- `start.sh` - 初始設定腳本（建立虛擬環境、安裝套件）
- `run.sh` - 快速執行腳本（直接啟動網頁介面）
- `setup.py` - 設定助手（互動式設定）

### 其他檔案
- `.gitignore` - Git 忽略檔案設定
- `README.md` - 專案說明文件
- `PROJECT_STRUCTURE.md` - 本檔案

### 目錄
- `venv/` - Python 虛擬環境（由 start.sh 自動建立）

## 快速使用

1. **第一次使用**：
   ```bash
   ./start.sh
   ```

2. **之後使用**：
   ```bash
   ./run.sh
   ```

3. **命令列模式**：
   ```bash
   source venv/bin/activate
   python gemini_tts_cli.py --text "測試文字" -o output.wav
   ``` 