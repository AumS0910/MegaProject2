@echo off
echo Starting Stable Diffusion WebUI with API enabled...

:: Set Python path and virtual environment
set PYTHON=python
set VENV_DIR=venv
set GIT=

:: Replace this path with your actual Stable Diffusion installation path
cd /d "E:\MegaProject\stable-diffusion-webui"
if errorlevel 1 (
    echo Failed to change directory to Stable Diffusion WebUI path
    pause
    exit /b 1
)

echo Current directory: %CD%

:: Activate virtual environment if it exists
if exist %VENV_DIR%\Scripts\activate.bat (
    echo Activating virtual environment...
    call %VENV_DIR%\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found at %VENV_DIR%
)

:: Check if Python is available
python --version
if errorlevel 1 (
    echo Error: Python not found
    pause
    exit /b 1
)

echo Starting Stable Diffusion WebUI...
echo Command: python webui.py --api --nowebui --skip-torch-cuda-test --skip-version-check --listen --port 7861

:: Start with API enabled
python webui.py --api --nowebui --skip-torch-cuda-test --skip-version-check --listen --port 7861

if errorlevel 1 (
    echo Error: Failed to start Stable Diffusion WebUI
    pause
    exit /b 1
)

pause
