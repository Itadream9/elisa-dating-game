import { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import confetti from 'canvas-confetti'
import { io } from 'socket.io-client'
import ChatUI from './components/ChatUI'
import { playSound, playAudioUrl } from './components/SoundManager'

// API Base URL
const API_BASE = '/api'
const SOCKET_URL = window.location.origin.replace(/^http/, 'ws').replace(':5173', ':8000')

function App() {
    // Game State
    const [messages, setMessages] = useState([])
    const [myBalance, setMyBalance] = useState(0.0)
    const [jackpot, setJackpot] = useState(1000.0)
    const [players, setPlayers] = useState([])

    // User Session
    const [sessionId, setSessionId] = useState(null)
    const [nickname, setNickname] = useState('')
    const [isRegistered, setIsRegistered] = useState(false)
    const [nicknameInput, setNicknameInput] = useState('')

    // UI State
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)
    const [audioEnabled, setAudioEnabled] = useState(false)
    const socketRef = useRef(null)

    // Check localStorage
    useEffect(() => {
        const storedSession = localStorage.getItem('elisa_session_id')
        const storedNickname = localStorage.getItem('elisa_nickname')

        if (storedSession && storedNickname) {
            setSessionId(storedSession)
            setNickname(storedNickname)
            setIsRegistered(true)
        }
    }, [])

    // WebSocket Connection
    useEffect(() => {
        if (isRegistered && sessionId) {
            // Initialize Socket.IO
            const socket = io(SOCKET_URL, {
                transports: ['websocket', 'polling'],
                reconnection: true
            })

            socketRef.current = socket

            socket.on('connect', () => {
                console.log('WebSocket connected:', socket.id)
                socket.emit('join_game', { session_id: sessionId })
                // Fetch initial state
                fetchStatus()
            })

            socket.on('new_message', (msg) => {
                setMessages(prev => [...prev, msg])
                if (msg.type === 'ai') {
                    playSound('messageReceived')
                }
            })

            socket.on('game_update', (data) => {
                if (data.jackpot !== undefined) setJackpot(data.jackpot)
                if (data.players) setPlayers(data.players)
            })

            socket.on('disconnect', () => {
                console.log('WebSocket disconnected')
            })

            return () => {
                socket.disconnect()
            }
        }
    }, [isRegistered, sessionId])

    const fetchStatus = async () => {
        try {
            const response = await fetch(`${API_BASE}/status?session_id=${sessionId}`)
            const data = await response.json()

            setMessages(data.messages || [])
            setMyBalance(data.my_balance)
            setJackpot(data.jackpot)
            setPlayers(data.players)
        } catch (err) {
            console.error('Status fetch failed:', err)
        }
    }

    const logout = () => {
        localStorage.removeItem('elisa_session_id')
        localStorage.removeItem('elisa_nickname')
        if (socketRef.current) socketRef.current.disconnect()
        window.location.reload()
    }

    const register = async (e) => {
        e.preventDefault()
        if (!nicknameInput.trim() || isLoading) return

        playSound('click')
        setIsLoading(true)
        try {
            const response = await fetch(`${API_BASE}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nickname: nicknameInput.trim(), session_id: sessionId })
            })
            const data = await response.json()

            localStorage.setItem('elisa_session_id', data.session_id)
            localStorage.setItem('elisa_nickname', data.nickname)
            setSessionId(data.session_id)
            setNickname(data.nickname)
            setMyBalance(data.balance)
            setIsRegistered(true)
            setAudioEnabled(true)
        } catch (err) {
            setError("Errore connessione con il Server")
            playSound('error')
        } finally {
            setIsLoading(false)
        }
    }

    const sendMessage = useCallback(async (text) => {
        if (!text.trim() || isLoading) return
        if (myBalance < 0.30) {
            setError("Credito insufficiente! Ricarica.")
            playSound('error')
            setTimeout(() => setError(null), 3000)
            return
        }

        playSound('messageSent')
        setIsLoading(true)
        setError(null)

        try {
            const response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, session_id: sessionId, nickname: nickname })
            })

            if (!response.ok) throw new Error((await response.json()).detail || "Errore sconosciuto")

            const data = await response.json()
            setMyBalance(data.balance)

            // Play Audio Response
            if (data.audio_base64) {
                playAudioUrl(`data:audio/wav;base64,${data.audio_base64}`)
            }

            if (data.is_win) {
                playSound('win')
                confetti({
                    particleCount: 150,
                    spread: 70,
                    origin: { y: 0.6 },
                    colors: ['#ff0055', '#00e5ff', '#ffffff']
                })
            }

        } catch (err) {
            setError(err.message)
            playSound('error')
            setTimeout(() => setError(null), 5000)
        } finally {
            setIsLoading(false)
        }
    }, [sessionId, nickname, myBalance, isLoading])

    // --- RENDER ---

    if (!isRegistered) {
        return (
            <div className="flex items-center justify-center h-screen w-screen relative overflow-hidden">
                <div className="cosmic-bg" />
                <div className="grid-overlay" />

                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="glass-panel p-8 max-w-md w-full text-center relative z-10 neon-border"
                >
                    <h1 className="text-5xl font-bold mb-2 font-display text-gradient tracking-tighter">HARD TO GET</h1>
                    <p className="text-gray-400 mb-6">La sfida impossibile. Conquistala o vai in rovina.</p>

                    <div className="glass-panel bg-black/30 p-4 mb-6 text-sm text-left">
                        <div className="flex justify-between mb-1"><span>Bonus Iniziale:</span> <span className="text-green-400">€10.00</span></div>
                        <div className="flex justify-between mb-1"><span>Costo SMS:</span> <span className="text-red-400">€0.30</span></div>
                        <div className="flex justify-between"><span>Jackpot Attuale:</span> <span className="text-yellow-400">€{jackpot.toFixed(2)}</span></div>
                    </div>

                    <form onSubmit={register} className="flex flex-col gap-4">
                        <input
                            value={nicknameInput}
                            onChange={e => setNicknameInput(e.target.value)}
                            placeholder="Inserisci il tuo nome..."
                            className="bg-black/50 border border-white/10 rounded px-4 py-3 text-white outline-none focus:border-[var(--accent-primary)] transition-colors text-center text-lg"
                            autoFocus
                        />
                        <button disabled={!nicknameInput} type="submit" className="btn-primary w-full">
                            {isLoading ? 'Connettendo...' : 'ACCETTA LA SFIDA'}
                        </button>
                    </form>
                </motion.div>
            </div>
        )
    }

    if (myBalance < 0.30) {
        return (
            <div className="flex items-center justify-center h-screen w-screen relative">
                <div className="cosmic-bg" />
                <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="glass-panel p-10 text-center border-red-500/50 shadow-[0_0_50px_rgba(255,0,0,0.3)]"
                >
                    <h1 className="text-6xl font-bold text-red-600 mb-4" style={{ textShadow: '0 0 20px red' }}>GAME OVER</h1>
                    <p className="text-xl mb-4">Sei rovinato.</p>
                    <div className="text-4xl font-mono mb-8 text-white">€{myBalance.toFixed(2)}</div>
                    <button onClick={logout} className="btn-primary bg-red-600 hover:bg-red-700 w-full shadow-red-900/50">
                        RICOMINCIA (Resetta)
                    </button>
                </motion.div>
            </div>
        )
    }

    return (
        <div className="flex h-screen w-screen overflow-hidden text-white relative">
            <div className="cosmic-bg" />
            <div className="grid-overlay" />

            {/* SIDEBAR PLAYERS */}
            <motion.div
                initial={{ x: -100 }}
                animate={{ x: 0 }}
                className="w-64 glass-panel m-4 flex flex-col hidden md:flex"
            >
                <div className="p-4 border-b border-white/10">
                    <h3 className="font-bold text-xs text-gray-500 uppercase tracking-widest">Pretendenti</h3>
                </div>
                <div className="flex-1 overflow-y-auto p-2">
                    {players.map(p => (
                        <div key={p.session_id} className={`p-3 mb-2 rounded flex items-center gap-3 ${p.session_id === sessionId ? 'bg-white/10 border border-white/20' : 'opacity-60'}`}>
                            <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_10px_lime]" />
                            <div className="flex-1">
                                <div className="font-mono text-sm truncate">{p.nickname}</div>
                                <div className="text-xs text-gray-500">€{p.balance?.toFixed(2) || '0.00'}</div>
                            </div>
                        </div>
                    ))}
                </div>
                <div className="p-4 border-t border-white/10 text-center">
                    <button onClick={logout} className="text-xs text-red-400 hover:text-red-300 uppercase tracking-widest">Esci dal gioco</button>
                </div>
            </motion.div>

            {/* MAIN AREA */}
            <div className="flex-1 flex flex-col h-full relative z-10 p-4 pl-0">
                {/* HUD */}
                <div className="flex justify-between items-center mb-4 glass-panel p-4 mx-4 md:mx-0">
                    <div>
                        <div className="text-xs text-gray-400 uppercase tracking-widest mb-1">Jackpot</div>
                        <div className="text-2xl font-mono text-[var(--accent-tertiary)] drop-shadow-[0_0_10px_rgba(204,255,0,0.5)]">
                            €{jackpot.toFixed(2)}
                        </div>
                    </div>
                    <div className="text-center">
                        <h2 className="text-xl font-display font-bold text-gradient">ELISA AI</h2>
                        <div className="flex items-center justify-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                            <span className="text-xs text-red-400 tracking-wider">LIVE</span>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-xs text-gray-400 uppercase tracking-widest mb-1">Il tuo saldo</div>
                        <div className={`text-2xl font-mono ${myBalance < 3.0 ? 'text-red-500 animate-pulse' : 'text-white'}`}>
                            €{myBalance.toFixed(2)}
                        </div>
                    </div>
                </div>

                {/* CHAT */}
                <div className="flex-1 overflow-hidden relative glass-panel mx-4 md:mx-0 mb-4 flex flex-col">
                    <ChatUI
                        messages={messages}
                        onSendMessage={sendMessage}
                        isLoading={isLoading}
                        error={error}
                        isMyTurn={true}
                        currentNickname={nickname}
                    />
                </div>
            </div>
        </div>
    )
}

export default App
