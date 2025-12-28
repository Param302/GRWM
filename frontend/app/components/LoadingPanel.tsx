'use client';

interface Event {
    type: string;
    stage?: string;
    message: string;
    timestamp: string;
}

interface LoadingPanelProps {
    events: Event[];
    currentStage: string;
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

export default function LoadingPanel({ events, currentStage }: LoadingPanelProps) {
    const currentInfo = stageInfo[currentStage as keyof typeof stageInfo] || {
        title: 'INITIALIZING',
        emoji: '🚀',
        description: 'Starting up...'
    };

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
                    {Object.entries(stageInfo).map(([stage, info], index) => {
                        const isActive = currentStage === stage;
                        const isPast = Object.keys(stageInfo).indexOf(currentStage) > index;

                        return (
                            <div
                                key={stage}
                                className={`flex-1 border-4 border-black p-4 transition-all ${isActive
                                        ? 'bg-[#ffe66d] shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]'
                                        : isPast
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

            {/* Event Log */}
            <div className="flex-1 overflow-y-auto p-6">
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
        </div>
    );
}
