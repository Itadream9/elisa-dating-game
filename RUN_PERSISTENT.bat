@echo off
title HARD TO GET AI - LAUNCHER
color 0D

echo ===================================================
echo   AVVIO SERVER PERSISTENTE - HARD TO GET AI
echo ===================================================
echo.
echo Sto aprendo 3 finestre separate:
echo 1. SERVER BACKEND (Python/FastAPI)
echo 2. SERVER FRONTEND (Vite/React)
echo 3. NGROK (Tunnel Online)
echo.
echo NON CHIUDERE NESSUNA DELLE 3 FINESTRE!
echo.
echo Se vedi errori in una finestra, fammelo sapere.
echo.

:: 1. Start Backend
start "BACKEND - ELISA AI" cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

:: 2. Start Frontend
timeout /t 2 >nul
start "FRONTEND - GAME UI" cmd /k "cd frontend && npm run dev"

:: 3. Start Ngrok
timeout /t 4 >nul
echo.
echo Ora avvio Ngrok. 
echo 1. Cerca la riga "Forwarding" nella finestra blu/nera.
echo 2. Copia il link (es. https://xxxx.ngrok-free.dev).
echo 3. Usalo per giocare.
echo.
start "NGROK - ONLINE" cmd /k "ngrok http 5173"

echo SISTEMA AVVIATO.
echo Tieni questa finestra aperta se vuoi.
pause
