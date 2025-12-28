'use client';

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

export default function LoadingPanel({ events, currentStage, analysisData }: LoadingPanelProps) {
    const currentInfo = stageInfo[currentStage as keyof typeof stageInfo] || {
        title: 'INITIALIZING',
        emoji: '🚀',
        description: 'Starting up...'
    };

    // Check completion status for each stage
    const detectiveCompleted = events.some(e => e.type === 'detective_complete');
    const ctoCompleted = events.some(e => e.type === 'cto_complete');
    const ghostwriterCompleted = events.some(e => e.type === 'ghostwriter_complete');

    return (
        <div className="h-full flex flex-col bg-[#fafafa]">
            {/* Header */}
            <div className="border-b-4 border-black bg-white p-6">
                <div className="flex items-center gap-4">
                    <div className="text-4xl">{currentInfo.emoji}</div>
                    <div>
                        <h2 className="text-2xl font-black text-black">{currentInfo.title}</h2>
                        <p className="font-mono text-sm text-black/60">{currentInfo.description}</p>
                    </div>
                </div>
            </div>

            {/* Progress Stages */}
            <div className="border-b-4 border-black bg-white p-6">
                <div className="flex gap-4">
                    {Object.entries(stageInfo).map(([stage, info]) => {
                        // Determine if this stage is completed, active, or pending
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

            {/* Event Log / Analysis Preview */}
            <div className="flex-1 overflow-y-auto p-6">
                {ctoCompleted && analysisData ? (
                    // Show analysis results when CTO completes
                    <div className="space-y-4">
                        <h3 className="font-mono text-sm font-bold text-black/60 mb-4 uppercase">Analysis Complete! 🎉</h3>

                        {/* Developer Archetype */}
                        <div className="border-4 border-black bg-[#4ecdc4] p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                            <h4 className="font-black text-xl mb-2 text-black">Developer Archetype</h4>
                            <p className="font-mono text-lg text-black">{analysisData.archetype}</p>
                        </div>

                        {/* Grind Score */}
                        {analysisData.grind_score && (
                            <div className="border-4 border-black bg-white p-6">
                                <h4 className="font-black text-xl mb-3 text-black">Grind Score</h4>
                                <div className="flex items-center gap-4">
                                    <div className="text-4xl">{analysisData.grind_score.emoji}</div>
                                    <div className="flex-1">
                                        <div className="font-mono text-2xl font-bold text-black">{analysisData.grind_score.score}/100</div>
                                        <div className="font-mono text-sm text-black/60">{analysisData.grind_score.label}</div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Primary Language */}
                        {analysisData.primary_language && (
                            <div className="border-4 border-black bg-[#ffe66d] p-6">
                                <h4 className="font-black text-xl mb-2 text-black">Primary Language</h4>
                                <div className="font-mono text-lg text-black">
                                    {analysisData.primary_language.name} ({analysisData.primary_language.percentage}%)
                                </div>
                            </div>
                        )}

                        {/* Top Languages */}
                        {analysisData.top_languages && analysisData.top_languages.length > 0 && (
                            <div className="border-4 border-black bg-white p-6">
                                <h4 className="font-black text-xl mb-3 text-black">Tech Stack</h4>
                                <div className="space-y-2">
                                    {analysisData.top_languages.slice(0, 5).map((lang: any, i: number) => (
                                        <div key={i} className="flex items-center gap-3">
                                            <div className="w-32 font-mono text-sm text-black">{lang.name}</div>
                                            <div className="flex-1 h-8 border-2 border-black bg-white relative overflow-hidden">
                                                <div
                                                    className="h-full bg-[#ff6b6b] transition-all duration-500"
                                                    style={{ width: `${lang.percentage}%` }}
                                                />
                                            </div>
                                            <div className="w-16 font-mono text-sm text-right text-black/60">{lang.percentage}%</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Ghostwriter Status */}
                        <div className="border-4 border-black bg-[#f0f0f0] p-6 flex items-center gap-4">
                            <div className="flex gap-1">
                                <div className="w-3 h-3 bg-black animate-pulse"></div>
                                <div className="w-3 h-3 bg-black animate-pulse" style={{ animationDelay: '200ms' }}></div>
                                <div className="w-3 h-3 bg-black animate-pulse" style={{ animationDelay: '400ms' }}></div>
                            </div>
                            <span className="font-mono text-lg font-bold text-black">✍️ Ghostwriter is crafting your README...</span>
                        </div>
                    </div>
                ) : (
                    // Show event logs before CTO completes
                    <div>
                        <h3 className="font-mono text-sm font-bold text-black/60 mb-4 uppercase">Live Log</h3>
                        <div className="space-y-2">
                            {events.map((event, index) => (
                                <div
                                    key={index}
                                    className={`border-2 border-black p-3 font-mono text-sm animate-slideIn ${event.type === 'error'
                                        ? 'bg-[#ff6b6b] text-black'
                                        : event.type.includes('complete')
                                            ? 'bg-[#4ecdc4] text-black'
                                            : event.type.includes('progress')
                                                ? 'bg-white text-black'
                                                : 'bg-[#f0f0f0] text-black/60'
                                        }`}
                                    style={{
                                        animationDelay: `${index * 50}ms`
                                    }}
                                >
                                    <div className="flex items-start gap-2">
                                        <span className="text-black/40 text-xs mt-0.5">
                                            [{new Date(event.timestamp).toLocaleTimeString()}]
                                        </span>
                                        <span className="flex-1">{event.message}</span>
                                    </div>
                                </div>
                            ))}

                            {/* Animated Loading Indicator */}
                            {events.length > 0 && (
                                <div className="border-2 border-black bg-white p-3 flex items-center gap-3">
                                    <div className="flex gap-1">
                                        <div className="w-2 h-2 bg-black animate-pulse"></div>
                                        <div className="w-2 h-2 bg-black animate-pulse" style={{ animationDelay: '200ms' }}></div>
                                        <div className="w-2 h-2 bg-black animate-pulse" style={{ animationDelay: '400ms' }}></div>
                                    </div>
                                    <span className="font-mono text-sm text-black/60">Processing...</span>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
