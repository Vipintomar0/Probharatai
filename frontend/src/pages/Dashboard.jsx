import React, { useState, useEffect } from 'react'
import { Activity, Briefcase, Cpu, FileText, Send, CheckCircle2, Clock, AlertTriangle, Zap, ArrowRight } from 'lucide-react'
import { getTasks, getJobs, getHealth } from '../api'

const stats = [
    { label: 'Tasks Completed', icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-500/10', key: 'completed' },
    { label: 'Running Tasks', icon: Activity, color: 'text-primary-400', bg: 'bg-primary-500/10', key: 'running' },
    { label: 'Jobs Applied', icon: Briefcase, color: 'text-accent-violet', bg: 'bg-violet-500/10', key: 'jobs' },
    { label: 'System Status', icon: Cpu, color: 'text-accent-cyan', bg: 'bg-cyan-500/10', key: 'status' },
]

export default function Dashboard() {
    const [tasks, setTasks] = useState([])
    const [health, setHealth] = useState(null)
    const [counts, setCounts] = useState({ completed: 0, running: 0, jobs: 0, status: 'Active' })

    useEffect(() => {
        loadData()
    }, [])

    async function loadData() {
        try {
            const [taskData, healthData, jobData] = await Promise.all([
                getTasks(20).catch(() => ({ tasks: [] })),
                getHealth().catch(() => null),
                getJobs(100).catch(() => ({ jobs: [] })),
            ])
            setTasks(taskData.tasks || [])
            setHealth(healthData)
            setCounts({
                completed: (taskData.tasks || []).filter(t => t.status === 'completed').length,
                running: (taskData.tasks || []).filter(t => t.status === 'executing').length,
                jobs: (jobData.jobs || []).length,
                status: healthData ? 'Active' : 'Offline',
            })
        } catch (e) { console.error(e) }
    }

    return (
        <div className="max-w-7xl mx-auto space-y-8 animate-fade-in">
            {/* Hero */}
            <div className="glass-card p-8 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-primary-500/10 via-accent-violet/5 to-transparent rounded-full -translate-y-1/2 translate-x-1/3" />
                <div className="relative">
                    <div className="flex items-center gap-2 mb-2">
                        <Zap className="w-5 h-5 text-primary-400" />
                        <span className="text-xs font-semibold text-primary-400 uppercase tracking-wider">AI Desktop Agent</span>
                    </div>
                    <h1 className="text-4xl font-bold mb-3">
                        <span className="gradient-text">ProBharatAI</span>
                    </h1>
                    <p className="text-dark-400 text-lg max-w-2xl">
                        Your open-source AI computer operator. Control your browser, automate jobs, and run tasks — all with natural language.
                    </p>
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {stats.map(({ label, icon: Icon, color, bg, key }) => (
                    <div key={key} className="glass-card-hover p-5">
                        <div className="flex items-center justify-between mb-3">
                            <div className={`w-10 h-10 ${bg} rounded-xl flex items-center justify-center`}>
                                <Icon className={`w-5 h-5 ${color}`} />
                            </div>
                            {key === 'status' && (
                                <div className="flex items-center gap-1.5">
                                    <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                                </div>
                            )}
                        </div>
                        <div className="text-2xl font-bold text-dark-100">
                            {key === 'status' ? counts.status : counts[key]}
                        </div>
                        <div className="text-sm text-dark-400 mt-1">{label}</div>
                    </div>
                ))}
            </div>

            {/* Quick Actions & Recent */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Quick Prompts */}
                <div className="glass-card p-6">
                    <h2 className="text-lg font-semibold text-dark-100 mb-4 flex items-center gap-2">
                        <Send className="w-5 h-5 text-primary-400" /> Quick Prompts
                    </h2>
                    <div className="space-y-2">
                        {[
                            'Apply to product manager jobs on LinkedIn',
                            'Download all invoices from Gmail',
                            'Scrape competitor pricing data',
                            'Generate a lead list for SaaS startups',
                            'Search remote AI jobs and save to CSV',
                        ].map((prompt, i) => (
                            <button
                                key={i}
                                className="w-full text-left px-4 py-3 rounded-xl bg-dark-800 hover:bg-dark-700 border border-dark-700 hover:border-primary-500/30 text-sm text-dark-300 hover:text-dark-100 transition-all duration-200 flex items-center justify-between group"
                            >
                                <span>{prompt}</span>
                                <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity text-primary-400" />
                            </button>
                        ))}
                    </div>
                </div>

                {/* Recent Tasks */}
                <div className="glass-card p-6">
                    <h2 className="text-lg font-semibold text-dark-100 mb-4 flex items-center gap-2">
                        <Clock className="w-5 h-5 text-accent-violet" /> Recent Tasks
                    </h2>
                    {tasks.length === 0 ? (
                        <div className="text-center py-12 text-dark-500">
                            <Activity className="w-12 h-12 mx-auto mb-3 opacity-30" />
                            <p className="text-sm">No tasks yet. Start by typing a prompt!</p>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {tasks.slice(0, 6).map((task) => (
                                <div key={task.id} className="flex items-center justify-between px-4 py-3 rounded-xl bg-dark-800 border border-dark-700">
                                    <div className="flex-1 min-w-0 mr-3">
                                        <p className="text-sm text-dark-200 truncate">{task.prompt}</p>
                                        <p className="text-xs text-dark-500 mt-0.5">#{task.id}</p>
                                    </div>
                                    <span className={`status-${task.status === 'completed' ? 'completed' : task.status === 'failed' ? 'failed' : task.status === 'executing' ? 'running' : 'pending'}`}>
                                        {task.status}
                                    </span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
