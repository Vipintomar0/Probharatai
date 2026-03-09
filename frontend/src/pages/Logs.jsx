import React, { useState, useEffect } from 'react'
import { FileText, RefreshCw, Filter, AlertTriangle, Info, CheckCircle, XCircle } from 'lucide-react'
import { getLogs } from '../api'

const levelConfig = {
    INFO: { icon: Info, color: 'text-primary-400', bg: 'bg-primary-500/10' },
    WARNING: { icon: AlertTriangle, color: 'text-amber-400', bg: 'bg-amber-500/10' },
    ERROR: { icon: XCircle, color: 'text-rose-400', bg: 'bg-rose-500/10' },
    SUCCESS: { icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
}

export default function Logs() {
    const [logs, setLogs] = useState([])
    const [levelFilter, setLevelFilter] = useState('')
    const [loading, setLoading] = useState(true)

    useEffect(() => { loadLogs() }, [levelFilter])

    async function loadLogs() {
        setLoading(true)
        try {
            const data = await getLogs(200, levelFilter || undefined)
            setLogs(data.logs || [])
        } catch (e) { console.error(e) }
        setLoading(false)
    }

    return (
        <div className="max-w-7xl mx-auto space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-dark-100 flex items-center gap-2">
                        <FileText className="w-6 h-6 text-accent-cyan" /> System Logs
                    </h1>
                    <p className="text-sm text-dark-400 mt-1">Real-time activity and automation logs</p>
                </div>
                <button onClick={loadLogs} className="btn-secondary flex items-center gap-2 text-sm">
                    <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Refresh
                </button>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-dark-500" />
                {['', 'INFO', 'WARNING', 'ERROR'].map(level => (
                    <button
                        key={level}
                        onClick={() => setLevelFilter(level)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${levelFilter === level ? 'bg-primary-500 text-white' : 'bg-dark-800 text-dark-400 hover:text-dark-200 border border-dark-700'
                            }`}
                    >
                        {level || 'All'}
                    </button>
                ))}
            </div>

            {/* Log entries */}
            <div className="glass-card divide-y divide-dark-700/50">
                {loading ? (
                    <div className="p-12 text-center text-dark-500">Loading logs...</div>
                ) : logs.length === 0 ? (
                    <div className="p-12 text-center">
                        <FileText className="w-12 h-12 mx-auto mb-3 text-dark-600" />
                        <p className="text-dark-400">No logs yet.</p>
                    </div>
                ) : (
                    logs.map((log) => {
                        const config = levelConfig[log.level] || levelConfig.INFO
                        const Icon = config.icon
                        return (
                            <div key={log.id} className="px-5 py-3 flex items-start gap-3 hover:bg-dark-800/50 transition-colors">
                                <div className={`w-7 h-7 rounded-lg ${config.bg} flex items-center justify-center shrink-0 mt-0.5`}>
                                    <Icon className={`w-3.5 h-3.5 ${config.color}`} />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm text-dark-200">{log.message}</p>
                                    <div className="flex items-center gap-3 mt-1 text-xs text-dark-500">
                                        <span>{log.source || 'system'}</span>
                                        <span>{new Date(log.created_at).toLocaleString()}</span>
                                    </div>
                                </div>
                                <span className={`text-xs font-mono ${config.color} opacity-60`}>{log.level}</span>
                            </div>
                        )
                    })
                )}
            </div>
        </div>
    )
}
