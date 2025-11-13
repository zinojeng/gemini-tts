# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A multilingual Text-to-Speech (TTS) application using Google Gemini API, supporting both single-speaker and multi-speaker dialogue modes with 30+ voice options and 24+ languages. Provides both a Streamlit web interface and CLI tool.

**Deployment**: Designed for Zeabur cloud deployment with ephemeral filesystem considerations. See [Deployment](#deployment) section for critical setup steps.

**Key Feature**: 3-tier voice preview caching system optimized for cloud environments - pregenerate and commit `voice_previews/` directory to avoid cold start delays and API quota consumption.

## Core Architecture

### Main Application Files

- **[gemini_tts_app.py](gemini_tts_app.py)** - Streamlit web UI (867 lines)
  - Entry point: `main()` function
  - Manages session state for voice preview caching
  - Handles both single and multi-speaker TTS generation
  - Integrates voice preview, file upload, and dialogue generation modules

- **[gemini_tts_cli.py](gemini_tts_cli.py)** - Command-line interface (231 lines)
  - Supports single-speaker: `--text`, `--voice`, `--style` parameters
  - Supports multi-speaker: `--mode multi --dialogue <json_file>`
  - Template generation: `--create-dialogue-template`

### Module Architecture

**Voice Preview System** (3-tier caching strategy):
1. **[voice_preview_widget.py](voice_preview_widget.py)** - UI components for voice selection with inline preview buttons
2. **[background_preview_generator.py](background_preview_generator.py)** - Background thread generation on app startup
3. Cache hierarchy:
   - Pregenerated files in `voice_previews/` directory (checked first)
   - Session state cache (`st.session_state.voice_previews`)
   - Local `.wav` files (`preview_{voice}_{language}.wav`)

**File Processing Module**:
- **[file_upload_module.py](file_upload_module.py)** - Parses SRT subtitles and text files
  - `parse_srt_file()` - Extracts dialogue from SRT format
  - `parse_text_file()` - Auto-detects speakers using "Speaker:" format
  - `format_dialogues_for_display()` - Formats for UI display

### API Integration Pattern

All TTS generation uses this Gemini API structure:

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=api_key)

# Single-speaker config
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

# Multi-speaker config
config = types.GenerateContentConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
            speaker_voice_configs=[
                types.SpeakerVoiceConfig(
                    speaker="講者1",
                    voice_config=types.VoiceConfig(...)
                ),
                # ... more speakers
            ]
        )
    )
)

response = client.models.generate_content(
    model=model_name,  # "gemini-2.5-flash-preview-tts" or "gemini-2.5-pro-preview-tts"
    contents=prompt_text,
    config=config
)

