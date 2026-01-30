@echo off
color 0A
title ELISE - HARD TO GET AI
echo ====================================================
echo  AVVIO CONNESSIONE ONLINE - HARD TO GET AI
echo ====================================================
echo.
echo 1. Il server di gioco e stato riavviato dall'AI.
echo 2. Ora avvieremo ngrok per mettere il gioco online.
echo.
echo ----------------------------------------------------
echo IMPORTANTE:
echo Apparira una schermata nera con scritto "Session Status: online"
echo Cerca la riga "Forwarding" e COPIA il link che finisce con .ngrok-free.dev
echo Esempio: https://abcdef123.ngrok-free.dev
echo.
echo Manda quel link ai tuoi amici (o provalo tu stesso)!
echo ----------------------------------------------------
echo.
echo Premi un tasto per avviare il tunnel...
pause >nul
ngrok http 5173
pause
