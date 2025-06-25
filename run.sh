#!/bin/bash

# uv가 설치되어 있지 않으면 설치
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # PATH에 uv 추가 (현재 세션용)
    export PATH="$HOME/.cargo/bin:$PATH"
fi

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

# app.py 파일 존재 확인
if [ ! -f "./app.py" ]; then
    echo "Error: app.py file not found!"
    echo "Please create app.py file first."
    exit 1
fi

# Streamlit 애플리케이션 실행
echo "Starting Streamlit application..."
streamlit run ./app.py

# 가상환경 비활성화 (스크립트 종료 시 자동으로 비활성화됨)
deactivate
