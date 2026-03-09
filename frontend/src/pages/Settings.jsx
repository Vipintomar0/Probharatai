import React, { useState, useEffect } from 'react'
import { Settings as SettingsIcon, Key, Bot, Send as TelegramIcon, Shield, Save, CheckCircle, Eye, EyeOff } from 'lucide-react'
import { getSettings, updateSettings, saveApiKey, testTelegram } from '../api'

const llmProviders = [
    { id: 'openai', name: 'OpenAI', model: 'GPT-4o' },
    { id: 'anthropic', name: 'Anthropic', model: 'Claude Sonnet' },
    { id: 'groq', name: 'Groq', model: 'Llama 3.3 70B' },
    { id: 'gemini', name: 'Google', model: 'Gemini 2.0 Flash' },
    { id: 'ollama', name: 'Ollama', model: 'Local LLM' },
    { id: 'openrouter', name: 'OpenRouter', model: 'Multi-model' },
]

export default function SettingsPage() {
    const [settings, setSettings] = useState({})
    const [apiKeys, setApiKeys] = useState({})
    const [showKeys, setShowKeys] = useState({})
    const [saving, setSaving] = useState(false)
    const [saveMsg, setSaveMsg] = useState('')
    const [telegramToken, setTelegramToken] = useState('')
    const [telegramChatId, setTelegramChatId] = useState('')

    useEffect(() => { loadSettings() }, [])

    async function loadSettings() {
        try {
            const data = await getSettings()
            setSettings(data)
        } catch (e) { console.error(e) }
    }

    async function handleSaveApiKey(provider) {
        const key = apiKeys[provider]
        if (!key) return
        setSaving(true)
        try {
            await saveApiKey(provider, key)
            setSaveMsg(`${provider} key saved!`)
            setTimeout(() => setSaveMsg(''), 3000)
        } catch (e) { setSaveMsg(`Error: ${e.message}`) }
        setSaving(false)
    }

    async function handleTestTelegram() {
        try {
            const result = await testTelegram()
            setSaveMsg(result.status === 'success' ? 'Telegram connected!' : 'Telegram failed')
            setTimeout(() => setSaveMsg(''), 3000)
        } catch (e) { setSaveMsg(`Error: ${e.message}`) }
    }

    return (
        <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
            <div>
                <h1 className="text-2xl font-bold text-dark-100 flex items-center gap-2">
                    <SettingsIcon className="w-6 h-6 text-dark-400" /> Settings
                </h1>
                <p className="text-sm text-dark-400 mt-1">Configure API keys, LLM, Telegram, and security</p>
            </div>

            {saveMsg && (
                <div className="glass-card p-3 flex items-center gap-2 border-emerald-500/30 bg-emerald-500/5">
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                    <span className="text-sm text-emerald-300">{saveMsg}</span>
                </div>
            )}

            {/* LLM Selection */}
            <div className="glass-card p-6">
                <h2 className="text-lg font-semibold text-dark-100 flex items-center gap-2 mb-4">
                    <Bot className="w-5 h-5 text-primary-400" /> LLM Provider
                </h2>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    {llmProviders.map(p => (
                        <button
                            key={p.id}
                            onClick={() => setSettings(s => ({ ...s, default_llm_provider: p.id }))}
                            className={`p-3 rounded-xl text-left border transition-all duration-200 ${settings.default_llm_provider === p.id
                                    ? 'border-primary-500 bg-primary-500/10'
                                    : 'border-dark-700 bg-dark-800 hover:border-dark-600'
                                }`}
                        >
                            <div className="text-sm font-medium text-dark-200">{p.name}</div>
                            <div className="text-xs text-dark-500 mt-0.5">{p.model}</div>
                        </button>
                    ))}
                </div>
            </div>

            {/* API Keys */}
            <div className="glass-card p-6">
                <h2 className="text-lg font-semibold text-dark-100 flex items-center gap-2 mb-4">
                    <Key className="w-5 h-5 text-accent-amber" /> API Keys
                </h2>
                <div className="space-y-3">
                    {llmProviders.filter(p => p.id !== 'ollama').map(p => (
                        <div key={p.id} className="flex items-center gap-3">
                            <label className="w-28 text-sm text-dark-400 shrink-0">{p.name}</label>
                            <div className="flex-1 relative">
                                <input
                                    type={showKeys[p.id] ? 'text' : 'password'}
                                    value={apiKeys[p.id] || ''}
                                    onChange={e => setApiKeys(k => ({ ...k, [p.id]: e.target.value }))}
                                    placeholder={`${p.name} API Key`}
                                    className="input-field w-full pr-10 text-sm"
                                />
                                <button
                                    onClick={() => setShowKeys(s => ({ ...s, [p.id]: !s[p.id] }))}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-dark-500 hover:text-dark-300"
                                >
                                    {showKeys[p.id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>
                            <button
                                onClick={() => handleSaveApiKey(p.id)}
                                disabled={!apiKeys[p.id]}
                                className="btn-primary text-sm px-4 disabled:opacity-30"
                            >
                                <Save className="w-4 h-4" />
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            {/* Telegram */}
            <div className="glass-card p-6">
                <h2 className="text-lg font-semibold text-dark-100 flex items-center gap-2 mb-4">
                    <TelegramIcon className="w-5 h-5 text-accent-cyan" /> Telegram Bot
                </h2>
                <div className="space-y-3">
                    <div className="flex items-center gap-3">
                        <label className="w-28 text-sm text-dark-400 shrink-0">Bot Token</label>
                        <input
                            type="password"
                            value={telegramToken}
                            onChange={e => setTelegramToken(e.target.value)}
                            placeholder="Your BotFather token"
                            className="input-field flex-1 text-sm"
                        />
                    </div>
                    <div className="flex items-center gap-3">
                        <label className="w-28 text-sm text-dark-400 shrink-0">Chat ID</label>
                        <input
                            value={telegramChatId}
                            onChange={e => setTelegramChatId(e.target.value)}
                            placeholder="Your Telegram chat ID"
                            className="input-field flex-1 text-sm"
                        />
                    </div>
                    <button onClick={handleTestTelegram} className="btn-primary text-sm">
                        Test Connection
                    </button>
                </div>
            </div>

            {/* Security */}
            <div className="glass-card p-6">
                <h2 className="text-lg font-semibold text-dark-100 flex items-center gap-2 mb-4">
                    <Shield className="w-5 h-5 text-accent-rose" /> Security
                </h2>
                <label className="flex items-center gap-3 cursor-pointer">
                    <input
                        type="checkbox"
                        checked={settings.require_approval !== 'false'}
                        onChange={e => setSettings(s => ({ ...s, require_approval: e.target.checked ? 'true' : 'false' }))}
                        className="w-5 h-5 rounded bg-dark-800 border-dark-600 text-primary-500 focus:ring-primary-500"
                    />
                    <div>
                        <span className="text-sm text-dark-200">Require approval for critical actions</span>
                        <p className="text-xs text-dark-500">AI will ask before applying to jobs, submitting forms, etc.</p>
                    </div>
                </label>
            </div>
        </div>
    )
}
