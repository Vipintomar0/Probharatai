import React, { useState, useEffect } from 'react'
import { Briefcase, Search, Download, ExternalLink, Building2, MapPin } from 'lucide-react'
import { getJobs } from '../api'

export default function Jobs() {
    const [jobs, setJobs] = useState([])
    const [filter, setFilter] = useState('')
    const [loading, setLoading] = useState(true)

    useEffect(() => { loadJobs() }, [])

    async function loadJobs() {
        try {
            const data = await getJobs()
            setJobs(data.jobs || [])
        } catch (e) { console.error(e) }
        setLoading(false)
    }

    const filtered = jobs.filter(j =>
        (j.title || '').toLowerCase().includes(filter.toLowerCase()) ||
        (j.company || '').toLowerCase().includes(filter.toLowerCase())
    )

    const statusCounts = {
        total: jobs.length,
        applied: jobs.filter(j => j.status === 'applied').length,
        found: jobs.filter(j => j.status === 'found').length,
    }

    return (
        <div className="max-w-7xl mx-auto space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-dark-100 flex items-center gap-2">
                        <Briefcase className="w-6 h-6 text-accent-violet" /> Job Applications
                    </h1>
                    <p className="text-sm text-dark-400 mt-1">Track your AI-assisted job applications</p>
                </div>
                <button className="btn-secondary flex items-center gap-2 text-sm">
                    <Download className="w-4 h-4" /> Export CSV
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
                <div className="glass-card p-4 text-center">
                    <div className="text-2xl font-bold text-dark-100">{statusCounts.total}</div>
                    <div className="text-xs text-dark-400 mt-1">Total Jobs</div>
                </div>
                <div className="glass-card p-4 text-center">
                    <div className="text-2xl font-bold text-emerald-400">{statusCounts.applied}</div>
                    <div className="text-xs text-dark-400 mt-1">Applied</div>
                </div>
                <div className="glass-card p-4 text-center">
                    <div className="text-2xl font-bold text-amber-400">{statusCounts.found}</div>
                    <div className="text-xs text-dark-400 mt-1">Found</div>
                </div>
            </div>

            {/* Search */}
            <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
                <input
                    value={filter}
                    onChange={e => setFilter(e.target.value)}
                    placeholder="Search jobs by title or company..."
                    className="input-field w-full pl-11"
                />
            </div>

            {/* Job List */}
            <div className="space-y-3">
                {loading ? (
                    <div className="text-center py-12 text-dark-500">Loading jobs...</div>
                ) : filtered.length === 0 ? (
                    <div className="glass-card p-12 text-center">
                        <Briefcase className="w-12 h-12 mx-auto mb-3 text-dark-600" />
                        <p className="text-dark-400">No job applications yet.</p>
                        <p className="text-sm text-dark-500 mt-1">Use the prompt to start searching for jobs!</p>
                    </div>
                ) : (
                    filtered.map((job) => (
                        <div key={job.id} className="glass-card-hover p-5 flex items-center justify-between">
                            <div className="flex-1 min-w-0">
                                <h3 className="text-sm font-semibold text-dark-100 truncate">{job.title || 'Untitled'}</h3>
                                <div className="flex items-center gap-4 mt-1.5 text-xs text-dark-400">
                                    {job.company && <span className="flex items-center gap-1"><Building2 className="w-3 h-3" />{job.company}</span>}
                                    <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{job.platform}</span>
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <span className={`status-${job.status === 'applied' ? 'completed' : 'pending'}`}>
                                    {job.status}
                                </span>
                                {job.url && (
                                    <a href={job.url} target="_blank" rel="noopener noreferrer" className="text-dark-400 hover:text-primary-400 transition-colors">
                                        <ExternalLink className="w-4 h-4" />
                                    </a>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    )
}
