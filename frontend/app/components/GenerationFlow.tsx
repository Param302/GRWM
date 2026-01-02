'use client';

import { useState, useEffect, useRef } from 'react';
import { ArrowLeft } from 'lucide-react';
import ProfileCard from './ProfileCard';
import LoadingPanel from './LoadingPanel';

interface GenerationFlowProps {
    username: string;
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
    archetype?: string;
    profile_headline?: string;
    grind_score?: {
        score: number;
        label: string;
        emoji: string;
    };
    top_languages?: Array<{
        name: string;
        percentage: number;
    }>;
    tech_stack?: string[];
    primary_language?: {
        name: string;
        percentage: number;
    };
    key_projects?: Array<{
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

export default function GenerationFlow({ username, onBack }: GenerationFlowProps) {
    const [loading, setLoading] = useState(true);
    const [events, setEvents] = useState<Event[]>([]);
    const [profileData, setProfileData] = useState<ProfileData | null>(null);
    const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
    const [finalMarkdown, setFinalMarkdown] = useState('');
    const [selectedStyle, setSelectedStyle] = useState('');
    const [currentStage, setCurrentStage] = useState('');
    const [sessionId, setSessionId] = useState<string>('');
    const [showTimeoutModal, setShowTimeoutModal] = useState(false);
    const [showErrorModal, setShowErrorModal] = useState(false);
    const [showConnectionLostModal, setShowConnectionLostModal] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [firstSelectionMade, setFirstSelectionMade] = useState(false);
    const hasStartedRef = useRef(false);
    const eventSourceRef = useRef<EventSource | null>(null);
    const cleanupCalledRef = useRef(false);

    // Cleanup function to notify server
    const cleanupConnection = async () => {
        if (cleanupCalledRef.current) return;
        cleanupCalledRef.current = true;

        if (sessionId && eventSourceRef.current) {
            console.log('🧹 Cleaning up SSE connection and notifying server');

            // Close EventSource
            eventSourceRef.current.close();
            eventSourceRef.current = null;

            // Notify server to cleanup
            try {
                const API_URL = process.env.NEXT_PUBLIC_API_URL;
                await fetch(`${API_URL}/api/cleanup/${sessionId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                console.log('✅ Server notified of cleanup');
            } catch (error) {
                console.error('❌ Failed to notify server:', error);
            }
        }
    };

    // Utility function to convert image URL to base64
    const imageUrlToBase64 = async (url: string): Promise<string> => {
        try {
            const response = await fetch(url);
            const blob = await response.blob();
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onloadend = () => resolve(reader.result as string);
                reader.onerror = reject;
                reader.readAsDataURL(blob);
            });
        } catch (error) {
            console.error('Failed to convert image to base64:', error);
            return url; // Fallback to original URL
        }
    };

    useEffect(() => {
        // Prevent double execution in React strict mode
        if (!hasStartedRef.current) {
            hasStartedRef.current = true;
            startGeneration();
        }

        // Handle page navigation/reload
        const handleBeforeUnload = (e: BeforeUnloadEvent) => {
            cleanupConnection();
        };

        const handleVisibilityChange = () => {
            if (document.hidden && eventSourceRef.current) {
                // Page is being hidden/closed
                cleanupConnection();
            }
        };

        // Add event listeners
        window.addEventListener('beforeunload', handleBeforeUnload);
        document.addEventListener('visibilitychange', handleVisibilityChange);

        // Cleanup on unmount
        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            cleanupConnection();
        };
    }, [sessionId]);

    const startGeneration = async () => {
        const API_URL = process.env.NEXT_PUBLIC_API_URL;

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
                    // Convert avatar URL to base64 to avoid CORS issues with html2canvas
                    const profileWithBase64Avatar = { ...data.data.profile };
                    if (profileWithBase64Avatar.avatar_url) {
                        imageUrlToBase64(profileWithBase64Avatar.avatar_url).then(base64 => {
                            profileWithBase64Avatar.avatar_url = base64;
                            setProfileData(profileWithBase64Avatar);
                        });
                    } else {
                        setProfileData(profileWithBase64Avatar);
                    }
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

                    // Check if it's a detective/username error
                    if (data.message && (
                        data.message.includes('Failed to fetch data for @') ||
                        data.message.includes('User not found') ||
                        data.message.includes('404') ||
                        data.stage === 'detective'
                    )) {
                        setErrorMessage(data.message);
                        setShowErrorModal(true);
                    }
                } else if (data.type === 'timeout') {
                    console.error('⏰ Timeout event:', data.message);
                    eventSource.close();
                    setLoading(false);
                    setShowTimeoutModal(true);
                }
            };

            eventSource.onerror = (error) => {
                console.error('❌ SSE connection error:', error);

                // Connection lost - show modal
                if (eventSource.readyState === EventSource.CLOSED) {
                    console.log('🔌 Connection closed unexpectedly');
                    setShowConnectionLostModal(true);
                }

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

    const handleStyleChange = async (newStyle: string, description?: string) => {
        setSelectedStyle(newStyle);
        console.log('🎨 Style selected:', newStyle, 'Description:', description);

        if (!sessionId) {
            console.error('❌ No session ID available');
            return;
        }

        // Mark first selection to extend timeout
        if (!firstSelectionMade) {
            setFirstSelectionMade(true);
            console.log('⏰ First selection made - timeout will be extended to 5 minutes');
        }

        const API_URL = process.env.NEXT_PUBLIC_API_URL;

        try {
            // Notify backend of style selection and optional description
            const response = await fetch(`${API_URL}/api/select-style`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    style: newStyle,
                    description: description || ''
                })
            });

            if (!response.ok) {
                throw new Error('Failed to submit style selection');
            }

            console.log('✅ Style selection sent to backend (timeout extended automatically)');
        } catch (error) {
            console.error('❌ Error submitting style:', error);
        }
    };

    const ctoCompleted = events.some(e => e.type === 'cto_complete');
    const ghostwriterStarted = events.some(e => e.type === 'ghostwriter_progress' || e.type === 'ghostwriter_complete');
    const showStyleSelector = ctoCompleted && !finalMarkdown && !ghostwriterStarted;
    const [showAnalysis, setShowAnalysis] = useState(false);

    return (
        <>
            {/* DESKTOP VIEW - Keep as is (lg and above) */}
            <div className="hidden lg:flex h-screen bg-[#fafafa]">
                {/* Left Panel - Profile & Analysis */}
                <div className="w-[40%] border-r-4 border-black bg-white flex flex-col">
                    {/* Fixed Header */}
                    <div className="p-6">
                        <div className="flex items-center justify-between">
                            <h2 className="text-2xl font-black tracking-tight text-black">PROFILE</h2>
                            <button
                                onClick={onBack}
                                className="flex items-center gap-1 py-2 px-4 border-4 border-black bg-white hover:bg-[#f0f0f0] text-black font-black transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1 cursor-pointer"
                                title="Go back to home"
                            >
                                <ArrowLeft className="w-5 h-5" />
                                <span>BACK</span>
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
                                    <div className="flex gap-2 justify-center mb-4">
                                        <div className="w-3 h-3 bg-black rounded-full animate-bounce"></div>
                                        <div className="w-3 h-3 bg-black rounded-full animate-bounce" style={{ animationDelay: '200ms' }}></div>
                                        <div className="w-3 h-3 bg-black rounded-full animate-bounce" style={{ animationDelay: '400ms' }}></div>
                                    </div>
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
                        showStyleSelector={showStyleSelector}
                        selectedStyle={selectedStyle}
                        onStyleChange={handleStyleChange}
                        finalMarkdown={finalMarkdown}
                        username={username}
                    />
                </div>
            </div>

            {/* MOBILE VIEW - New scrollable layout */}
            <div className="lg:hidden flex flex-col h-screen bg-[#fafafa]">
                {/* Fixed Top - Project Branding */}
                <div className="border-b-4 border-black bg-white p-4 flex items-center justify-between">
                    <div>
                        <div className="flex gap-2 items-end">
                            <h1 className="text-2xl font-black text-black">GRWM</h1>
                        </div>
                        <p className="font-mono text-xs text-black/60">Get README With Me</p>
                    </div>
                    <button
                        onClick={onBack}
                        className="flex items-center gap-1 py-2 px-3 border-4 border-black bg-white hover:bg-[#f0f0f0] text-black font-black transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1 cursor-pointer"
                        title="Go back to home"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        <span className="text-sm">BACK</span>
                    </button>
                </div>

                {/* Scrollable Content Area */}
                <div className="flex-1 overflow-y-auto pb-32">
                    {/* Profile Card */}
                    <div className="p-4 border-b-4 border-black bg-white">
                        {profileData ? (
                            <ProfileCard profile={profileData} analysis={analysisData} />
                        ) : (
                            <div className="flex items-center justify-center h-32">
                                <div className="text-center">
                                    <div className="flex gap-2 justify-center mb-4">
                                        <div className="w-3 h-3 bg-black rounded-full animate-bounce"></div>
                                        <div className="w-3 h-3 bg-black rounded-full animate-bounce" style={{ animationDelay: '200ms' }}></div>
                                        <div className="w-3 h-3 bg-black rounded-full animate-bounce" style={{ animationDelay: '400ms' }}></div>
                                    </div>
                                    <p className="font-mono text-xs text-black/60">Loading profile...</p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Analysis Section - Collapsible */}
                    {analysisData && (
                        <div className="border-b-4 border-black bg-white">
                            <button
                                onClick={() => setShowAnalysis(!showAnalysis)}
                                className="w-full p-4 flex items-center justify-between text-left cursor-pointer hover:bg-[#f0f0f0] transition-colors"
                            >
                                <h2 className="text-xl font-black tracking-tight text-black">ANALYSIS</h2>
                                <span className="text-2xl font-black text-black">{showAnalysis ? '−' : '+'}</span>
                            </button>
                            {showAnalysis && (
                                <div className="p-4 space-y-3 border-t-4 border-black">
                                    {/* Profile Headline */}
                                    {analysisData.profile_headline && (
                                        <div className="border-4 border-black bg-[#4ecdc4] p-4">
                                            <h4 className="font-black text-xs mb-2 text-black/60 uppercase">Profile Headline</h4>
                                            <p className="font-mono text-sm text-black leading-relaxed">{analysisData.profile_headline}</p>
                                        </div>
                                    )}

                                    {/* Grind Score */}
                                    {analysisData.grind_score && (
                                        <div className="border-4 border-black bg-[#ff6b6b] p-4">
                                            <h4 className="font-black text-base mb-2 text-black">Grind Score</h4>
                                            <div className="flex items-center gap-3">
                                                <div className="text-2xl">{analysisData.grind_score.emoji}</div>
                                                <div className="flex-1">
                                                    <div className="font-mono text-lg font-bold text-black">{analysisData.grind_score.score}/100</div>
                                                    <div className="font-mono text-xs text-black/70">{analysisData.grind_score.label}</div>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {/* Top Languages */}
                                    {analysisData.top_languages && analysisData.top_languages.length > 0 && (
                                        <div className="border-4 border-black bg-white p-4">
                                            <h4 className="font-black text-base mb-2 text-black">Top Languages</h4>
                                            <div className="space-y-2">
                                                {analysisData.top_languages[0] && (
                                                    <div className="border-2 border-black bg-[#ffe66d] p-3">
                                                        <div className="font-black text-base text-black">{analysisData.top_languages[0].name}</div>
                                                        <div className="font-mono text-xs text-black/70 mt-1">{analysisData.top_languages[0].percentage}% of code</div>
                                                    </div>
                                                )}
                                                {analysisData.top_languages.slice(1, 3).map((lang: any, i: number) => (
                                                    <div key={i} className="flex items-center gap-2">
                                                        <div className="w-24 font-mono text-xs text-black">{lang.name}</div>
                                                        <div className="flex-1 h-4 border-2 border-black bg-white relative overflow-hidden">
                                                            <div
                                                                className="h-full bg-[#4ecdc4] transition-all duration-500"
                                                                style={{ width: `${lang.percentage}%` }}
                                                            />
                                                        </div>
                                                        <div className="w-10 font-mono text-xs text-right text-black/60">{lang.percentage}%</div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Tech Stack */}
                                    {analysisData.tech_stack && analysisData.tech_stack.length > 0 && (
                                        <div className="border-4 border-black bg-white p-4">
                                            <h4 className="font-black text-base mb-2 text-black">Tech Stack</h4>
                                            <div className="flex flex-wrap gap-2">
                                                {analysisData.tech_stack.map((tech: string, i: number) => {
                                                    const colors = ['bg-[#ff6b6b]', 'bg-[#4ecdc4]', 'bg-[#ffe66d]', 'bg-[#a8e6cf]', 'bg-[#ffd3b6]', 'bg-[#dcedc1]'];
                                                    return (
                                                        <span key={i} className={`px-2 py-1 border-2 border-black ${colors[i % colors.length]} font-mono text-xs font-bold text-black`}>
                                                            {tech}
                                                        </span>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}

                    {/* README Preview */}
                    <LoadingPanel
                        events={events}
                        currentStage={currentStage}
                        showStyleSelector={showStyleSelector}
                        selectedStyle={selectedStyle}
                        onStyleChange={handleStyleChange}
                        finalMarkdown={finalMarkdown}
                        username={username}
                    />
                </div>
            </div>

            {/* Timeout Modal */}
            {showTimeoutModal && (
                <div className="fixed inset-0 bg-black/20 backdrop-blur-md flex items-center justify-center z-50">
                    <div className="bg-white border-4 border-black p-8 max-w-md shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] animate-slideIn">
                        <div className="flex justify-between items-start mb-4">
                            <h2 className="text-xl sm:text-2xl font-black text-black">Ghostwriter is exhausted! 😴</h2>
                            <button
                                onClick={() => {
                                    setShowTimeoutModal(false);
                                    onBack();
                                }}
                                className="text-black hover:text-gray-600 text-2xl font-bold leading-none cursor-pointer"
                            >
                                ×
                            </button>
                        </div>
                        <p className="text-black mb-6 font-mono text-xs sm:text-sm">
                            Took way too long to decide... our agents literally couldn't wait and went to sleep! Give it another shot though, you got this! 🚀
                        </p>
                        <button
                            onClick={() => {
                                setShowTimeoutModal(false);
                                onBack();
                            }}
                            className="w-full border-4 border-black bg-black text-white hover:bg-gray-800 font-black px-6 py-3 transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-1 hover:translate-y-1 cursor-pointer"
                        >
                            OKAY, GO BACK
                        </button>
                    </div>
                </div>
            )}

            {/* Error Modal - Username Not Found */}
            {showErrorModal && (
                <div className="fixed inset-0 bg-black/20 backdrop-blur-md flex items-center justify-center z-50 p-4">
                    <div className="bg-white border-4 border-black p-6 sm:p-8 max-w-md w-full shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] animate-slideIn">
                        <div className="flex justify-between items-start mb-4">
                            <h2 className="text-xl sm:text-2xl font-black text-black">Username Not Found! 🔍</h2>
                            <button
                                onClick={() => {
                                    setShowErrorModal(false);
                                    onBack();
                                }}
                                className="text-black hover:text-gray-600 text-2xl font-bold leading-none cursor-pointer"
                            >
                                ×
                            </button>
                        </div>
                        <p className="text-black mb-4 font-mono text-xs sm:text-sm">
                            {errorMessage || 'Could not find the GitHub user. Please check the username and try again.'}
                        </p>
                        <p className="text-black/60 mb-6 font-mono text-xs">
                            Make sure the username is correct and the profile is public.
                        </p>
                        <button
                            onClick={() => {
                                setShowErrorModal(false);
                                onBack();
                            }}
                            className="w-full border-4 border-black bg-[#ff6b6b] text-white hover:bg-[#ff5252] font-black px-6 py-3 transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-1 hover:translate-y-1 cursor-pointer"
                        >
                            RETRY WITH NEW USERNAME
                        </button>
                    </div>
                </div>
            )}

            {/* Connection Lost Modal - Agent Exhaust */}
            {showConnectionLostModal && (
                <div className="fixed inset-0 bg-black/20 backdrop-blur-md flex items-center justify-center z-50 p-4">
                    <div className="bg-white border-4 border-black p-6 sm:p-8 max-w-md w-full shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] animate-slideIn">
                        <div className="flex justify-between items-start mb-4">
                            <h2 className="text-xl sm:text-2xl font-black text-black">Connection Lost! 🔌</h2>
                            <button
                                onClick={() => {
                                    setShowConnectionLostModal(false);
                                    onBack();
                                }}
                                className="text-black hover:text-gray-600 text-2xl font-bold leading-none cursor-pointer"
                            >
                                ×
                            </button>
                        </div>
                        <p className="text-black mb-4 font-mono text-xs sm:text-sm">
                            Our agents got disconnected and couldn't finish the job! This might be due to network issues or server timeout.
                        </p>
                        <p className="text-black/60 mb-6 font-mono text-xs">
                            The agents are exhausted... give them a break and try again! 😴
                        </p>
                        <button
                            onClick={() => {
                                setShowConnectionLostModal(false);
                                onBack();
                            }}
                            className="w-full border-4 border-black bg-[#4ecdc4] text-white hover:bg-[#3dbdb3] font-black px-6 py-3 transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-1 hover:translate-y-1 cursor-pointer"
                        >
                            TRY AGAIN
                        </button>
                    </div>
                </div>
            )}
        </>
    );
}
