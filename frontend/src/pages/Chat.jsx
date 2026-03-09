import React, { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, Sparkles, Zap, Terminal } from 'lucide-react'
import { executePrompt, sendChat } from '../api'

export default function Chat() {
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content: 'Hello! I\'m ProBharatAI, your AI desktop automation agent. Tell me what you\'d like to do — I can control your browser, search jobs, manage files, and much more. Try something like:\n\n• "Search product manager jobs on LinkedIn"\n• "Scrape AI startups in India and save to CSV"\n• "Open Chrome and go to GitHub"',
        }
    ])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [mode, setMode] = useState('execute') // 'execute' or 'chat'
    const bottomRef = useRef(null)
    const inputRef = useRef(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    async function handleSend() {
        if (!input.trim() || loading) return
        const userMsg = input.trim()
        setInput('')
        setMessages(prev => [...prev, { role: 'user', content: userMsg }])
        setLoading(true)

        try {
            let response
            if (mode === 'execute') {
                response = await executePrompt(userMsg)
                const plan = response.plan || []
                const results = response.results || []
                const summary = plan.map((s, i) => {
                    const r = results[i]
                    const status = r?.error ? '❌' : '✅'
                    return `${status} Step ${s.step}: ${s.description}`
                }).join('\n')
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: `🤖 Task #${response.task_id} completed!\n\n${summary}`,
                    type: 'task',
                }])
            } else {
                response = await sendChat(userMsg)
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: response.response,
                }])
            }
        } catch (e) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `⚠️ Error: ${e.message}`,
                type: 'error',
            }])
        }
        setLoading(false)
        inputRef.current?.focus()
    }

    return (
        <div className="max-w-4xl mx-auto h-[calc(100vh-7rem)] flex flex-col animate-fade-in">
            {/* Header */}
            <div className="glass-card p-4 mb-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-violet flex items-center justify-center">
                        <Bot className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-lg font-bold text-dark-100">AI Agent</h1>
                        <p className="text-xs text-dark-400">Natural language computer control</p>
                    </div>
                </div>
                <div className="flex items-center gap-2 bg-dark-800 rounded-xl p-1">
                    <button
                        onClick={() => setMode('execute')}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${mode === 'execute' ? 'bg-primary-500 text-white' : 'text-dark-400 hover:text-dark-200'}`}
                    >
                        <Terminal className="w-3.5 h-3.5 inline mr-1" />Execute
                    </button>
                    <button
                        onClick={() => setMode('chat')}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${mode === 'chat' ? 'bg-primary-500 text-white' : 'text-dark-400 hover:text-dark-200'}`}
                    >
                        <Sparkles className="w-3.5 h-3.5 inline mr-1" />Chat
                    </button>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-auto space-y-4 pr-2">
                {messages.map((msg, i) => (
                    <div key={i} className={`flex gap-3 animate-slide-up ${msg.role === 'user' ? 'justify-end' : ''}`}>
                        {msg.role === 'assistant' && (
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-accent-violet flex items-center justify-center shrink-0 mt-1">
                                <Bot className="w-4 h-4 text-white" />
                            </div>
                        )}
                        <div className={`max-w-[80%] rounded-2xl px-5 py-3 ${msg.role === 'user'
                                ? 'bg-primary-600 text-white'
                                : msg.type === 'error'
                                    ? 'bg-rose-500/10 border border-rose-500/20 text-rose-300'
                                    : 'glass-card text-dark-200'
                            }`}>
                            <pre className="whitespace-pre-wrap text-sm font-sans leading-relaxed">{msg.content}</pre>
                        </div>
                        {msg.role === 'user' && (
                            <div className="w-8 h-8 rounded-lg bg-dark-700 flex items-center justify-center shrink-0 mt-1">
                                <User className="w-4 h-4 text-dark-300" />
                            </div>
                        )}
                    </div>
                ))}
                {loading && (
                    <div className="flex gap-3 animate-slide-up">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-accent-violet flex items-center justify-center shrink-0">
                            <Bot className="w-4 h-4 text-white" />
                        </div>
                        <div className="glass-card px-5 py-3 flex items-center gap-2">
                            <Loader2 className="w-4 h-4 animate-spin text-primary-400" />
                            <span className="text-sm text-dark-400">
                                {mode === 'execute' ? 'Planning and executing...' : 'Thinking...'}
                            </span>
                        </div>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div className="mt-4 glass-card p-3">
                <div className="flex items-center gap-3">
                    <input
                        ref={inputRef}
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
                        placeholder={mode === 'execute' ? 'Tell AI what to do...' : 'Ask AI anything...'}
                        className="flex-1 bg-transparent text-dark-100 placeholder-dark-500 outline-none text-sm"
                        disabled={loading}
                    />
                    <button
                        onClick={handleSend}
                        disabled={!input.trim() || loading}
                        className="w-10 h-10 rounded-xl bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 flex items-center justify-center transition-all duration-200 disabled:opacity-30 disabled:cursor-not-allowed active:scale-90"
                    >
                        <Send className="w-4 h-4 text-white" />
                    </button>
                </div>
                <div className="flex items-center gap-2 mt-2 text-xs text-dark-500">
                    <Zap className="w-3 h-3" />
                    <span>Mode: {mode === 'execute' ? 'Execute (runs actions)' : 'Chat (conversation only)'}</span>
                </div>
            </div>
        </div>
    )
}
