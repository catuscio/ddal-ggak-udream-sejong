@echo off

:: uv가 설치되어 있는지 확인
echo Checking uv installation...
where uv >nul 2>&1
IF ERRORLEVEL 1 (
    echo uv not found. Installing uv...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    :: PATH 새로고침을 위해 잠시 대기
    echo Please restart this script or refresh your terminal session.
    echo uv has been installed but may not be available in current session.
    pause
    exit /b 0
) ELSE (
    echo uv is already installed.
)
:: 가상환경이 없으면 생성
IF NOT EXIST .venv (
    echo Creating virtual environment...
    uv venv
)

:: 가상환경 활성화
call .venv\Scripts\activate.bat

:: 프로젝트 의존성 설치 및 업데이트
echo Installing project dependencies...
uv sync

:: Streamlit 설치 확인 및 설치
echo Checking Streamlit installation...
python -c "import streamlit" 2>nul
IF ERRORLEVEL 1 (
    echo Installing Streamlit...
    uv add streamlit
)

:: Playwright 설치 확인 및 설치
echo Checking Playwright installation...
python -c "import playwright" 2>nul
IF ERRORLEVEL 1 (
    echo Installing Playwright...
    uv add playwright
)

:: Playwright 브라우저 바이너리 설치
echo Installing Playwright browsers...
python -m playwright install

:: Streamlit 애플리케이션 실행
echo Starting Streamlit application...
streamlit run ./app.py

:: 가상환경 비활성화
call .venv\Scripts\deactivate.bat
