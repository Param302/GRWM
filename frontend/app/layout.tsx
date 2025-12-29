import type { Metadata } from "next";
import { Space_Grotesk, Space_Mono } from "next/font/google";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

const spaceMono = Space_Mono({
  variable: "--font-space-mono",
  subsets: ["latin"],
  weight: ["400", "700"],
});

export const metadata: Metadata = {
  metadataBase: new URL('https://getreadmewithme.vercel.app'),
  title: {
    default: 'GRWM - Get README With Me | AI Agentic GitHub Portfolio Generator with Multi-Agent System',
    template: '%s | GRWM - AI Agentic Portfolio Generator'
  },
  description: 'Get README With Me (GRWM) - Revolutionary AI Agentic GitHub Portfolio Generator powered by Multi-Agent AI System. 3 specialized AI agents (Detective, CTO, Ghostwriter) work together to craft personalized, custom-toned professional README portfolios instantly. Transform your GitHub profile with AI-driven automation. Perfect for developers, engineers, and GitHub users worldwide. #AIAgents #MultiAgentAI #GitHubProfile #READMEGenerator',
  keywords: [
    // Primary Keywords - AI Agentic Focus
    'AI Agentic system',
    'Multi-Agent AI',
    'AI Agent system',
    'Agentic AI',
    'Multi-Agent system',
    'AI Agents collaboration',
    'Autonomous AI agents',

    // GRWM Specific
    'Get README With Me',
    'GRWM',
    'GRWM app',
    'GetReadmeWithMe',

    // GitHub User Targeting
    'GitHub portfolio generator',
    'GitHub profile README',
    'GitHub README maker',
    'GitHub profile generator',
    'GitHub user portfolio',
    'developer GitHub profile',
    'engineer GitHub portfolio',
    'GitHub profile creator',
    'professional GitHub profile',

    // AI-Powered Features
    'AI README generator',
    'AI README maker',
    'AI-powered GitHub',
    'AI Portfolio generator',
    'AI-powered portfolio',
    'AI GitHub profile',
    'automated README',
    'AI-driven README',
    'intelligent README generator',

    // Custom Toned & Styling
    'custom toned README',
    'personalized README',
    'styled README',
    'professional README',
    'creative README',
    'minimal README',
    'detailed README',
    'custom GitHub portfolio',

    // Developer Tools
    'README generator',
    'README maker',
    'README creator',
    'portfolio generator',
    'developer portfolio',
    'developer profile generator',
    'GitHub tools',
    'developer tools',

    // Technical Keywords
    'multi-agentic workflow',
    'AI workflow automation',
    'agentic workflow',
    'AI portfolio automation',
    'GitHub automation',
    'profile automation',

    // Use Case Keywords
    'software developer portfolio',
    'software engineer profile',
    'data scientist GitHub',
    'web developer portfolio',
    'frontend developer profile',
    'backend developer portfolio',
    'fullstack developer profile',

    // Hashtags for AI Engines
    '#AIAgents',
    '#MultiAgentAI',
    '#AgenticAI',
    '#GitHubProfile',
    '#READMEGenerator',
    '#DeveloperTools',
    '#AIAutomation',
    '#GitHubPortfolio'
  ],
  authors: [{ name: 'Parampreet Singh', url: 'https://parampreetsingh.me' }],
  creator: 'Parampreet Singh',
  publisher: 'Parampreet Singh',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://getreadmewithme.vercel.app',
    title: 'GRWM - AI Agentic GitHub Portfolio Generator | Multi-Agent AI System',
    description: 'Revolutionary AI Agentic system with 3 specialized AI agents working together to create personalized, custom-toned GitHub portfolio READMEs. Perfect for every GitHub user - from students to senior engineers. Transform your profile instantly with Multi-Agent AI automation.',
    siteName: 'GRWM - Get README With Me',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'GRWM - AI Agentic GitHub Portfolio Generator with Multi-Agent System',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'GRWM - AI Agentic GitHub Portfolio Generator',
    description: 'Revolutionary Multi-Agent AI system with 3 specialized agents creating custom-toned GitHub portfolios. Perfect for every developer. #AIAgents #MultiAgentAI #GitHubProfile',
    creator: '@Param302',
    images: ['/og-image.png'],
  },
  manifest: '/manifest.json',
  icons: {
    icon: [
      { url: '/favicon.ico' },
      { url: '/icon-192.png', sizes: '192x192', type: 'image/png' },
      { url: '/icon-512.png', sizes: '512x512', type: 'image/png' },
    ],
    apple: [
      { url: '/apple-icon.png', sizes: '180x180', type: 'image/png' },
    ],
  },
  category: 'technology',
  alternates: {
    canonical: 'https://getreadmewithme.vercel.app',
  },
  other: {
    'google-site-verification': 'pending',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
        <meta name="theme-color" content="#fafafa" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="GRWM" />
        <link rel="canonical" href="https://getreadmewithme.vercel.app" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "WebApplication",
              "name": "GRWM - Get README With Me",
              "alternateName": "GRWM",
              "url": "https://getreadmewithme.vercel.app",
              "description": "Revolutionary AI Agentic GitHub Portfolio Generator powered by Multi-Agent AI System. 3 specialized AI agents (Detective, CTO, Ghostwriter) collaborate to create personalized, custom-toned professional README portfolios instantly. Perfect for all GitHub users - developers, engineers, and programmers worldwide.",
              "applicationCategory": "DeveloperApplication",
              "operatingSystem": "Any",
              "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
              },
              "creator": {
                "@type": "Person",
                "name": "Parampreet Singh",
                "url": "https://parampreetsingh.me",
                "email": "connectwithparam.30@gmail.com"
              },
              "featureList": [
                "AI Agentic Multi-Agent System",
                "3 Specialized AI Agents (Detective, CTO, Ghostwriter)",
                "Custom-Toned Portfolio Generation",
                "4 Professional Styles (Professional, Creative, Minimal, Detailed)",
                "Real-time Live Generation",
                "Personalized Developer Profiles",
                "Automated GitHub Portfolio Creation"
              ],
              "keywords": "AI Agentic system, Multi-Agent AI, GitHub portfolio generator, custom toned README, AI agents collaboration, GitHub profile maker, developer portfolio, #AIAgents #MultiAgentAI #GitHubProfile"
            })
          }}
        />
      </head>
      <body
        className={`${spaceGrotesk.variable} ${spaceMono.variable} antialiased font-sans`}
      >
        {children}
      </body>
    </html>
  );
}
