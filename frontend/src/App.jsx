import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import { LayoutDashboard, MessageSquare, Settings, FileText, Briefcase, Activity, Menu, X, Zap } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import Jobs from './pages/Jobs'
import Logs from './pages/Logs'
import SettingsPage from './pages/Settings'

const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/chat', icon: MessageSquare, label: 'Prompt' },
    { to: '/jobs', icon: Briefcase, label: 'Jobs' },
    { to: '/logs', icon: FileText, label: 'Logs' },
    { to: '/settings', icon: Settings, label: 'Settings' },
]

function Sidebar({ isOpen, setIsOpen }) {
    return (
        <>
            {/* Mobile overlay */}
            {isOpen && (
                <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setIsOpen(false)} />
            )}

            <aside className={`
        fixed top-0 left-0 h-full w-64 bg-dark-900/95 backdrop-blur-xl border-r border-dark-700/50 z-50
        transform transition-transform duration-300 ease-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static
      `}>
                {/* Logo */}
                <div className="p-6 border-b border-dark-700/50">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-violet flex items-center justify-center">
                            <Zap className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h1 className="text-lg font-bold gradient-text">ProBharatAI</h1>
                            <p className="text-xs text-dark-400">AI Desktop Agent</p>
                        </div>
                    </div>
                </div>

                {/* Nav */}
                <nav className="p-4 space-y-1">
                    {navItems.map(({ to, icon: Icon, label }) => (
                        <NavLink
                            key={to}
                            to={to}
                            onClick={() => setIsOpen(false)}
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200
                ${isActive
                                    ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20'
                                    : 'text-dark-400 hover:text-dark-200 hover:bg-dark-800'
                                }`
                            }
                        >
                            <Icon className="w-5 h-5" />
                            {label}
                        </NavLink>
                    ))}
                </nav>

                {/* Status */}
                <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-dark-700/50">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                        <span className="text-xs text-dark-400">System Active</span>
                    </div>
                </div>
            </aside>
        </>
    )
}

export default function App() {
    const [sidebarOpen, setSidebarOpen] = useState(false)

    return (
        <Router>
            <div className="flex h-screen overflow-hidden bg-dark-950">
                <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

                <div className="flex-1 flex flex-col overflow-hidden">
                    {/* Top bar */}
                    <header className="h-16 border-b border-dark-700/50 flex items-center justify-between px-6 bg-dark-900/50 backdrop-blur-xl lg:hidden">
                        <button onClick={() => setSidebarOpen(true)} className="text-dark-400 hover:text-dark-200">
                            <Menu className="w-6 h-6" />
                        </button>
                        <h1 className="text-lg font-bold gradient-text">ProBharatAI</h1>
                        <div className="w-6" />
                    </header>

                    {/* Content */}
                    <main className="flex-1 overflow-auto p-6">
                        <Routes>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/chat" element={<Chat />} />
                            <Route path="/jobs" element={<Jobs />} />
                            <Route path="/logs" element={<Logs />} />
                            <Route path="/settings" element={<SettingsPage />} />
                        </Routes>
                    </main>
                </div>
            </div>
        </Router>
    )
}