audio_data = response.candidates[0].content.parts[0].inline_data.data
```

### Multi-Speaker Dialogue Processing

Critical flow in [gemini_tts_app.py](gemini_tts_app.py):

1. **Text Cleaning** (`clean_dialogue_text()` at line 211):
   - Removes non-dialogue lines
   - Auto-detects actual speaker names if using defaults ("講者1", "講者2")
   - Returns cleaned text and updated speaker list

2. **Style Application** (`apply_styles_to_dialogue()` at line 248):
   - Adds style instructions per speaker: `[興奮的, 快速地] 講者1：對話內容`

3. **Prompt Construction** (line 774-788):
   - Prepends style instructions: `講者1用興奮的語氣說話；講者2用平靜的語氣說話。`
   - Adds "TTS 以下對話：" prefix before dialogue content

4. **Speaker Validation** (line 725-728):
   - Checks if cleaned text is empty (indicates speaker name mismatch)
   - Common error: speaker names in text don't match configured speakers

### Dialogue Format Examples

**JSON format** (for CLI `--dialogue` parameter):
```json
{
  "speakers": [
    {"name": "主持人", "voice": "Kore"},
    {"name": "嘉賓", "voice": "Puck"}
  ],
  "content": "主持人：歡迎來到節目\n嘉賓：謝謝邀請"
}
```

**Text format** (for file upload):
```
講者A：這是第一句話
講者B：這是回應
講者A：繼續對話
```

## Deployment

### Zeabur Deployment

**Primary Deployment Target**: This app is designed for deployment on Zeabur.

**Quick Deployment Checklist**:
1. ✅ **Voice previews already included**: This repository includes 35 pregenerated preview files in `voice_previews/` (zh-TW language)
2. ✅ Verify previews are committed: `git ls-files voice_previews/*.wav` should show 35 files
3. ✅ Set `GEMINI_API_KEY` in Zeabur dashboard (Environment Variables section)
4. ✅ Connect GitHub repository to Zeabur
5. ✅ Deploy from Zeabur dashboard (auto-detects Streamlit, uses default start command)
6. ✅ Verify deployment: Check sidebar - should **not** show "正在背景生成預覽..." message
7. ✅ Test voice preview buttons - should play instantly without API calls

**If adding new language support**: Regenerate previews for new language and commit:
```bash
python generate_all_voice_previews.py  # Prompts for language selection
git add voice_previews/preview_*_<language>.wav
git commit -m "Add voice previews for <language>"
git push
```

**Start Command** (auto-detected by Zeabur for Streamlit apps):
```bash
streamlit run gemini_tts_app.py --server.port $PORT --server.address 0.0.0.0
```

**Required Environment Variables** (configure in Zeabur dashboard):
```bash
GEMINI_API_KEY=your_api_key_here  # Required - get from https://makersuite.google.com/app/apikey
```

**Optional Environment Variables**:
```bash
GEMINI_TTS_MODEL=gemini-2.5-flash-preview-tts  # Default model (optional)
GEMINI_DEFAULT_VOICE=Kore                       # Default voice (optional)
GEMINI_DEFAULT_LANGUAGE=zh-TW                   # Default language (optional)
```

**Critical Zeabur Considerations**:

1. **Ephemeral Filesystem**:
   - `output/` directory and runtime-generated preview files are **temporary**
   - Users must download generated audio files immediately via download button
   - Files will be lost when container restarts

2. **Voice Preview Strategy**:
   - **Best Practice**: Pregenerate all voice previews locally and commit `voice_previews/` directory
   - Run locally: `python generate_all_voice_previews.py`
   - Commit generated files: `git add voice_previews/*.wav && git commit -m "Add pregenerated voice previews"`
   - This reduces cold start time and API quota usage in production

3. **Background Threads**:
   - `background_preview_generator.py` uses daemon threads (line 61) - safe for cloud deployment
   - Background generation continues if previews not pregenerated
   - Progress shown in sidebar (line 138-141)

4. **Memory Caching**:
   - Session state (`st.session_state.voice_previews`) caches audio data in memory
   - Cache is per-user session, cleared on browser refresh
   - Reduces redundant API calls during active session

5. **Port Configuration**:
   - App automatically uses Zeabur's `$PORT` environment variable
   - Default Streamlit port is 8501 if `$PORT` not set

**Optional Dockerfile** (if custom build needed):
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directory (will be ephemeral)
RUN mkdir -p output

# Expose Streamlit default port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "gemini_tts_app.py", \
     "--server.port", "8501", \
     "--server.address", "0.0.0.0", \
     "--server.headless", "true"]
```

**Performance Tips for Production**:
- Enable Streamlit caching for API responses (already implemented via session state)
- Consider increasing Streamlit's `server.maxUploadSize` if processing large text files
- Monitor API quota usage in Google AI Studio dashboard

### Local Development

#### Environment Setup
```bash
# First-time setup (creates venv, installs packages, configures .env)
./start.sh

# Quick launch (assumes setup is complete)
./run.sh

# Manual setup
python setup.py
```

#### Running the Application
```bash
# Web interface (local)
streamlit run gemini_tts_app.py

# CLI - single speaker
python gemini_tts_cli.py --text "測試文字" --voice Kore -o output.wav

# CLI - multi-speaker
python gemini_tts_cli.py --mode multi --dialogue dialogue_example.json -o output.wav

# List available voices
python gemini_tts_cli.py --list-voices

# Create dialogue template
python gemini_tts_cli.py --create-dialogue-template
```

#### Testing
```bash
# Quick TTS test
python test_tts.py

# Test voice preview functionality
python test_voice_preview.py

# Test cache performance
python test_cache_performance.py

# Generate all voice previews
python generate_all_voice_previews.py
```

## Configuration

### Environment Variables (.env)
```bash
GEMINI_API_KEY=your_api_key_here          # Required
GEMINI_TTS_MODEL=gemini-2.5-flash-preview-tts  # Optional
GEMINI_DEFAULT_VOICE=Kore                 # Optional
GEMINI_DEFAULT_LANGUAGE=zh-TW             # Optional
```

Get API key from: https://makersuite.google.com/app/apikey

### Voice Options
30 prebuilt voices defined in `VOICE_OPTIONS` dict (line 24 in [gemini_tts_app.py](gemini_tts_app.py)):
- Categorized by style: Bright (Zephyr, Autonoe), Upbeat (Puck, Laomedeia), Firm (Kore, Orus, Alnilam), etc.
- Each voice has Chinese description for UI display

### Supported Languages
24 languages in `SUPPORTED_LANGUAGES` dict (line 58):
- Chinese: zh-TW, zh-CN
- Major Asian: ja-JP, ko-KR, hi-IN, th-TH, vi-VN, id-ID
- European: en-US, en-IN, fr-FR, de-DE, es-US, it-IT, pt-BR, ru-RU, nl-NL, pl-PL, tr-TR, ro-RO, uk-UA
- South Asian: bn-BD, mr-IN, ta-IN, te-IN

## Common Development Patterns

### Adding a New Voice
1. Add to `VOICES` list in [gemini_tts_cli.py](gemini_tts_cli.py) (line 21)
2. Add to `VOICE_OPTIONS` dict in [gemini_tts_app.py](gemini_tts_app.py) (line 24)
3. Voice must exist in Gemini API's prebuilt voice list

### Adding a New Language
1. Add to `SUPPORTED_LANGUAGES` dict in [gemini_tts_app.py](gemini_tts_app.py) (line 58)
2. Optionally add preview text in `generate_voice_preview()` (line 160)

### Modifying Prompt Templates
Prompt examples in `PROMPT_EXAMPLES` dict (line 94 in [gemini_tts_app.py](gemini_tts_app.py)):
- Categories: "播客對話", "有聲書朗讀", "客服對話", "教育內容"
- Each has "single" and "multi" variants
- Dynamic suggestions in `generate_prompt_suggestion()` (line 273) - adds progressive content

### Session State Management
Key session state variables:
- `voice_previews` - Audio data cache for previews
- `preview_generation_thread` - Background generation thread reference
- `selected_language` - Current language selection
- `single_text_content` / `multi_text_content` - Text area content persistence

## Output Structure

**Local Development**:
```
output/                      # Generated TTS files (gitignored)
  gemini_tts_YYYYMMDD_HHMMSS.wav

voice_previews/              # Pregenerated preview files (SHOULD BE COMMITTED)
  preview_{voice}_{language}.wav

preview_{voice}_{language}.wav  # Runtime-generated previews (root directory, gitignored)

.env                         # API credentials (gitignored, local only)
```

**Zeabur Production**:
```
output/                      # Ephemeral - cleared on restart
  gemini_tts_YYYYMMDD_HHMMSS.wav

voice_previews/              # Persistent (if committed to git) - RECOMMENDED
  preview_{voice}_{language}.wav

preview_{voice}_{language}.wav  # Ephemeral - generated at runtime if voice_previews/ missing
```

**Important**: On Zeabur, only files committed to git repository are persistent. All runtime-generated files in `output/` and root directory are ephemeral and lost on container restart. **Always commit `voice_previews/*.wav` for production deployments**.

## Dependencies

**Core** (from [requirements.txt](requirements.txt)):
- `google-genai>=0.1.0` - Gemini API client
- `streamlit>=1.28.0` - Web UI framework
- `python-dotenv>=1.0.0` - Environment variable management

**Standard library**: wave, argparse, json, threading, re

## Debugging Tips

### Multi-Speaker Dialogue Issues

**Problem**: "API 回應中沒有音訊資料" error
- **Cause**: Speaker names in dialogue text don't match configured speaker names
- **Solution**: Use the debug expander (line 731: "調試信息 - 清理後的對話文本") to verify:
  1. Cleaned dialogue text is not empty
  2. Speaker names match between text and configuration
  3. Text uses colon separator ("：" or ":") after speaker names

**Problem**: Empty cleaned dialogue
- **Cause**: Speaker name format not recognized
- **Solution**: Ensure format is `講者名稱：對話內容` with colon immediately after name

### Voice Preview Issues

**Problem**: Preview button needs two clicks
- **Fixed**: Now uses HTML5 audio element with autoplay (line 164-179 in [voice_preview_widget.py](voice_preview_widget.py))

**Problem**: Slow preview generation
- **Solution**: Run `python generate_all_voice_previews.py` to pregenerate all previews
- Or let background generation complete after app startup

### API Connection Issues

**Problem**: Authentication errors
- **Local**: Check `.env` file exists and has valid `GEMINI_API_KEY`
- **Zeabur**: Verify environment variable set in Zeabur dashboard (not `.env` file)
- Use `python check_env.py` to verify environment (local only)

**Problem**: Model not found
- Ensure using supported models: `gemini-2.5-flash-preview-tts` or `gemini-2.5-pro-preview-tts`

### Zeabur-Specific Issues

**Problem**: Voice previews regenerate every time (slow cold start)
- **Cause**: `voice_previews/` directory not committed to repository
- **Solution**:
  1. Generate locally: `python generate_all_voice_previews.py`
  2. Update [.gitignore](.gitignore) to allow `voice_previews/*.wav` (line 27 already configured)
  3. Commit: `git add voice_previews/*.wav && git commit && git push`

**Problem**: Generated audio files disappear after download
- **Expected Behavior**: This is normal - ephemeral filesystem
- **Solution**: Users must download immediately; files stored in `output/` are temporary

**Problem**: Session state cleared unexpectedly
- **Cause**: Browser refresh or Zeabur container restart
- **Impact**: Voice preview cache in `st.session_state.voice_previews` is lost
- **Mitigation**: Pregenerate and commit `voice_previews/` directory

**Problem**: Port binding errors in logs
- **Cause**: Missing `$PORT` environment variable configuration
- **Solution**: Ensure start command uses `--server.port $PORT` (Zeabur auto-configures)

**Problem**: High API quota usage
- **Cause**: Voice previews regenerating on every session
- **Solution**: Commit pregenerated previews (30 voices × selected language = 30 API calls saved per deployment)

## API Limits & Considerations

- Max input: 8,000 tokens per request
- Output format: 24kHz PCM, 16-bit, mono/stereo
- Multi-speaker mode: Maximum 2 speakers
- TTS models are preview versions - expect potential API changes
- Rate limiting: Background preview generator includes 0.5s delay between requests (line 55 in [background_preview_generator.py](background_preview_generator.py))

## Code Style Notes

- Chinese comments and UI strings (Traditional Chinese primary)
- Emoji prefixes in UI messages and section headers
- Error messages use ❌, warnings use ⚠️, success uses ✅
- Function docstrings in Chinese
- Use `st.spinner()` for operations >1 second
- Audio files saved to `output/` directory with timestamp naming

## Author

**Tseng Yao Hsien, MD**
Endocrinologist
Tungs' Taichung MetroHarbor Hospital
