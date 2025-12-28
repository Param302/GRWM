'use client';

import { useState, useEffect, useRef } from 'react';
import { ArrowLeft } from 'lucide-react';
import ProfileCard from './ProfileCard';
import StyleSelector from './StyleSelector';
import LoadingPanel from './LoadingPanel';
import ReadmePreview from './ReadmePreview';

interface GenerationFlowProps {
    username: string;
    tone: string;
    onBack: () => void;
}

interface ProfileData {
    name: string;
    username: string;
    bio: string;
    avatar_url: string;
    location: string;
    company: string;
    public_repos: number;
    followers: number;
    following: number;
}

interface AnalysisData {
    archetype: string;
    grind_score: {
        score: number;
        label: string;
        emoji: string;
    };
    primary_language: {
        name: string;
        percentage: number;
    };
    key_projects: Array<{
        name: string;
        description: string;
        stars: number;
    }>;
}

interface Event {
    type: string;
    stage?: string;
    message: string;
    data?: any;
    timestamp: string;
}

export default function GenerationFlow({ username, tone, onBack }: GenerationFlowProps) {
    const [loading, setLoading] = useState(true);
    const [events, setEvents] = useState<Event[]>([]);
    const [profileData, setProfileData] = useState<ProfileData | null>(null);
    const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
    const [finalMarkdown, setFinalMarkdown] = useState('');
    const [selectedStyle, setSelectedStyle] = useState('');
    const [currentStage, setCurrentStage] = useState('');
    const [sessionId, setSessionId] = useState<string>('');
    const hasStartedRef = useRef(false);
    const eventSourceRef = useRef<EventSource | null>(null);

    useEffect(() => {
        // Prevent double execution in React strict mode
        if (!hasStartedRef.current) {
            hasStartedRef.current = true;
            startGeneration();
        }

        // Cleanup on unmount
        return () => {
            if (eventSourceRef.current) {
                console.log('🧹 Cleaning up SSE connection');
                eventSourceRef.current.close();
                eventSourceRef.current = null;
            }
        };
    }, []);

    const startGeneration = async () => {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        try {
            console.log('🚀 Starting generation for:', username);

            // Start generation
            const response = await fetch(`${API_URL}/api/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, tone: selectedStyle })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('✅ Received session data:', data);

            if (!data || !data.session_id) {
                throw new Error('No session_id received from server');
            }

            const { session_id } = data;
            setSessionId(session_id);
            console.log('🔗 Connecting to SSE stream:', session_id);

            // Connect to SSE stream
            const eventSource = new EventSource(`${API_URL}/api/stream/${session_id}`);
            eventSourceRef.current = eventSource;

            eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log('📨 SSE Event received:', data.type);

                // Add to events list
                setEvents(prev => [...prev, data]);

                // Update current stage
                if (data.stage) {
                    setCurrentStage(data.stage);
                }

                // Handle specific events
                if (data.type === 'detective_complete') {
                    console.log('👤 Profile data received');
                    setProfileData(data.data.profile);
                } else if (data.type === 'cto_complete') {
                    console.log('🧠 Analysis data received');
                    setAnalysisData(data.data);
                } else if (data.type === 'ghostwriter_complete') {
                    console.log('✍️ README received');
                    setFinalMarkdown(data.data.markdown);
                    setLoading(false);
                } else if (data.type === 'done') {
                    console.log('✅ Generation complete');
                    eventSource.close();
                    if (!finalMarkdown) {
                        setLoading(false);
                    }
                } else if (data.type === 'error') {
                    console.error('❌ Error event:', data.message);
                    eventSource.close();
                    setLoading(false);
                }
            };

            eventSource.onerror = (error) => {
                console.error('❌ SSE connection error:', error);
                eventSource.close();
                setLoading(false);
                setEvents(prev => [...prev, {
                    type: 'error',
                    message: 'Connection lost',
                    timestamp: new Date().toISOString()
                }]);
            };

        } catch (error) {
            setLoading(false);
            console.error('❌ Generation error:', error);
            setEvents(prev => [...prev, {
                type: 'error',
                message: error instanceof Error ? error.message : 'Failed to start generation',
                timestamp: new Date().toISOString()
            }]);
        }
    };

    const handleStyleChange = async (newStyle: string) => {
        setSelectedStyle(newStyle);
        console.log('🎨 Style selected:', newStyle);

        if (!sessionId) {
            console.error('❌ No session ID available');
            return;
        }

        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        try {
            // Notify backend of style selection
            const response = await fetch(`${API_URL}/api/select-style`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, style: newStyle })
            });

            if (!response.ok) {
                throw new Error('Failed to submit style selection');
            }

            console.log('✅ Style selection sent to backend');
        } catch (error) {
            console.error('❌ Error submitting style:', error);
        }
    };

    const ctoCompleted = events.some(e => e.type === 'cto_complete');
    const ghostwriterStarted = events.some(e => e.type === 'ghostwriter_progress' || e.type === 'ghostwriter_complete');
    const showStyleSelector = ctoCompleted && !finalMarkdown && !ghostwriterStarted;

    return (
        <div className="flex h-screen bg-[#fafafa]">
            {/* Left Panel - 40% - Profile & Analysis */}
            <div className="w-[40%] border-r-4 border-black bg-white flex flex-col">
                {/* Fixed Header */}
                <div className="p-8">
                    <div className="flex items-center justify-between">
                        <h2 className="text-2xl font-black tracking-tight text-black">PROFILE</h2>
                        <button
                            onClick={onBack}
                            className="px-4 py-2 border-2 border-black bg-white hover:bg-black hover:text-white font-mono font-bold transition-all text-sm flex items-center gap-2"
                        >
                            <ArrowLeft className="w-4 h-4" />
                            BACK
                        </button>
                    </div>
                </div>

                {/* Fixed Profile Card */}
                <div className="p-6 border-b-4 border-black">
                    {profileData ? (
                        <ProfileCard profile={profileData} analysis={analysisData} />
                    ) : (
                        <div className="flex items-center justify-center h-64">
                            <div className="text-center">
                                <div className="inline-block w-16 h-16 border-4 border-black border-t-transparent rounded-full animate-spin mb-4"></div>
                                <p className="font-mono text-sm text-black/60">Loading profile...</p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Scrollable Analysis Cards */}
                {analysisData && (
                    <div className="flex-1 overflow-y-auto p-6">
                        <div className="space-y-4">
                            <h2 className="text-2xl font-black tracking-tight text-black mb-4">ANALYSIS</h2>

                            {/* Profile Headline */}
                            {analysisData.profile_headline && (
                                <div className="border-4 border-black bg-[#4ecdc4] p-6">
                                    <h4 className="font-black text-sm mb-2 text-black/60 uppercase">Profile Headline</h4>
                                    <p className="font-mono text-base text-black leading-relaxed">{analysisData.profile_headline}</p>
                                </div>
                            )}

                            {/* Grind Score */}
                            {analysisData.grind_score && (
                                <div className="border-4 border-black bg-[#ff6b6b] p-6">
                                    <h4 className="font-black text-lg mb-3 text-black">Grind Score</h4>
                                    <div className="flex items-center gap-4">
                                        <div className="text-3xl">{analysisData.grind_score.emoji}</div>
                                        <div className="flex-1">
                                            <div className="font-mono text-xl font-bold text-black">{analysisData.grind_score.score}/100</div>
                                            <div className="font-mono text-sm text-black/70">{analysisData.grind_score.label}</div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Top Languages - Primary highlighted */}
                            {analysisData.top_languages && analysisData.top_languages.length > 0 && (
                                <div className="border-4 border-black bg-white p-6">
                                    <h4 className="font-black text-lg mb-3 text-black">Top Languages</h4>
                                    <div className="space-y-3">
                                        {/* Primary Language - Large */}
                                        {analysisData.top_languages[0] && (
                                            <div className="border-2 border-black bg-[#ffe66d] p-4">
                                                <div className="font-black text-xl text-black">{analysisData.top_languages[0].name}</div>
                                                <div className="font-mono text-sm text-black/70 mt-1">{analysisData.top_languages[0].percentage}% of code</div>
                                            </div>
                                        )}
                                        {/* Secondary & Tertiary */}
                                        <div className="space-y-2">
                                            {analysisData.top_languages.slice(1, 3).map((lang: any, i: number) => (
                                                <div key={i} className="flex items-center gap-3">
                                                    <div className="w-28 font-mono text-sm text-black">{lang.name}</div>
                                                    <div className="flex-1 h-5 border-2 border-black bg-white relative overflow-hidden">
                                                        <div
                                                            className="h-full bg-[#4ecdc4] transition-all duration-500"
                                                            style={{ width: `${lang.percentage}%` }}
                                                        />
                                                    </div>
                                                    <div className="w-12 font-mono text-xs text-right text-black/60">{lang.percentage}%</div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Tech Stack */}
                            {analysisData.tech_stack && analysisData.tech_stack.length > 0 && (
                                <div className="border-4 border-black bg-white p-6">
                                    <h4 className="font-black text-lg mb-3 text-black">Tech Stack</h4>
                                    <div className="flex flex-wrap gap-2">
                                        {analysisData.tech_stack.map((tech: string, i: number) => {
                                            const colors = ['bg-[#ff6b6b]', 'bg-[#4ecdc4]', 'bg-[#ffe66d]', 'bg-[#a8e6cf]', 'bg-[#ffd3b6]', 'bg-[#dcedc1]'];
                                            return (
                                                <span key={i} className={`px-3 py-1 border-2 border-black ${colors[i % colors.length]} font-mono text-xs font-bold text-black`}>
                                                    {tech}
                                                </span>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>

            {/* Right Panel - 60% */}
            <div className="flex-1 flex flex-col">
                <LoadingPanel
                    events={events}
                    currentStage={currentStage}
                    analysisData={analysisData}
                    showStyleSelector={showStyleSelector}
                    selectedStyle={selectedStyle}
                    onStyleChange={handleStyleChange}
                    finalMarkdown={finalMarkdown}
                    username={username}
                />
            </div>
        </div>
    );
}
