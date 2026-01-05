'use client';

import { useState, KeyboardEvent } from 'react';
import { ArrowRight } from 'lucide-react';

interface UsernameInputProps {
    onStart: (username: string) => void;
}

export default function UsernameInput({ onStart }: UsernameInputProps) {
    const [username, setUsername] = useState('');
    const [error, setError] = useState('');

    const extractUsername = (input: string): string => {
        // Remove whitespace
        input = input.trim();

        // Check if it's a GitHub URL and extract username
        const urlPatterns = [
            /^https?:\/\/github\.com\/([a-zA-Z0-9-]+)/i,  // https://github.com/username
            /^github\.com\/([a-zA-Z0-9-]+)/i,             // github.com/username
            /^www\.github\.com\/([a-zA-Z0-9-]+)/i         // www.github.com/username
        ];

        for (const pattern of urlPatterns) {
            const match = input.match(pattern);
            if (match && match[1]) {
                return match[1];
            }
        }

        // Return as-is if not a URL
        return input;
    };

    const validateUsername = (input: string): boolean => {
        // Check for spaces
        if (input.includes(' ')) {
            setError('Username cannot contain spaces');
            return false;
        }

        // Check for valid GitHub username format (alphanumeric and hyphens only)
        if (input && !/^[a-zA-Z0-9-]+$/.test(input)) {
            setError('Username can only contain letters, numbers, and hyphens');
            return false;
        }

        setError('');
        return true;
    };

    const handleInputChange = (input: string) => {
        const extracted = extractUsername(input);
        setUsername(extracted);

        if (extracted) {
            validateUsername(extracted);
        } else {
            setError('');
        }
    };

    const handleSubmit = () => {
        const trimmedUsername = username.trim();

        if (!trimmedUsername) {
            setError('Please enter a username');
            return;
        }

        if (validateUsername(trimmedUsername)) {
            onStart(trimmedUsername);
        }
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && username.trim()) {
            handleSubmit();
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-[#fafafa] px-4 sm:px-6 py-24 md:py-0 relative pb-20 md:pb-0">
            {/* Desktop: Vertical Sidebar - Right Side */}
            <a
                href="https://parampreetsingh.me"
                target="_blank"
                rel="noopener noreferrer"
                className="hidden md:flex fixed right-0 top-1/2 -translate-y-1/2 -rotate-90 origin-center z-50 border-4 border-black bg-white hover:bg-[#ffe66d] transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] p-4 items-center gap-4 cursor-pointer"
            >
                <img
                    src="https://avatars.githubusercontent.com/u/76559816?v=4"
                    alt="Parampreet Singh"
                    className="w-10 h-10 border-2 border-black rotate-90"
                />
                <span className="font-mono font-bold text-sm text-black whitespace-nowrap">Made by Parampreet Singh</span>
            </a>

            {/* Mobile/Tablet: Bottom Center Branding */}
            <a
                href="https://parampreetsingh.me"
                target="_blank"
                rel="noopener noreferrer"
                className="md:hidden fixed bottom-4 left-1/2 -translate-x-1/2 z-50 border-4 border-black bg-white hover:bg-[#ffe66d] transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] p-3 flex items-center gap-3 cursor-pointer"
            >
                <img
                    src="https://avatars.githubusercontent.com/u/76559816?v=4"
                    alt="Parampreet Singh"
                    className="w-8 h-8 border-2 border-black"
                />
                <span className="font-mono font-bold text-xs sm:text-sm text-black whitespace-nowrap">Made by Parampreet Singh</span>
            </a>

            <div className="w-full max-w-2xl">
                {/* Logo/Title */}
                <div className="mb-8 sm:mb-12">
                    <h1 className="text-5xl sm:text-6xl lg:text-[4rem] leading-none font-black tracking-tighter text-black">
                        GRWM
                    </h1>
                    <p className="text-lg sm:text-xl font-mono text-black/70">
                        Get README With Me
                    </p>
                </div>

                {/* Main CTA */}
                <div className="border-4 border-black bg-white p-4 sm:p-6 lg:p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                    <label htmlFor="username" className="block text-sm font-mono font-bold mb-3 text-black uppercase tracking-wide">
                        Enter GitHub Username
                    </label>

                    <input
                        id="username"
                        type="text"
                        value={username}
                        onChange={(e) => handleInputChange(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="octocat"
                        className={`w-full px-4 sm:px-6 py-3 sm:py-4 text-xl sm:text-2xl font-mono border-4 ${error ? 'border-red-600' : 'border-black'} focus:outline-none focus:ring-0 bg-[#fff] text-black placeholder:text-black/30 transition-all`}
                        autoFocus
                    />

                    {/* Error Message */}
                    {error && (
                        <p className="mt-2 text-sm font-mono text-red-600 font-bold">
                            ⚠️ {error}
                        </p>
                    )}

                    <div className="mt-4 sm:mt-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                        <p className="text-xs sm:text-sm font-mono text-black/60">
                            Press <kbd className="px-2 py-1 border-2 border-black bg-[#f0f0f0] font-bold">Enter</kbd> to continue
                        </p>

                        <button
                            onClick={handleSubmit}
                            disabled={!username.trim() || !!error}
                            className="w-full sm:w-auto flex items-center justify-center gap-2 px-5 sm:px-7 py-2.5 sm:py-3 bg-black text-white font-mono font-bold uppercase tracking-wide border-4 border-black hover:bg-white hover:text-black transition-all disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-black disabled:hover:text-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-1 active:translate-y-1 cursor-pointer"
                        >
                            Start
                            <ArrowRight className="w-5 h-5" />

                        </button>
                    </div>
                </div>

                {/* Info Section */}
                <div className="mt-8 sm:mt-12 grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
                    <div className="border-4 border-black bg-[#ff6b6b] p-4">
                        <p className="font-mono font-bold text-sm text-black">01</p>
                        <p className="mt-2 text-sm font-mono text-black font-bold">Multi-Agentic AI</p>
                        <p className="mt-1 text-xs font-mono text-black/70">3 AI agents craft your Github Portfolio</p>
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

                {/* Buy Me A Chai Button */}
                <div className="mt-8 flex justify-center">
                    <a
                        href="https://buymeachai.ezee.li/param302"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-block border-4 border-black bg-white hover:bg-[#ffe66d] transition-all shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:-translate-y-0.5 active:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] active:translate-x-0.5 active:translate-y-0.5 p-2"
                    >
                        <img
                            src="https://buymeachai.ezee.li/assets/images/buymeachai-button.png"
                            alt="Buy Me A Chai"
                            className="w-40 sm:w-48 md:w-52 h-auto block"
                        />
                    </a>
                </div>
            </div>
        </div>
    );
}
