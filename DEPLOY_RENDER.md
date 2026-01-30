# 🚀 GUIDA DEPLOYMENT RENDER.COM

## Perché Render?
- ✅ **Gratuito** per sempre
- ✅ **Link permanente** (es. `elisa-game.onrender.com`)
- ✅ **Zero sbattimenti** (deploy automatico da GitHub)
- ✅ **HTTPS** incluso
- ✅ Non devi tenere il PC acceso

---

## 📋 PASSAGGI (5 Minuti)

### 1️⃣ Crea Account GitHub (se non ce l'hai)
👉 Vai su [github.com](https://github.com) e registrati (gratis)

### 2️⃣ Carica il Progetto su GitHub

**Opzione A: Usando GitHub Desktop (Più Facile)**
1. Scarica [GitHub Desktop](https://desktop.github.com/)
2. Apri GitHub Desktop
3. Click su `File` → `Add Local Repository`
4. Seleziona la cartella: `C:\Users\robya\Desktop\Nuova cartella (17)`
5. Click su `Publish repository`
6. Dai un nome: `elisa-dating-game`
7. ✅ Lascia **Public** (Render richiede repo pubblico per piano free)
8. Click `Publish`

**Opzione B: Da Riga di Comando** (se preferisci)
```bash
cd "C:\Users\robya\Desktop\Nuova cartella (17)"
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TUO_USERNAME/elisa-dating-game.git
git push -u origin main
```

### 3️⃣ Crea Account Render
👉 Vai su [render.com](https://render.com)
- Click `Get Started for Free`
- Registrati con GitHub (autorizza accesso)

### 4️⃣ Deploy Backend

1. Nel Dashboard Render, click `New +` → `Web Service`
2. Connetti il repository `elisa-dating-game`
3. Configura:
   - **Name**: `elisa-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn main:socket_app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
4. Click su `Advanced` → `Add Environment Variable`:
   - Key: `DEEPSEEK_API_KEY`
   - Value: `sk-05b9143a26414f82be9fbd3c0229fff2`
5. Click `Create Web Service`
6. ⏳ Aspetta il deploy (2-3 minuti)
7. ✅ Copia l'URL generato (es. `https://elisa-backend-abc123.onrender.com`)

### 5️⃣ Deploy Frontend

1. Nel Dashboard, click `New +` → `Static Site`
2. Scegli di nuovo il repository `elisa-dating-game`
3. Configura:
   - **Name**: `elisa-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. Click su `Advanced` → `Add Environment Variable`:
   - Key: `VITE_API_URL`
   - Value: `https://elisa-backend-abc123.onrender.com` (l'URL del backend)
5. Click `Create Static Site`
6. ⏳ Aspetta il build (3-5 minuti)

### 6️⃣ Configura CORS (Importante!)

Torna al Backend su Render:
1. Vai su `Environment` tab
2. Aggiungi variabile:
   - Key: `FRONTEND_URL`
   - Value: `https://elisa-frontend.onrender.com` (il tuo URL frontend)
3. Riavvia il servizio

---

## 🎉 FATTO!

Il tuo gioco è ONLINE al link:
```
https://elisa-frontend.onrender.com
```

Condividi questo link su Discord, funziona per tutti!

---

## ⚠️ NOTA IMPORTANTE: Free Tier

Render Free spegne i server dopo 15 minuti di inattività.
Il primo accesso dopo inattività richiede ~30 secondi per "svegliare" il server.

**Soluzione**: Usa [UptimeRobot](https://uptimerobot.com) (gratis) per pingare il backend ogni 10 minuti e tenerlo sempre attivo.

---

## 🔧 Aggiornamenti Futuri

Ogni volta che modifichi il codice:
1. Vai su GitHub Desktop
2. Scrivi un messaggio di commit (es. "Fix bug")
3. Click `Commit to main`
4. Click `Push origin`
5. ✅ Render rileva il push e fa il deploy automaticamente!

---

## 🆘 Problemi?

**Backend non parte?**
- Controlla i logs: Dashboard → elisa-backend → Logs
- Verifica che `DEEPSEEK_API_KEY` sia impostata

**Frontend non si connette?**
- Verifica che `VITE_API_URL` punti al backend corretto
- Controlla CORS nel backend

**Audio non funziona?**
- pyttsx3 non è supportato su Render (serve sistema locale)
- L'audio funzionerà solo se elimini il TTS o usi Edge TTS (online)
