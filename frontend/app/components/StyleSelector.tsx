'use client';

interface StyleSelectorProps {
    selectedStyle: string;
    onStyleChange: (style: string) => void;
    disabled: boolean;
}

const styles = [
    {
        id: 'professional',
        name: 'Professional',
        description: 'Clean and polished',
        color: 'bg-[#3b82f6]'
    },
    {
        id: 'genz',
        name: 'GenZ',
        description: 'Vibes and emojis',
        color: 'bg-[#ec4899]'
    },
    {
        id: 'minimalist',
        name: 'Minimalist',
        description: 'Less is more',
        color: 'bg-[#6b7280]'
    },
    {
        id: 'creative',
        name: 'Creative',
        description: 'Stand out loud',
        color: 'bg-[#f59e0b]'
    }
];

export default function StyleSelector({ selectedStyle, onStyleChange, disabled }: StyleSelectorProps) {
    return (
        <div className="space-y-3">
            <p className="font-mono text-sm text-black/60 mb-4">
                Choose a style for your README
            </p>

            {styles.map((style) => (
                <button
                    key={style.id}
                    onClick={() => !disabled && onStyleChange(style.id)}
                    disabled={disabled}
                    className={`w-full border-4 border-black p-4 text-left transition-all ${selectedStyle === style.id
                            ? 'bg-black text-white shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]'
                            : 'bg-white text-black hover:translate-x-1 hover:translate-y-1 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]'
                        } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                >
                    <div className="flex items-center gap-3">
                        <div className={`w-4 h-4 border-2 ${selectedStyle === style.id ? 'border-white bg-white' : 'border-black'
                            }`}></div>
                        <div className="flex-1">
                            <p className="font-black text-base">{style.name}</p>
                            <p className={`font-mono text-xs ${selectedStyle === style.id ? 'text-white/70' : 'text-black/60'
                                }`}>
                                {style.description}
                            </p>
                        </div>
                    </div>
                </button>
            ))}

            {disabled && (
                <p className="font-mono text-xs text-black/40 mt-4">
                    Style selection available after generation
                </p>
            )}
        </div>
    );
}
