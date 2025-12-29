'use client';

import { useState } from 'react';
import UsernameInput from './components/UsernameInput';
import GenerationFlow from './components/GenerationFlow';

export default function Home() {
  const [started, setStarted] = useState(false);
  const [username, setUsername] = useState('');

  const handleStart = (user: string) => {
    setUsername(user);
    setStarted(true);
  };

  return (
    <div className="min-h-screen bg-[#fafafa] overflow-hidden">
      <div className="relative w-full h-screen">
        {/* Username Input Screen */}
        <div
          className={`absolute inset-0 transition-transform duration-700 ease-in-out ${started ? '-translate-x-full' : 'translate-x-0'
            }`}
        >
          <UsernameInput onStart={handleStart} />
        </div>

        {/* Generation Flow Screen */}
        <div
          className={`absolute inset-0 transition-transform duration-700 ease-in-out ${started ? 'translate-x-0' : 'translate-x-full'
            }`}
        >
          {started && (
            <GenerationFlow
              username={username}
              onBack={() => setStarted(false)}
            />
          )}
        </div>
      </div>
    </div>
  );
}
