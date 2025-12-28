'use client';

import { useState } from 'react';

interface Event {
    type: string;
    stage?: string;
    message: string;
    timestamp: string;
    data?: any;
}

interface LoadingPanelProps {
    events: Event[];
    currentStage: string;
    analysisData?: any;
    showStyleSelector?: boolean;
    selectedStyle?: string;
    onStyleChange?: (style: string) => void;
    finalMarkdown?: string;
    username?: string;
}

const stageInfo = {
    detective: {
        title: 'THE DETECTIVE',
        emoji: '🔍',
        description: 'Investigating your GitHub profile...'
    },
    cto: {
        title: 'THE CTO',
        emoji: '🧠',
        description: 'Analyzing your tech stack and patterns...'
    },
    ghostwriter: {
        title: 'THE GHOSTWRITER',
        emoji: '✍️',
        description: 'Crafting your README with style...'
    }
};

export default function LoadingPanel({
    events,
    currentStage,
    analysisData,
    showStyleSelector = false,
    selectedStyle = 'professional',
    onStyleChange,
    finalMarkdown,
    username
}: LoadingPanelProps) {
    const [copied, setCopied] = useState(false);

    // Check completion status for each stage
    const detectiveCompleted = events.some(e => e.type === 'detective_complete');
    const ctoCompleted = events.some(e => e.type === 'cto_complete');
    const ghostwriterCompleted = events.some(e => e.type === 'ghostwriter_complete');

    const styles = [
        { id: 'professional', name: 'Professional', desc: 'Clean & Corporate' },
        { id: 'creative', name: 'Creative', desc: 'Bold & Expressive' },
        { id: 'minimal', name: 'Minimal', desc: 'Less is More' },
        { id: 'detailed', name: 'Detailed', desc: 'Comprehensive' },
    ];

    const handleCopy = () => {
        if (finalMarkdown) {
            navigator.clipboard.writeText(finalMarkdown);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const handleDownload = () => {
        if (finalMarkdown) {
            const blob = new Blob([finalMarkdown], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'README.md';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    };

    return (
        <div className="h-full flex flex-col bg-[#fafafa]">
            {/* Project Header */}
            <div className="border-b-4 border-black bg-white p-6">
                <h1 className="text-4xl font-black text-black tracking-tight">GRWM</h1>
                <p className="font-mono text-sm text-black/60 mt-1">Get README With Me</p>
            </div>

            {/* Progress Stages */}
            <div className="border-b-4 border-black bg-white p-6">
                <div className="flex gap-4">
                    {Object.entries(stageInfo).map(([stage, info]) => {
                        let stageStatus: 'completed' | 'active' | 'pending' = 'pending';

                        if (stage === 'detective' && detectiveCompleted) {
                            stageStatus = 'completed';
                        } else if (stage === 'detective' && currentStage === 'detective') {
                            stageStatus = 'active';
                        } else if (stage === 'cto' && ctoCompleted) {
                            stageStatus = 'completed';
                        } else if (stage === 'cto' && currentStage === 'cto') {
                            stageStatus = 'active';
                        } else if (stage === 'ghostwriter' && ghostwriterCompleted) {
                            stageStatus = 'completed';
                        } else if (stage === 'ghostwriter' && currentStage === 'ghostwriter') {
                            stageStatus = 'active';
                        }

                        return (
                            <div
                                key={stage}
                                className={`flex-1 border-4 border-black p-4 transition-all ${stageStatus === 'active'
                                    ? 'bg-[#ffe66d] shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]'
                                    : stageStatus === 'completed'
                                        ? 'bg-[#4ecdc4]'
                                        : 'bg-[#f0f0f0]'
                                    }`}
                            >
                                <div className="text-2xl mb-2">{info.emoji}</div>
                                <p className="font-mono text-xs font-bold text-black">{info.title}</p>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Style Selector - Show after CTO completes, before README */}
            {showStyleSelector && onStyleChange && (
                <div className="border-b-4 border-black bg-white p-6">
                    <h3 className="font-black text-2xl mb-6 text-black uppercase">Choose Your Vibe ✨</h3>
                    <div className="grid grid-cols-2 gap-6">
                        {styles.map((style, idx) => {
                            const colors = ['bg-[#ff6b6b]', 'bg-[#4ecdc4]', 'bg-[#ffe66d]', 'bg-[#a8e6cf]'];
                            return (
                                <button
                                    key={style.id}
                                    onClick={() => onStyleChange(style.id)}
                                    className={`border-4 border-black p-6 text-center transition-all font-black ${selectedStyle === style.id
                                        ? 'bg-black text-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] scale-105'
                                        : `${colors[idx]} text-black hover:translate-x-1 hover:translate-y-1 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]`
                                        }`}
                                >
                                    <div className="text-2xl mb-2">{style.name}</div>
                                    <div className="font-mono text-xs font-normal opacity-80">{style.desc}</div>
                                </button>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* README Preview - Show when ghostwriter completes */}
            {finalMarkdown ? (
                <>
                    {/* Action Buttons */}
                    <div className="border-b-4 border-black bg-white p-6">
                        <div className="flex gap-4">
                            <button
                                onClick={handleCopy}
                                className="flex-1 px-6 py-3 border-4 border-black bg-[#4ecdc4] hover:bg-[#3dbab1] font-mono font-bold text-black transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1"
                            >
                                {copied ? 'COPIED!' : 'COPY'}
                            </button>
                            <button
                                onClick={handleDownload}
                                className="flex-1 px-6 py-3 border-4 border-black bg-[#ffe66d] hover:bg-[#ffd93d] font-mono font-bold text-black transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1"
                            >
                                DOWNLOAD
                            </button>
                        </div>
                    </div>

                    {/* README Content */}
                    <div className="flex-1 overflow-y-auto p-6">
                        <div className="border-4 border-black bg-white p-8 font-mono text-sm whitespace-pre-wrap">
                            {finalMarkdown}
                        </div>
                    </div>
                </>
            ) : (
                /* Event Logs - Reversed (latest first) */
                <div className="flex-1 overflow-y-auto p-6">
                    <h3 className="font-mono text-sm font-bold text-black/60 mb-4 uppercase">Live Log</h3>
                    <div className="space-y-2">
                        {/* Animated Loading Indicator - At Top */}
                        {events.length > 0 && !finalMarkdown && (
                            <div className="border-2 border-black bg-white p-3 flex items-center gap-3">
                                <div className="flex gap-1">
                                    <div className="w-2 h-2 bg-black animate-pulse"></div>
                                    <div className="w-2 h-2 bg-black animate-pulse" style={{ animationDelay: '200ms' }}></div>
                                    <div className="w-2 h-2 bg-black animate-pulse" style={{ animationDelay: '400ms' }}></div>
                                </div>
                                <span className="font-mono text-sm text-black/60">
                                    {showStyleSelector ? "Waiting for you to pick your vibe... no rush tho 😎" : "Processing..."}
                                </span>
                            </div>
                        )}

                        {[...events].reverse()
                            .filter(event => {
                                // Filter out "complete" event that happens before ghostwriter starts
                                if (event.type === 'complete' && event.message?.includes('README generation complete')) {
                                    const hasGhostwriterEvent = events.some(e =>
                                        e.type === 'ghostwriter_complete' || e.type === 'ghostwriter_progress'
                                    );
                                    return hasGhostwriterEvent;
                                }
                                return true;
                            })
                            .map((event, index) => (
                                <div
                                    key={events.length - index}
                                    className={`border-2 border-black p-3 font-mono text-sm ${event.type === 'error'
                                        ? 'bg-[#ff6b6b] text-black'
                                        : event.type.includes('complete')
                                            ? 'bg-[#4ecdc4] text-black'
                                            : event.type === 'progress'
                                                ? 'bg-[#ffe66d] text-black'
                                                : 'bg-white text-black'
                                        }`}
                                >
                                    <div className="flex items-start gap-2">
                                        <span className="text-black/40 text-xs mt-0.5">
                                            {event.timestamp && !isNaN(new Date(event.timestamp).getTime())
                                                ? `[${new Date(event.timestamp).toLocaleTimeString()}]`
                                                : ''}
                                        </span>
                                        <span className="flex-1">{event.message}</span>
                                    </div>
                                </div>
                            ))}
                    </div>
                </div>
            )}
        </div>
    );
}
