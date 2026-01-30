@echo off
color 0E
title HARD TO GET - LINK DIRETTO (NO INSTALL)
echo ====================================================
echo  IL MODO PIU SEMPLICE IN ASSOLUTO
echo ====================================================
echo.
echo 1. Lascia questo gioco aperto.
echo 2. Assicurati che il gioco (Frontend/Backend) sia avviato.
echo 3. Qui sotto apparira un link (es. vercel-clone.localhost.run).
echo.
echo COPIA QUEL LINK e mandalo ai tuoi amici.
echo.
echo Premi un tasto per andare online...
pause >nul

echo Connessione in corso...
echo Se e la prima volta, scrivi "yes" se te lo chiede.
echo.
echo IL LINK E NELLE ULTIME RIGHE (cerca http/https)
echo.

ssh -R 80:localhost:5173 nokey@localhost.run

pause
