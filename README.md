# Elisa - Hard to Get AI Dating Simulator

Un gioco multiplayer competitivo dove i giocatori cercano di conquistare Elisa, un'AI incredibilmente difficile da impressionare.

## 🎮 Come Giocare

- Ogni giocatore inizia con **€10.00**
- Ogni messaggio costa **€0.30**
- Convincere Elisa ad accettare un appuntamento → **JACKPOT** (€1000+)
- Se finisci i soldi → **GAME OVER**

## 🚀 Deploy

Il gioco è hostato su Render.com. Vedi [DEPLOY_RENDER.md](DEPLOY_RENDER.md) per istruzioni.

## 🛠️ Tech Stack

- **Frontend**: React + Vite + Tailwind CSS + Framer Motion + Socket.IO
- **Backend**: FastAPI + Socket.IO + DeepSeek AI
- **Database**: SQLite
- **Real-Time**: WebSocket

## 💻 Sviluppo Locale

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📝 License

MIT
