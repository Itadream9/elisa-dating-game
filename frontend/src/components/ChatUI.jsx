import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { playSound } from './SoundManager'

export default function ChatUI({ messages, onSendMessage, isLoading, error, isMyTurn, currentNickname }) {
    const [inputValue, setInputValue] = useState('')
    const messagesEndRef = useRef(null)
    const inputRef = useRef(null)

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages, isLoading])

    const handleSubmit = (e) => {
        e.preventDefault()
        if (inputValue.trim() && !isLoading && isMyTurn) {
            onSendMessage(inputValue.trim())
            setInputValue('')
        } else if (!isMyTurn) {
            playSound('error')
        }
    }

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSubmit(e)
        }
    }

    return (
        <div className="flex flex-col h-full w-full">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
                <AnimatePresence initial={false}>
                    {messages.length === 0 && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="text-center p-8 text-gray-400 italic"
                        >
                            "Ciao, sono Elisa. Ho 22 anni e sono abituata a rifiutare chiunque.
                            Convincimi che non sei il solito noioso. Hai il 5% di probabilità."
                        </motion.div>
                    )}

                    {messages.map((msg) => {
                        const isAi = msg.type === 'ai';
                        const isSystem = msg.type === 'system';
                        const isMe = msg.nickname === currentNickname;

                        if (isSystem) {
                            return (
                                <motion.div
                                    key={msg.id}
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className="flex justify-center my-4"
                                >
                                    <div className="bg-white/5 border border-white/10 rounded-full px-4 py-1 text-xs text-yellow-500 font-mono tracking-wider shadow-[0_0_10px_rgba(255,215,0,0.2)]">
                                        {msg.text}
                                    </div>
                                </motion.div>
                            )
                        }

                        return (
                            <motion.div
                                key={msg.id}
                                initial={{ opacity: 0, x: isMe ? 20 : -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                className={`flex flex-col ${isMe ? 'items-end' : 'items-start'}`}
                            >
                                <div className="text-[10px] text-gray-500 mb-1 px-1 uppercase tracking-wider">
                                    {isAi ? 'ELISA AI' : msg.nickname}
                                </div>
                                <div
                                    className={`
                                        max-w-[85%] md:max-w-[70%] px-5 py-3 rounded-2xl text-sm leading-relaxed relative
                                        ${isAi
                                            ? 'bg-gradient-to-br from-gray-800 to-gray-900 border border-white/10 text-gray-100 rounded-tl-none shadow-[0_0_15px_rgba(255,255,255,0.05)]'
                                            : isMe
                                                ? 'bg-gradient-to-br from-[var(--accent-primary)] to-pink-700 text-white rounded-tr-none shadow-[0_0_15px_rgba(255,0,85,0.3)]'
                                                : 'bg-gray-800/80 text-gray-300 rounded-tl-none border-l-2 border-gray-600'}
                                    `}
                                >
                                    {msg.text}

                                    {/* Sentiment Indicator for AI messages */}
                                    {isAi && msg.sentiment !== undefined && msg.sentiment > 0 && (
                                        <div className="absolute -bottom-5 right-0 text-[10px] text-gray-500 font-mono">
                                            INTERESSE: <span className={msg.sentiment > 50 ? 'text-green-400' : 'text-red-400'}>{msg.sentiment}%</span>
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        )
                    })}
                </AnimatePresence>

                {isLoading && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex items-center gap-2 text-gray-500 text-xs ml-2"
                    >
                        <div className="flex gap-1">
                            <span className="w-1.5 h-1.5 bg-[var(--accent-secondary)] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                            <span className="w-1.5 h-1.5 bg-[var(--accent-secondary)] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                            <span className="w-1.5 h-1.5 bg-[var(--accent-secondary)] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                        </div>
                        Elisa sta scrivendo...
                    </motion.div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-black/20 border-t border-white/5 backdrop-blur-sm">
                <form onSubmit={handleSubmit} className="flex gap-2 relative">
                    <input
                        ref={inputRef}
                        type="text"
                        className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-[var(--accent-primary)] focus:bg-white/10 transition-all font-sans"
                        placeholder={isMyTurn ? "Scrivi il tuo messaggio..." : "Aspetta il tuo turno..."}
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={handleKeyDown}
                        disabled={isLoading}
                        autoComplete="off"
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !inputValue.trim()}
                        className={`
                            px-6 rounded-xl font-bold uppercase tracking-wider text-sm transition-all
                            ${!inputValue.trim()
                                ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
                                : 'bg-[var(--accent-primary)] text-white hover:bg-pink-600 shadow-[0_0_15px_rgba(255,0,85,0.4)] hover:shadow-[0_0_25px_rgba(255,0,85,0.6)] hover:-translate-y-1 active:translate-y-0'}
                        `}
                    >
                        Invia
                    </button>

                    {error && (
                        <div className="absolute -top-12 left-0 right-0 mx-auto w-max bg-red-500/90 text-white text-xs px-3 py-1 rounded shadow-lg animate-bounce">
                            ⚠️ {error}
                        </div>
                    )}
                </form>
            </div>
        </div>
    )
}
