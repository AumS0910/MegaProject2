@echo off
echo Starting all services...

:: Start T5 Server (Port 8003)
start cmd /k "python models/t5_server.py"

:: Start Stable Diffusion API (Port 7860)
start cmd /k "call models/start_sd_api.bat"

:: Start Brochure API (Port 8004)
start cmd /k "python api/brochure_api.py"

:: Start Trifold API (Port 8009)
start cmd /k "cd /d %~dp0 && python -m api.trifold_api"

:: Start Main Backend Server (Port 8006)
start cmd /k "python main.py"

echo Services started on:
echo T5 Server: http://localhost:8003
echo Stable Diffusion API: http://localhost:7860
echo Brochure API: http://localhost:8004
echo Trifold API: http://localhost:8009
echo Main Backend: http://localhost:8006
