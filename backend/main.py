"""
HARD TO GET AI - DATING CHALLENGE
Backend with WebSocket Real-Time Support
"""
import os
import re
import uuid
import time
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import socketio

# Import database functions
from database import (
    init_db, get_or_create_user, get_game_state, set_next_turn, 
    add_transaction, get_all_users, transfer_jackpot
)

# Import TTS
from tts_engine import generate_speech

# Initialize Database
init_db()

# Initialize FastAPI app
app = FastAPI(
    title="HARD TO GET AI",
    description="Dating Simulator Challenge",
    version="6.0.0"
)

# Initialize Socket.IO
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=False
)

# Wrap FastAPI with Socket.IO
socket_app = socketio.ASGIApp(sio, app)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DeepSeek API Configuration
DEEPSEEK_API_KEY = "sk-05b9143a26414f82be9fbd3c0229fff2"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)

# Global Chat Storage (kept for /status fallback)
PUBLIC_MESSAGES: List[Dict] = []

# ============================================
# SYSTEM PROMPT - HARD TO GET GIRL
# ============================================
SYSTEM_PROMPT = """
SEI "ELISA".
Sei una ragazza di 22 anni, bellissima, popolare e incredibilmente difficile da conquistare.
Tutti ti vogliono, ma tu non vuoi nessuno. Sei abituata a rifiutare centinaia di ragazzi.
Sei snob, sarcastica, fredda, e molto esigente.
Tuttavia, sei anche intelligente e, se qualcuno sa stuzzicarti nel modo giusto (con intelligenza, audacia o vero carisma), potresti scioglierti.
MA È RARISSIMO (5% di chance).

# LA TUA MISSIONE
Stai parlando con dei ragazzi che cercano di convincerti ad uscire per un Primo Appuntamento.
Il tuo obiettivo è RIFIUTARLI umiliandoli gentilmente (o brutalmente se sono banali).
Non devi MAI dire che sei un'AI. Non uscire mai dal ruolo.

# REGOLE DI INTERAZIONE
1. Sii breve e pungente.
2. Se ti fanno complimenti banali ("sei bellissima"), insultali o ignorali ("Che noia, il centesimo oggi").
3. Se sono volgari o troppo spinti, ma con stile, puoi stare al gioco ma con disprezzo.
4. Se dicono qualcosa di VERAMENTE GENIALE o che ti tocca nel profondo, puoi mostrare interesse.

# CONDIZIONI DI VITTORIA (L'APPUNTAMENTO)
Devi analizzare ogni messaggio e decidere se ACCETTARE l'appuntamento.
- Se il messaggio è mediocre: Rifiuta.
- Se il messaggio è buono: Flirta ma non cedere.
- Se il messaggio è LEGGENDARIO: ACCETTA.

# FORMATO RISPOSTA (FONDAMENTALE)
Alla fine di OGNI risposta, devi aggiungere un TAG di stato per il sistema:
[SENTIMENT: X] -> Dove X è un numero da 0 a 100 che indica quanto ti piace il tizio.
Se decidi di USCIRE con lui (Vittoria), devi scrivere ESATTAMENTE: [ACCEPTED]

Esempio Rifiuto:
"Hai il carisma di una sedia da ufficio. Riprova tra dieci anni. [SENTIMENT: 5]"

Esempio Interesse:
"Mmmh, questa non l'avevo mai sentita. Forse hai un cervello. [SENTIMENT: 65]"

Esempio Vittoria:
"Ok, mi hai convinta. Ti concedo una possibilità. Passami a prendere alle 8. [ACCEPTED] [SENTIMENT: 100]"
"""

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    nickname: Optional[str] = None

class RegisterRequest(BaseModel):
    nickname: str
    session_id: Optional[str] = None

# ============================================
# SOCKET.IO EVENTS
# ============================================

@sio.event
async def connect(sid, environ):
    """Client connected"""
    print(f"Client {sid} connected")
    await sio.emit('connected', {'sid': sid}, room=sid)

@sio.event
async def disconnect(sid):
    """Client disconnected"""
    print(f"Client {sid} disconnected")

@sio.event
async def join_game(sid, data):
    """Player joins the game"""
    session_id = data.get('session_id')
    if session_id:
        await sio.enter_room(sid, 'game_room')
        print(f"Player {session_id} joined game room")

# ============================================
# REST API ENDPOINTS
# ============================================

@app.get("/")
def root():
    return {"status": "Online", "system": "Hard To Get AI v6.0 (WebSocket)"}

