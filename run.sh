#!/bin/bash

# 快速執行腳本 - 用於已設定好環境的情況

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 錯誤：未找到虛擬環境${NC}"
    echo "請先執行 ./start.sh 進行初始設定"
    exit 1
fi

# 啟動虛擬環境
source venv/bin/activate

# 檢查 .env 檔案
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  警告：未找到 .env 檔案${NC}"
    echo "請確保已設定 GEMINI_API_KEY"
fi

# 直接啟動 Streamlit
echo -e "${GREEN}🎙️  啟動 Gemini TTS 網頁介面...${NC}"
echo -e "${YELLOW}提示：按 Ctrl+C 停止伺服器${NC}\n"

streamlit run gemini_tts_app.py 