'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { Info, Copy, Check, FileDown, Share2, Search, Brain, Pen, Twitter, Linkedin, Link, Moon, Sun, HelpCircle, ArrowLeft, Briefcase, Sparkles, Minimize2, List, Send, Mail } from 'lucide-react';

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
    onStyleChange?: (style: string, description?: string) => void;
    finalMarkdown?: string;
    username?: string;
}

const stageInfo = {
    detective: {
        title: 'THE DETECTIVE',
        icon: Search,
        description: 'Investigating your GitHub profile...'
    },
    cto: {
        title: 'THE CTO',
        icon: Brain,
        description: 'Analyzing your tech stack and patterns...'
    },
    ghostwriter: {
        title: 'THE GHOSTWRITER',
        icon: Pen,
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
    const [showInfo, setShowInfo] = useState(false);
    const [showShare, setShowShare] = useState(false);
    const [darkMode, setDarkMode] = useState(false);
    const [userDescription, setUserDescription] = useState('');
    const [showDescriptionInput, setShowDescriptionInput] = useState(false);
    const [tempSelectedStyle, setTempSelectedStyle] = useState('');
    const [screenshot, setScreenshot] = useState<string | null>(null);

    // Check completion status for each stage
    const detectiveCompleted = events.some(e => e.type === 'detective_complete');
    const ctoCompleted = events.some(e => e.type === 'cto_complete');
    const ghostwriterCompleted = events.some(e => e.type === 'ghostwriter_complete');

    const styles = [
        { id: 'professional', name: 'Professional', desc: 'Polished and corporate-ready', icon: Briefcase, color: 'bg-blue-50' },
        { id: 'creative', name: 'Creative', desc: 'Bold and expressive', icon: Sparkles, color: 'bg-purple-50' },
        { id: 'minimal', name: 'Minimal', desc: 'Clean and concise', icon: Minimize2, color: 'bg-green-50' },
        { id: 'detailed', name: 'Detailed', desc: 'Comprehensive coverage', icon: List, color: 'bg-amber-50' },
    ];

    const handleStyleSelect = (styleId: string) => {
        setTempSelectedStyle(styleId);
        setShowDescriptionInput(true);
    };

    const handleGenerate = () => {
        if (onStyleChange && tempSelectedStyle) {
            onStyleChange(tempSelectedStyle, userDescription);
            setShowDescriptionInput(false);
        }
    };

    const handleSkip = () => {
        if (onStyleChange && tempSelectedStyle) {
            onStyleChange(tempSelectedStyle, '');
            setUserDescription('');
            setShowDescriptionInput(false);
        }
    };

    const handleCopy = async () => {
        if (finalMarkdown) {
            await navigator.clipboard.writeText(finalMarkdown);
            setCopied(true);
            setTimeout(() => setCopied(false), 3000);
        }
    };

    const handleDownload = () => {
        if (finalMarkdown) {
            const blob = new Blob([finalMarkdown], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${username || 'github'}-README.md`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    };

    const handleShare = async (platform: string) => {
        const text = `I just generated my GitHub README with "Get README With Me"! 🚀`;
        const url = window.location.href;

        const shareUrls: Record<string, string> = {
            twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`,
            linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
            reddit: `https://reddit.com/submit?url=${encodeURIComponent(url)}&title=${encodeURIComponent(text)}`,
            email: `mailto:?subject=${encodeURIComponent('Check out Get README With Me!')}&body=${encodeURIComponent(text + '\n\n' + url)}`,
            whatsapp: `https://wa.me/?text=${encodeURIComponent(text + ' ' + url)}`,
            instagram: url, // Instagram doesn't have direct web sharing, so just copy link
        };

        if (platform === 'copyLink') {
            navigator.clipboard.writeText(url);
            alert('Link copied!');
        } else if (platform === 'copyImage') {
            if (screenshot) {
                try {
                    const blob = await (await fetch(screenshot)).blob();
                    await navigator.clipboard.write([
                        new ClipboardItem({ 'image/png': blob })
                    ]);
                    alert('Image copied!');
                } catch (err) {
                    console.error('Failed to copy image:', err);
                    alert('Failed to copy image. Try downloading instead.');
                }
            }
        } else if (platform === 'instagram') {
            navigator.clipboard.writeText(url);
            alert('Link copied!');
        } else {
            window.open(shareUrls[platform], '_blank', 'width=600,height=400');
        }
    };

    return (
        <div className="h-full flex flex-col bg-[#fafafa]">
            {/* Project Header */}
            <div className="border-b-4 border-black bg-white p-6">
                <div className="flex items-center justify-between">
                    <div>
                        <span className="flex gap-2 items-end">
                            <h1 className="text-4xl font-black text-black">GRWM</h1>
                            <h3 className="text-xl font-semibold text-black"> - Get README With Me</h3>
                        </span>
                        <p className="font-mono text-sm text-black/60 mt-1">Multi-Agentic AI-Powered GitHub Portfolio Generator</p>
                    </div>
                    {finalMarkdown && (
                        <div className="flex items-center gap-4">
                            <div className="text-right">
                                <p className="font-mono text-sm font-bold text-black">Share it with your friends!</p>
                                <p className="font-mono text-xs text-black/60">Spread the word on social media</p>
                            </div>
                            <button
                                onClick={async () => {
                                    // Capture screenshot of entire visible webpage first, then open modal
                                    try {
                                        const html2canvas = (await import('html2canvas-pro')).default;
                                        // Capture the entire document body (whole page)
                                        const canvas = await html2canvas(document.body, {
                                            scale: 0.5,
                                            backgroundColor: '#fafafa',
                                            logging: false,
                                            useCORS: true,
                                            allowTaint: true,
                                            ignoreElements: (element) => {
                                                // Skip modal overlays to avoid capturing them
                                                return element.classList?.contains('fixed');
                                            }
                                        });
                                        const imgData = canvas.toDataURL('image/png');
                                        setScreenshot(imgData);
                                    } catch (error) {
                                        console.error('Screenshot capture failed:', error);
                                        // Set null if fails but still open modal
                                        setScreenshot(null);
                                    }
                                    // Open modal after screenshot attempt
                                    setShowShare(true);
                                }}
                                className="px-4 py-2 border-4 border-black bg-white hover:bg-[#ff6b6b] font-black transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1"
                                title="Share"
                            >
                                <Share2 className="w-5 h-5" />
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {/* README Actions Header - Show when README is ready */}
            {finalMarkdown && (
                <div className="border-b-4 border-black bg-white p-6">
                    <div className="flex items-center justify-between gap-4">
                        <div className="flex items-center gap-3">
                            <h2 className="text-2xl font-black text-black">Your GitHub Portfolio is Ready!</h2>
                            <button
                                onClick={() => setShowInfo(true)}
                                className="p-2 border-4 border-black bg-white hover:bg-gray-100 font-black transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1 flex items-center gap-2"
                                title="How to use this README"
                            >
                                <HelpCircle className="w-5 h-5" />
                                <span className="text-sm">How to</span>
                            </button>
                        </div>
                        <div className="flex items-center gap-3">
                            <button
                                onClick={handleCopy}
                                disabled={copied}
                                className={`p-3 border-4 border-black font-black transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1 ${copied
                                    ? 'bg-[#4ecdc4] text-black cursor-default'
                                    : 'bg-[#4ecdc4] hover:bg-[#3dbab1] text-black'
                                    }`}
                                title={copied ? 'Copied!' : 'Copy to clipboard'}
                            >
                                {copied ? <Check className="w-6 h-6" /> : <Copy className="w-6 h-6" />}
                            </button>
                            <button
                                onClick={handleDownload}
                                className="p-3 border-4 border-black bg-[#ffe66d] hover:bg-[#ffd93d] font-black text-black transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1"
                                title="Export as README.md"
                            >
                                <FileDown className="w-6 h-6" />
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Progress Stages - Hide when README is ready */}
            {!finalMarkdown && (
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

                            const IconComponent = info.icon;
                            return (
                                <div
                                    key={stage}
                                    className={`flex-1 border-4 border-black p-4 transition-all relative ${stageStatus === 'active'
                                        ? 'bg-[#ffe66d] shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]'
                                        : stageStatus === 'completed'
                                            ? 'bg-[#4ecdc4]'
                                            : 'bg-[#f0f0f0]'
                                        }`}
                                >
                                    {/* Active signal indicator */}
                                    {stageStatus === 'active' && (
                                        <div className="absolute top-2 right-2 flex gap-1">
                                            <div className="w-2 h-2 bg-black rounded-full animate-pulse"></div>
                                            <div className="w-2 h-2 bg-black rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                                            <div className="w-2 h-2 bg-black rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                                        </div>
                                    )}
                                    <IconComponent className="w-8 h-8 mb-2" />
                                    <p className="font-mono text-xs font-bold text-black">{info.title}</p>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Style Selector - Show after CTO completes, before README */}
            {showStyleSelector && onStyleChange && (
                <div className="border-b-4 border-black bg-white p-6 overflow-hidden">
                    <h3 className="font-black text-xl mb-4 text-black uppercase">What's Special About Your Portfolio?</h3>
                    <p className="text-sm text-gray-600 mb-4">Choose a style that represents you best</p>

                    <div className="flex gap-4 transition-all duration-500">
                        {/* Style Options - Slides to left when description shown */}
                        <div className={`transition-all duration-500 ${showDescriptionInput ? 'w-[35%]' : 'w-full'}`}>
                            <div className={`grid gap-3 ${showDescriptionInput ? 'grid-cols-1' : 'grid-cols-4'}`}>
                                {styles.map((style) => {
                                    const StyleIcon = style.icon;
                                    return (
                                        <button
                                            key={style.id}
                                            onClick={() => handleStyleSelect(style.id)}
                                            className={`border-3 border-black p-3 text-center transition-all ${tempSelectedStyle === style.id
                                                ? 'bg-black text-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] scale-105'
                                                : `${style.color} text-black hover:translate-x-1 hover:translate-y-1 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]`
                                                }`}
                                        >
                                            <div className="flex items-center gap-2 justify-center">
                                                <StyleIcon className={`${showDescriptionInput ? 'w-4 h-4' : 'w-6 h-6'}`} />
                                                <div className={`font-bold ${showDescriptionInput ? 'text-xs' : 'text-xs'}`}>{style.name}</div>
                                            </div>
                                        </button>
                                    );
                                })}
                            </div>
                        </div>

                        {/* Description Input - Slides in from right */}
                        {showDescriptionInput && tempSelectedStyle && (
                            <div className="w-[65%] animate-slide-in-right">
                                <div className="flex flex-col h-full">
                                    <div className="relative">
                                        <textarea
                                            value={userDescription}
                                            onChange={(e) => setUserDescription(e.target.value)}
                                            placeholder="Want something specific in your portfolio? Mention key projects, skills, or achievements you'd like highlighted... (Optional)"
                                            className="w-full h-32 p-3 pb-8 border-3 border-black font-mono text-sm focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all resize-none"
                                            maxLength={500}
                                        />
                                        <p className="absolute bottom-2 right-3 text-xs text-gray-500 font-mono">{userDescription.length}/500</p>
                                    </div>

                                    <div className="flex gap-3 mt-3">
                                        <button
                                            onClick={handleSkip}
                                            className="flex-1 border-3 border-black bg-[#4a90e2] text-white hover:bg-[#357abd] font-black px-4 py-2 transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-1 hover:translate-y-1 text-sm"
                                        >
                                            SKIP & CONTINUE
                                        </button>
                                        <button
                                            onClick={handleGenerate}
                                            className="flex-1 border-3 border-black bg-black text-white hover:bg-gray-800 font-black px-4 py-2 transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-1 hover:translate-y-1 text-sm"
                                        >
                                            ENTER
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* README Preview - Show when ghostwriter completes */}
            {finalMarkdown ? (
                <>
                    {/* README Content with Markdown Rendering */}
                    <div className="flex-1 overflow-y-auto p-6 bg-[#fafafa]">
                        <div className="border-4 border-black bg-white relative">
                            {/* Floating Theme Toggle */}
                            <button
                                onClick={() => setDarkMode(!darkMode)}
                                className="sticky top-4 float-right z-50 p-3 border-4 border-black bg-white hover:bg-gray-100 font-black transition-all shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-x-1 hover:translate-y-1 ml-4 mb-4 mr-4"
                                title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
                            >
                                {darkMode ? <Sun className="w-6 h-6" /> : <Moon className="w-6 h-6" />}
                            </button>
                            <div className={`p-8 markdown-body ${darkMode ? 'markdown-dark' : 'markdown-light'}`}>
                                <ReactMarkdown
                                    remarkPlugins={[remarkGfm]}
                                    rehypePlugins={[rehypeRaw]}
                                    components={{
                                        img: ({ node, ...props }) => (
                                            <img
                                                {...props}
                                                loading="lazy"
                                                style={{ display: 'inline-block', maxWidth: '100%' }}
                                                onError={(e) => {
                                                    // Fallback if image fails to load
                                                    const target = e.target as HTMLImageElement;
                                                    target.style.display = 'none';
                                                }}
                                            />
                                        ),
                                        a: ({ node, ...props }) => (
                                            <a {...props} target="_blank" rel="noopener noreferrer" />
                                        ),
                                    }}
                                >
                                    {finalMarkdown}
                                </ReactMarkdown>
                            </div>
                        </div>
                    </div>
                </>
            ) : (
                <>
                    {/* Event Logs - Reversed (latest first) */}
                    <div className="flex-1 overflow-y-auto p-6">
                        <h3 className="font-mono text-sm font-bold text-black/60 mb-4 uppercase">Live Log</h3>
                        <div className="space-y-2">
                            {/* Animated Loading Indicator - At Top */}
                            {events.length > 0 && !finalMarkdown && (
                                <div className={`border-4 p-4 flex items-center gap-3 transition-all ${showStyleSelector
                                    ? 'border-black bg-[#ffe66d] animate-pulse'
                                    : 'border-black bg-white'
                                    }`}>
                                    <div className="flex gap-1">
                                        <div className="w-3 h-3 bg-black rounded-full animate-bounce"></div>
                                        <div className="w-3 h-3 bg-black rounded-full animate-bounce" style={{ animationDelay: '200ms' }}></div>
                                        <div className="w-3 h-3 bg-black rounded-full animate-bounce" style={{ animationDelay: '400ms' }}></div>
                                    </div>
                                    <span className={`font-mono font-bold ${showStyleSelector ? 'text-black text-base' : 'text-black/60 text-sm'
                                        }`}>
                                        {showStyleSelector ? "👉 Waiting for you to pick your vibe... no rush tho 😎" : "Processing..."}
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
                                .map((event, index) => {
                                    // Calculate opacity based on position (latest = full opacity)
                                    const getOpacity = (index: number) => {
                                        if (index === 0) return 'opacity-100'; // Latest - full
                                        if (index === 1) return 'opacity-80';  // Latest - 1
                                        if (index === 2) return 'opacity-60';  // Latest - 2
                                        if (index === 3) return 'opacity-40';  // Latest - 3
                                        return 'opacity-20';                    // Latest - 4 and older
                                    };

                                    // Check if message contains Ghostwriter crafting text
                                    const isGhostwriterCrafting = event.message.includes('Ghostwriter is crafting');

                                    return (
                                        <div
                                            key={events.length - index}
                                            className={`border-2 border-black p-3 font-mono text-sm transition-opacity duration-300 ${getOpacity(index)} ${event.type === 'error'
                                                ? 'bg-[#ff6b6b] text-black'
                                                : isGhostwriterCrafting
                                                    ? 'bg-[#4a90e2] text-white font-bold'
                                                    : event.type.includes('complete')
                                                        ? 'bg-[#4ecdc4] text-black'
                                                        : event.type === 'progress'
                                                            ? 'bg-[#ffe66d] text-black'
                                                            : 'bg-white text-black'
                                                }`}
                                        >
                                            <div className="flex items-start gap-2">
                                                <span className={`text-xs mt-0.5 ${isGhostwriterCrafting ? 'text-white/60' : 'text-black/40'}`}>
                                                    {event.timestamp && !isNaN(new Date(event.timestamp).getTime())
                                                        ? `[${new Date(event.timestamp).toLocaleTimeString()}]`
                                                        : ''}
                                                </span>
                                                <span className="flex-1">{event.message}</span>
                                            </div>
                                        </div>
                                    );
                                })}
                        </div>
                    </div>
                </>
            )}

            {/* Info Popup Modal */}
            {showInfo && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowInfo(false)}>
                    <div className="border-4 border-black bg-white p-8 max-w-lg w-full shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-2xl font-black text-black">How to Update Your GitHub Profile</h3>
                            <button onClick={() => setShowInfo(false)} className="text-2xl font-black hover:text-[#ff6b6b]">
                                ✕
                            </button>
                        </div>
                        <div className="space-y-4 font-mono text-sm">
                            <div className="flex gap-3">
                                <span className="font-black text-lg">1.</span>
                                <p>Go to your GitHub profile at <span className="font-bold">github.com/{username}</span></p>
                            </div>
                            <div className="flex gap-3">
                                <span className="font-black text-lg">2.</span>
                                <p>Create a new repository with your username: <span className="font-bold">{username}</span></p>
                            </div>
                            <div className="flex gap-3">
                                <span className="font-black text-lg">3.</span>
                                <p>Make it <span className="font-bold">public</span> (it won't work if it's private!)</p>
                            </div>
                            <div className="flex gap-3">
                                <span className="font-black text-lg">4.</span>
                                <p>Create a <span className="font-bold">README.md</span> file in that repository</p>
                            </div>
                            <div className="flex gap-3">
                                <span className="font-black text-lg">5.</span>
                                <p>Copy your generated README content and paste it there</p>
                            </div>
                            <div className="flex gap-3">
                                <span className="font-black text-lg">6.</span>
                                <p>Commit the changes and watch your profile come to life! 🚀</p>
                            </div>
                        </div>
                        <button
                            onClick={() => setShowInfo(false)}
                            className="mt-6 w-full px-6 py-3 border-4 border-black bg-[#4ecdc4] hover:bg-[#3dbab1] font-black text-black transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1"
                        >
                            GOT IT!
                        </button>
                    </div>
                </div>
            )}

            {/* Share Popup Modal */}
            {showShare && (
                <div className="fixed inset-0 bg-black/20 backdrop-blur-md flex items-center justify-center z-50 p-4" onClick={() => setShowShare(false)}>
                    <div className="border-4 border-black bg-white p-8 max-w-2xl w-full shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-2xl font-black text-black flex items-center gap-2">
                                <Share2 className="w-6 h-6" />
                                Share Your README
                            </h3>
                            <button onClick={() => setShowShare(false)} className="text-2xl font-black hover:text-[#ff6b6b]">
                                ✕
                            </button>
                        </div>

                        {/* Screenshot Preview */}
                        {screenshot && (
                            <div className="mb-6 border-4 border-black overflow-hidden">
                                <img src={screenshot} alt="Page Screenshot" className="w-full h-auto" />
                            </div>
                        )}

                        <p className="font-mono text-sm text-black/70 mb-4 font-bold">Share on social media:</p>

                        {/* Social Media Icon Buttons */}
                        <div className="flex gap-3 mb-6 justify-center flex-wrap">
                            <button
                                onClick={() => handleShare('twitter')}
                                className="p-4 border-4 border-black bg-[#1DA1F2] hover:bg-[#1a8cd8] transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1"
                                title="Share on X (Twitter)"
                            >
                                <Twitter className="w-6 h-6 text-white" />
                            </button>
                            <button
                                onClick={() => handleShare('linkedin')}
                                className="p-4 border-4 border-black bg-[#0077B5] hover:bg-[#006399] transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1"
                                title="Share on LinkedIn"
                            >
                                <Linkedin className="w-6 h-6 text-white" />
                            </button>
                            <button
                                onClick={() => handleShare('reddit')}
                                className="p-4 border-4 border-black bg-[#FF4500] hover:bg-[#e03d00] transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1"
                                title="Share on Reddit"
                            >
                                <Share2 className="w-6 h-6 text-white" />
                            </button>
                            <button
                                onClick={() => handleShare('email')}
                                className="p-4 border-4 border-black bg-[#EA4335] hover:bg-[#d33b2c] transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1"
                                title="Share via Email"
                            >
                                <Mail className="w-6 h-6 text-white" />
                            </button>
                            <button
                                onClick={() => handleShare('whatsapp')}
                                className="p-4 border-4 border-black bg-[#25D366] hover:bg-[#20bd5a] transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1"
                                title="Share on WhatsApp"
                            >
                                <Send className="w-6 h-6 text-white" />
                            </button>
                            <button
                                onClick={() => handleShare('instagram')}
                                className="p-4 border-4 border-black bg-gradient-to-br from-[#833AB4] via-[#E1306C] to-[#F77737] hover:opacity-90 transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1"
                                title="Share on Instagram"
                            >
                                <Share2 className="w-6 h-6 text-white" />
                            </button>
                        </div>

                        {/* Copy Buttons */}
                        <div className="flex gap-3">
                            <button
                                onClick={() => handleShare('copyImage')}
                                className="flex-1 px-6 py-4 border-4 border-black bg-[#4ecdc4] hover:bg-[#3dbab1] font-black text-black transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1 flex items-center justify-center gap-2"
                            >
                                <Copy className="w-5 h-5" />
                                <span>COPY IMAGE</span>
                            </button>
                            <button
                                onClick={() => handleShare('copyLink')}
                                className="flex-1 px-6 py-4 border-4 border-black bg-[#ffe66d] hover:bg-[#ffd93d] font-black text-black transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1 flex items-center justify-center gap-2"
                            >
                                <Link className="w-5 h-5" />
                                <span>COPY LINK</span>
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
