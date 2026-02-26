@echo off
echo ========================================
echo Fake News Detector - Quick Start
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Check if dependencies are installed
if not exist "venv\Lib\site-packages\flask" (
    echo Installing dependencies...
    echo This may take 5-10 minutes on first run...
    pip install -r requirements.txt
    echo.
)

echo.
echo ========================================
echo Starting Fake News Detector...
echo ========================================
echo.
echo The application will open at:
echo http://localhost:5001
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python app.py

pause
