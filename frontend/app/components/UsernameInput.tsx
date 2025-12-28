'use client';

import { useState, KeyboardEvent } from 'react';
import { ArrowRight } from 'lucide-react';

interface UsernameInputProps {
    onStart: (username: string, tone: string) => void;
}

export default function UsernameInput({ onStart }: UsernameInputProps) {
    const [username, setUsername] = useState('');

    const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && username.trim()) {
            onStart(username.trim(), 'professional');
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-[#fafafa] px-6 relative">
            {/* Vertical Sidebar - Right Side */}
            <a
                href="https://parampreetsingh.me"
                target="_blank"
                rel="noopener noreferrer"
                className="fixed right-0 top-1/2 -translate-y-1/2 -rotate-90 origin-center z-50 border-4 border-black bg-white hover:bg-[#ffe66d] transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] p-4 flex items-center gap-4 cursor-pointer"
            >
                <img
                    src="https://avatars.githubusercontent.com/u/76559816?v=4"
                    alt="Parampreet Singh"
                    className="w-10 h-10 border-2 border-black rotate-90"
                />
                <span className="font-mono font-bold text-sm text-black whitespace-nowrap">Made by Parampreet Singh</span>
            </a>

            <div className="w-full max-w-2xl">
                {/* Logo/Title */}
                <div className="mb-12">
                    <h1 className="text-[4rem] leading-none font-black tracking-tighter text-black">
                        GRWM
                    </h1>
                    <p className="text-xl font-mono text-black/70 ">
                        Get README With Me
                    </p>
                </div>

                {/* Main CTA */}
                <div className="border-4 border-black bg-white p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                    <label htmlFor="username" className="block text-sm font-mono font-bold mb-3 text-black uppercase tracking-wide">
                        Enter GitHub Username
                    </label>

                    <input
                        id="username"
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="octocat"
                        className="w-full px-6 py-4 text-2xl font-mono border-4 border-black focus:outline-none focus:ring-0 bg-[#fff] text-black placeholder:text-black/30 transition-all"
                        autoFocus
                    />

                    <div className="mt-6 flex items-center justify-between">
                        <p className="text-sm font-mono text-black/60">
                            Press <kbd className="px-2 py-1 border-2 border-black bg-[#f0f0f0] font-bold">Enter</kbd> to continue
                        </p>

                        <button
                            onClick={() => username.trim() && onStart(username.trim(), 'professional')}
                            disabled={!username.trim()}
                            className="flex items-center gap-2 px-7 py-3 bg-black text-white font-mono font-bold uppercase tracking-wide border-4 border-black hover:bg-white hover:text-black transition-all disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-black disabled:hover:text-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-1 active:translate-y-1"
                        >
                            Start
                            <ArrowRight className="w-5 h-5" />

                        </button>
                    </div>
                </div>

                {/* Info Section */}
                <div className="mt-12 grid grid-cols-3 gap-4">
                    <div className="border-4 border-black bg-[#ff6b6b] p-4">
                        <p className="font-mono font-bold text-sm text-black">01</p>
                        <p className="mt-2 text-sm font-mono text-black font-bold">Multi-Agentic AI</p>
                        <p className="mt-1 text-xs font-mono text-black/70">3 AI agents craft your <br/> Github Portfolio</p>
                    </div>
                    <div className="border-4 border-black bg-[#4ecdc4] p-4">
                        <p className="font-mono font-bold text-sm text-black">02</p>
                        <p className="mt-2 text-sm font-mono text-black font-bold">Styled READMEs</p>
                        <p className="mt-1 text-xs font-mono text-black/70">Custom styled profiles for every developer</p>
                    </div>
                    <div className="border-4 border-black bg-[#ffe66d] p-4">
                        <p className="font-mono font-bold text-sm text-black">03</p>
                        <p className="mt-2 text-sm font-mono text-black font-bold">Real-Time Magic</p>
                        <p className="mt-1 text-xs font-mono text-black/70">Watch AI agents work live</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
