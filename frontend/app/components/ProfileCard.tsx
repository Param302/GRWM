'use client';

interface ProfileCardProps {
    profile: {
        name: string;
        username: string;
        bio: string;
        avatar_url: string;
        location: string;
        company: string;
        public_repos: number;
        followers: number;
        following: number;
    };
    analysis: {
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
    } | null;
}

export default function ProfileCard({ profile, analysis }: ProfileCardProps) {
    return (
        <div className="space-y-4">
            {/* Avatar & Name */}
            <div className="border-4 border-black bg-white p-6 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">
                <div className="flex items-start gap-4">
                    {profile.avatar_url && (
                        <div className="border-4 border-black w-20 h-20 flex-shrink-0">
                            <img
                                src={profile.avatar_url}
                                alt={profile.name}
                                className="w-full h-full object-cover"
                            />
                        </div>
                    )}
                    <div className="flex-1 min-w-0">
                        <h3 className="text-xl font-black text-black truncate">{profile.name || profile.username}</h3>
                        <p className="font-mono text-sm text-black/60">@{profile.username}</p>
                        {profile.bio && (
                            <p className="mt-2 text-sm text-black/80 line-clamp-2">{profile.bio}</p>
                        )}
                    </div>
                </div>

                {/* Stats */}
                <div className="mt-4 grid grid-cols-3 gap-2">
                    <div className="border-2 border-black bg-[#f0f0f0] p-2 text-center">
                        <p className="font-mono text-xs text-black/60">REPOS</p>
                        <p className="font-black text-lg text-black">{profile.public_repos}</p>
                    </div>
                    <div className="border-2 border-black bg-[#f0f0f0] p-2 text-center">
                        <p className="font-mono text-xs text-black/60">FOLLOWERS</p>
                        <p className="font-black text-lg text-black">{profile.followers}</p>
                    </div>
                    <div className="border-2 border-black bg-[#f0f0f0] p-2 text-center">
                        <p className="font-mono text-xs text-black/60">FOLLOWING</p>
                        <p className="font-black text-lg text-black">{profile.following}</p>
                    </div>
                </div>

                {/* Location & Company */}
                {(profile.location || profile.company) && (
                    <div className="mt-4 space-y-2">
                        {profile.location && (
                            <p className="font-mono text-sm text-black/70">📍 {profile.location}</p>
                        )}
                        {profile.company && (
                            <p className="font-mono text-sm text-black/70">🏢 {profile.company}</p>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
