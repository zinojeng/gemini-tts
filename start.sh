#!/bin/bash

# Gemini TTS 啟動腳本
# 自動設定虛擬環境、安裝套件並啟動應用程式

set -e  # 遇到錯誤時停止執行

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 顯示標題
echo -e "${GREEN}🎙️  Gemini TTS 啟動腳本${NC}"
echo "=================================="

# 檢查 Python 版本
echo -e "\n${YELLOW}檢查 Python 版本...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo -e "${RED}❌ 錯誤：需要 Python $required_version 或更高版本${NC}"
    echo "目前版本：$python_version"
    exit 1
fi
echo -e "${GREEN}✅ Python 版本符合要求：$python_version${NC}"

# 建立虛擬環境
VENV_DIR="venv"

if [ ! -d "$VENV_DIR" ]; then
    echo -e "\n${YELLOW}建立虛擬環境...${NC}"
    python3 -m venv $VENV_DIR
    echo -e "${GREEN}✅ 虛擬環境建立完成${NC}"
else
    echo -e "\n${GREEN}✅ 找到現有虛擬環境${NC}"
fi

# 啟動虛擬環境
echo -e "\n${YELLOW}啟動虛擬環境...${NC}"
source $VENV_DIR/bin/activate
echo -e "${GREEN}✅ 虛擬環境已啟動${NC}"

# 升級 pip
echo -e "\n${YELLOW}升級 pip...${NC}"
pip install --upgrade pip --quiet

# 安裝相依套件
echo -e "\n${YELLOW}安裝相依套件...${NC}"
pip install -r requirements.txt --quiet
echo -e "${GREEN}✅ 套件安裝完成${NC}"

# 檢查 .env 檔案
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}未找到 .env 檔案${NC}"
    echo "是否要建立 .env 檔案？(y/n)"
    read -r create_env
    
    if [ "$create_env" = "y" ] || [ "$create_env" = "Y" ]; then
        echo "請輸入您的 Gemini API 金鑰："
        read -r api_key
        
        cat > .env << EOF
# Gemini API Configuration
GEMINI_API_KEY=$api_key

# Optional: Default Model Selection
# GEMINI_TTS_MODEL=gemini-2.5-flash-preview-tts

# Optional: Default Voice
# GEMINI_DEFAULT_VOICE=Kore

# Optional: Default Language
# GEMINI_DEFAULT_LANGUAGE=zh-TW
EOF
        echo -e "${GREEN}✅ .env 檔案已建立${NC}"
    else
        echo -e "${RED}⚠️  警告：沒有 .env 檔案，請確保設定 API 金鑰${NC}"
    fi
else
    echo -e "\n${GREEN}✅ 找到 .env 檔案${NC}"
fi

# 顯示選項
echo -e "\n${GREEN}準備就緒！請選擇要執行的模式：${NC}"
echo "=================================="
echo "1) 網頁介面 (Streamlit)"
echo "2) 命令列工具"
echo "3) 快速測試"
echo "4) 設定助手"
echo "5) 退出"
echo "=================================="

read -p "請輸入選項 (1-5): " choice

case $choice in
    1)
        echo -e "\n${YELLOW}啟動 Streamlit 網頁介面...${NC}"
        echo -e "${GREEN}提示：按 Ctrl+C 停止伺服器${NC}\n"
        streamlit run gemini_tts_app.py
        ;;
    2)
        echo -e "\n${YELLOW}命令列工具使用範例：${NC}"
        echo "單一講者："
        echo "  python gemini_tts_cli.py --text '你好，歡迎使用 Gemini TTS！' --voice Kore -o welcome.wav"
        echo ""
        echo "多講者："
        echo "  python gemini_tts_cli.py --mode multi --dialogue dialogue_example.json -o dialogue.wav"
        echo ""
        echo "列出所有語音："
        echo "  python gemini_tts_cli.py --list-voices"
        echo ""
        echo -e "${GREEN}提示：使用 'python gemini_tts_cli.py -h' 查看所有選項${NC}"
        ;;
    3)
        echo -e "\n${YELLOW}執行快速測試...${NC}"
        python test_tts.py
        ;;
    4)
        echo -e "\n${YELLOW}執行設定助手...${NC}"
        python setup.py
        ;;
    5)
        echo -e "\n${GREEN}再見！${NC}"
        exit 0
        ;;
    *)
        echo -e "\n${RED}無效的選項${NC}"
        exit 1
        ;;
esac

# 保持虛擬環境啟動（如果使用者想要繼續操作）
echo -e "\n${YELLOW}虛擬環境仍在啟動中。${NC}"
echo "您可以繼續執行其他命令，或輸入 'deactivate' 退出虛擬環境。" 