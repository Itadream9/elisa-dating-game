@echo off
color 0D
title HARD TO GET - LINK DIRETTO
echo ====================================================
echo  CONDIVISIONE SEMPLICE (Localtunnel)
echo ====================================================
echo.
echo 1. Assicurati che il gioco sia GIA avviato (Backend e Frontend).
echo 2. Questo script creera un link pubblico.
echo.
echo Quando appare "your url is: ...", COPIA quel link.
echo.
echo Premi un tasto per generare il link...
pause >nul

echo Generazione in corso (puo richiedere la conferma "y" alla prima volta)...
call npx localtunnel --port 5173

pause
