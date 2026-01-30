@echo off
color 0B
title HARD TO GET - CONDIVISIONE ONLINE
echo ====================================================
echo  CONDIVISIONE GIOCO CON AMICI
echo ====================================================
echo.
echo Questo script mettera il gioco online per i tuoi amici.
echo Assicurati che il gioco sia GIA avviato in un'altra finestra.
echo.
echo Stiamo usando un servizio di tunnel rapido.
echo.
echo Premi un tasto per generare il LINK...
pause >nul

echo.
echo Tentativo con Pinggy (Piu stabile, nessun account)...
echo Copia il link HTTP/HTTPS che apparira qui sotto.
echo.

ssh -p 443 -R0:localhost:5173 a.pinggy.io

pause
