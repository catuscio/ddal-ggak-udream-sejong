#!/bin/bash

# 가상환경이 없으면 생성
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# 가상환경 활성화
source .venv/bin/activate

# 프로젝트 의존성 설치 및 업데이트
echo "Installing project dependencies..."
uv sync

# Streamlit 설치 확인 및 설치
echo "Checking Streamlit installation..."
if ! python -c "import streamlit" 2>/dev/null; then
    echo "Installing Streamlit..."
    uv add streamlit
fi

# Playwright 설치 확인 및 설치
echo "Checking Playwright installation..."
if ! python -c "import playwright" 2>/dev/null; then
    echo "Installing Playwright..."
    uv add playwright
fi

# Playwright 브라우저 바이너리 설치
echo "Installing Playwright browsers..."
python -m playwright install

# Streamlit 애플리케이션 실행
echo "Starting Streamlit application..."
streamlit run app.py

# 가상환경 비활성화
deactivate
