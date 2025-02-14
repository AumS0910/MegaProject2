@echo off
echo Starting AI Brochure Generation Services...

:: Start T5 Server (Port 8003)
start cmd /k "python models/t5_server.py"

:: Start Stable Diffusion API (Port 7860)
start cmd /k "call models/start_sd_api.bat"

:: Start Brochure API (Port 8004)
start cmd /k "python api/brochure_api.py"

:: Start Main Backend Server (Port 8006)
start cmd /k "python main.py"

echo All services started!
echo T5 Server: http://localhost:8003
echo Stable Diffusion API: http://localhost:7860
echo Brochure API: http://localhost:8004
echo Main Backend: http://localhost:8006