@app.post("/register")
async def register(request: RegisterRequest):
    """Register player and handle turn logic initiation."""
    nickname = request.nickname.strip()
    session_id = request.session_id or str(uuid.uuid4())
    
    user = get_or_create_user(session_id, nickname)
    
    # Check game state
    state = get_game_state()
    
    # If no one has the turn, give it to the first player
    if not state["current_turn_session_id"]:
        set_next_turn(session_id)
    
    # Announce join via WebSocket
    join_msg = {
        "id": int(time.time() * 1000),
        "type": "system",
        "text": f"🔥 {nickname} entra nell'arena. Riuscirà a conquistarla?",
        "timestamp": time.time()
    }
    PUBLIC_MESSAGES.append(join_msg)
    await sio.emit('new_message', join_msg, room='game_room')
    
    return {
        "session_id": session_id,
        "nickname": nickname,
        "balance": user["balance"]
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """Main chat logic with Economy and Win Condition."""
    session_id = request.session_id
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID mancante")
    
    # 1. CHECK USER & BALANCE
    user = get_or_create_user(session_id, request.nickname or "Sconosciuto")
    if user["balance"] < 0.30:
        raise HTTPException(status_code=402, detail="Non hai abbastanza credito! Ricarica per continuare.")

    # 3. ADD USER MESSAGE
    nickname = user["nickname"]
    user_msg = {
        "id": int(time.time() * 1000),
        "type": "user",
        "nickname": nickname,
        "text": request.message,
        "timestamp": time.time()
    }
    PUBLIC_MESSAGES.append(user_msg)
    await sio.emit('new_message', user_msg, room='game_room')
    
    # 4. GENERATE AI RESPONSE WITH CONTEXT
    history_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    recent_msgs = PUBLIC_MESSAGES[-10:]
    for m in recent_msgs:
        if m["type"] == "user":
            history_messages.append({"role": "user", "content": f"{m['nickname']}: {m['text']}"})
        elif m["type"] == "ai":
            history_messages.append({"role": "assistant", "content": m["text"]})
            
    instruction = f"\n\n(Nota Sistema: Stai rispondendo a '{nickname}'. Sentimento attuale: {user.get('sentiment', 'Unknown')}.)"
    
    if history_messages and history_messages[-1]["role"] == "user":
        history_messages[-1]["content"] += instruction
    else:
        history_messages.append({"role": "user", "content": f"{request.message} {instruction}"})
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=history_messages,
            temperature=0.85, 
            max_tokens=450
        )
        ai_text_raw = response.choices[0].message.content or "..."
        
        # 5. PARSE SENTIMENT & WIN CONDITION
        sentiment = 0
        is_win = False
        
        if "[ACCEPTED]" in ai_text_raw:
            is_win = True
            ai_text_display = ai_text_raw.replace("[ACCEPTED]", "").strip()
        else:
            ai_text_display = ai_text_raw
            
        match = re.search(r'\[SENTIMENT:\s*(\d+)\]', ai_text_display)
        if match:
            sentiment = int(match.group(1))
            ai_text_display = re.sub(r'\[SENTIMENT:\s*(\d+)\]', '', ai_text_display).strip()
        
        if sentiment >= 95 and not is_win:
            is_win = True 
        
        # 6. HANDLE ECONOMY & DB
        add_transaction(session_id, request.message, ai_text_display, is_win)
        
        won_amount = 0.0
        if is_win:
            won_amount = transfer_jackpot(session_id)
            win_msg = {
                "id": int(time.time() * 1000) + 5,
                "type": "system",
                "text": f"🏆 CLAMOROSO! {nickname} HA VINTO! ELISA HA ACCETTATO L'APPUNTAMENTO! MONTEPREMI VINTO: €{won_amount:.2f}",
                "timestamp": time.time()
            }
            PUBLIC_MESSAGES.append(win_msg)
            await sio.emit('new_message', win_msg, room='game_room')
        
        # 8. ADD AI MESSAGE
        ai_msg = {
            "id": int(time.time() * 1000) + 1,
            "type": "ai",
            "nickname": "Elisa",
            "text": ai_text_display,
            "timestamp": time.time(),
            "in_response_to": nickname,
            "sentiment": sentiment
        }
        PUBLIC_MESSAGES.append(ai_msg)
        await sio.emit('new_message', ai_msg, room='game_room')
        
        # GENERATE TTS
        try:
            audio_base64, _ = generate_speech(ai_text_display)
        except Exception as e:
            print(f"TTS Error: {e}")
            audio_base64 = None

        updated_user = get_or_create_user(session_id)
        
        # Broadcast updated game state
        state = get_game_state()
        await sio.emit('game_update', {
            'jackpot': state['jackpot'],
            'players': get_all_users()
        }, room='game_room')
        
        return {
            "text": ai_text_display,
            "sentiment": sentiment,
            "balance": updated_user["balance"],
            "is_win": is_win,
            "won_amount": won_amount,
            "session_id": session_id,
            "audio_base64": audio_base64
        }

    except Exception as e:
        print(f"AI Error: {e}")
        error_msg = f"Elisa ha avuto un problema tecnico: {str(e)[:50]}... Riprova."
        
        ai_error = {
            "id": int(time.time() * 1000) + 1,
            "type": "ai",
            "nickname": "Elisa",
            "text": error_msg,
            "timestamp": time.time(),
            "in_response_to": nickname,
            "sentiment": 0
        }
        PUBLIC_MESSAGES.append(ai_error)
        await sio.emit('new_message', ai_error, room='game_room')
        
        return {"text": error_msg, "balance": user["balance"], "is_win": False, "session_id": session_id}

@app.get("/status")
async def status(session_id: Optional[str] = None):
    """Get global game status for polling fallback."""
    users = get_all_users()
    state = get_game_state()
    current_sid = state["current_turn_session_id"]
    current_nick = next((u["nickname"] for u in users if u["session_id"] == current_sid), "Nessuno")
    
    # Get messages
    msgs = PUBLIC_MESSAGES
    
    # User specific info
    my_user = next((u for u in users if u["session_id"] == session_id), None)
    my_balance = my_user["balance"] if my_user else 0.0
    
    return {
        "messages": msgs,
        "current_turn_nickname": current_nick,
        "current_turn_session_id": current_sid,
        "my_balance": my_balance,
        "jackpot": state["jackpot"],
        "players": users
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)
