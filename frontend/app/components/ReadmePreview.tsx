'use client';

import { useState } from 'react';

interface ReadmePreviewProps {
    markdown: string;
    username: string;
}

export default function ReadmePreview({ markdown, username }: ReadmePreviewProps) {
    const [copied, setCopied] = useState(false);
    const [downloading, setDownloading] = useState(false);

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(markdown);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (error) {
            console.error('Failed to copy:', error);
        }
    };

    const handleDownload = () => {
        try {
            setDownloading(true);
            const blob = new Blob([markdown], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${username}-README.md`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            setTimeout(() => setDownloading(false), 1000);
        } catch (error) {
            console.error('Failed to download:', error);
            setDownloading(false);
        }
    };

    return (
        <div className="h-full flex flex-col bg-[#fafafa]">
            {/* Header with Actions */}
            <div className="border-b-4 border-black bg-white p-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-2xl font-black text-black">YOUR README</h2>
                        <p className="font-mono text-sm text-black/60">
                            {markdown.split('\n').length} lines • {markdown.length} characters
                        </p>
                    </div>

                    <div className="flex gap-3">
                        <button
                            onClick={handleCopy}
                            className="px-6 py-3 bg-[#4ecdc4] border-4 border-black font-mono font-bold uppercase tracking-wide hover:bg-[#3db5ad] transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-1 active:translate-y-1"
                        >
                            {copied ? '✓ COPIED!' : '📋 COPY'}
                        </button>

                        <button
                            onClick={handleDownload}
                            disabled={downloading}
                            className="px-6 py-3 bg-[#ff6b6b] border-4 border-black font-mono font-bold uppercase tracking-wide hover:bg-[#ff5252] transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-1 active:translate-y-1 disabled:opacity-50"
                        >
                            {downloading ? '⏳ SAVING...' : '⬇ DOWNLOAD'}
                        </button>
                    </div>
                </div>
            </div>

            {/* Markdown Preview */}
            <div className="flex-1 overflow-y-auto p-6">
                <div className="border-4 border-black bg-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                    <div className="border-b-4 border-black bg-[#f0f0f0] p-3">
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-[#ff6b6b] border-2 border-black"></div>
                            <div className="w-3 h-3 rounded-full bg-[#ffe66d] border-2 border-black"></div>
                            <div className="w-3 h-3 rounded-full bg-[#4ecdc4] border-2 border-black"></div>
                            <span className="ml-3 font-mono text-xs text-black/60">README.md</span>
                        </div>
                    </div>

                    <div className="p-8">
                        <pre className="font-mono text-sm text-black whitespace-pre-wrap break-words">
                            {markdown}
                        </pre>
                    </div>
                </div>

                {/* Success Message */}
                <div className="mt-6 border-4 border-black bg-[#ffe66d] p-6 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">
                    <p className="font-black text-lg text-black mb-2">🎉 README GENERATED!</p>
                    <p className="font-mono text-sm text-black/70">
                        Copy the markdown above and paste it into your GitHub profile README.md file.
                        Don't have one? Create a repository with the same name as your username and add a README.md file.
                    </p>
                </div>
            </div>
        </div>
    );
}
