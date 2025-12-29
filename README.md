# 🚀 GRWM - Get README With Me

<div align="center">

![GRWM Banner](https://img.shields.io/badge/GRWM-AI%20Agentic%20Portfolio%20Generator-black?style=for-the-badge&logo=github)

**Revolutionary AI Agentic GitHub Portfolio Generator**  
*Powered by Multi-Agent AI System*

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge)](https://getreadmewithme.vercel.app)
[![Backend](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](backend/)
[![Frontend](https://img.shields.io/badge/Next.js-16.1.1-black?style=for-the-badge&logo=next.js)](frontend/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

[Features](#-features) • [Demo](#-demo) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [API](#-api-documentation)

</div>

---

## 📖 Overview

**GRWM (Get README With Me)** is an **AI Agentic system** that transforms your GitHub profile into a stunning, personalized portfolio README in seconds. Unlike traditional generators, GRWM uses a **Multi-Agent AI architecture** where three specialized AI agents collaborate to analyze your GitHub profile and craft custom-toned professional portfolios.

### 🎯 The Problem

- Creating a compelling GitHub README is time-consuming
- Generic templates don't capture your unique developer identity
- Keeping your profile updated is tedious
- Choosing the right tone and style is challenging

### ✨ The Solution

GRWM automates the entire process using **AI Agentic Workflows** with three specialized agents working in harmony:
- **🔍 Detective Agent**: Investigates your GitHub profile, analyzes repositories, and gathers comprehensive data
- **🧠 CTO Agent**: Performs deep technical analysis, identifies skills, determines developer archetype, and calculates impact metrics
- **✍️ Ghostwriter Agent**: Crafts personalized, engaging README content with custom tones and styles

---

## 🌟 Features

### 🤖 AI Agentic Multi-Agent System
- **3 Specialized AI Agents** working collaboratively
- **LangGraph-powered** workflow orchestration
- **Real-time progress streaming** with Server-Sent Events (SSE)
- **Autonomous decision-making** with intelligent routing

### 🎨 Customization Options
- **4 Style Presets**: Professional, Creative, Minimal, Detailed
- **Custom Tone Control**: Tailor the writing style to your preference
- **Personalized Descriptions**: Add specific requirements or highlights
- **Live Preview**: Dark/Light mode markdown preview

### 📊 Intelligent Analysis
- **Grind Score Calculation**: Measures your GitHub activity and impact
- **Developer Archetype Detection**: Identifies your coding personality
- **Tech Stack Recognition**: Automatically detects languages, frameworks, and tools
- **Key Project Identification**: Highlights your most impactful repositories
- **Social Proof Metrics**: Analyzes stars, forks, and community engagement

### 🚀 Modern Tech Stack
- **Frontend**: Next.js 16.1.1, React 19, TypeScript, TailwindCSS 4
- **Backend**: Python 3.11+, FastAPI, LangGraph, LangChain
- **AI**: Google Gemini Flash (Free Tier)
- **Real-time**: Server-Sent Events (SSE) for live updates
- **PWA**: Installable as Progressive Web App

### 🎁 Additional Features
- Instant download and clipboard copy
- Social media sharing with screenshot capture
- Responsive brutalist design
- SEO optimized with comprehensive metadata
- Zero-cost AI model (Gemini Flash free tier)

---

## 🎬 Demo

Visit the live application: **[getreadmewithme.vercel.app](https://getreadmewithme.vercel.app)**

### How It Works

1. **Enter GitHub Username** - Start with any public GitHub profile
2. **Watch AI Agents Work** - See real-time progress as each agent completes its task
3. **Choose Your Style** - Select from 4 professional style options
4. **Get Your README** - Download, copy, or share your personalized portfolio

---

## 🏗️ Architecture

<details>
<summary><b>📐 System Architecture (Click to expand)</b></summary>

### Multi-Agent Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Home Screen │→│ Progress View │→│ Preview & DL  │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└────────────────────────┬────────────────────────────────────┘
                         │ SSE Connection
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI + SSE)                     │
│                                                               │
│  ┌─────────────────────────────────────────────┐            │
│  │         LangGraph Orchestration              │            │
│  │                                               │            │
│  │  ┌──────────────┐                            │            │
│  │  │ 🔍 DETECTIVE │  Fetches Profile Data      │            │
│  │  │    AGENT     │  • GitHub API Client       │            │
│  │  │              │  • Repository Analysis     │            │
│  │  │              │  • Tech Stack Detection    │            │
│  │  └──────┬───────┘                            │            │
│  │         │ State Flow                         │            │
│  │         ↓                                    │            │
│  │  ┌──────────────┐                            │            │
│  │  │   🧠 CTO     │  Technical Analysis        │            │
│  │  │    AGENT     │  • Language Analysis       │            │
│  │  │              │  • Skill Mapping           │            │
│  │  │              │  • Archetype Detection     │            │
│  │  │              │  • Grind Score Calculation │            │
│  │  └──────┬───────┘                            │            │
│  │         │ Awaits User Style Selection        │            │
│  │         ↓                                    │            │
│  │  ┌──────────────┐                            │            │
│  │  │✍️ GHOSTWRITER│  Content Generation        │            │
│  │  │    AGENT     │  • Gemini Flash LLM        │            │
│  │  │              │  • Tone Instructions       │            │
│  │  │              │  • Style Templates         │            │
│  │  │              │  • Markdown Generation     │            │
│  │  └──────────────┘                            │            │
│  └─────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

### Agent State Management

Each agent maintains and transforms a shared state object:

```python
AgentState = {
    "username": str,
    "user_preferences": {
        "tone": str,      # professional/creative/minimal/detailed
        "style": str,     # user's selected style
        "description": str # custom requirements
    },
    "raw_data": dict,     # Detective's gathered data
    "analysis": dict,     # CTO's analysis results
    "final_markdown": str, # Ghostwriter's output
    "messages": list,     # Agent communication log
    "error": str,         # Error tracking
    "retry_count": int,   # Retry logic
    "intermediate_results": dict,
    "generation_history": list
}
```

</details>

<details>
<summary><b>🔍 Detective Agent - Data Gathering (Click to expand)</b></summary>

### Detective Agent Responsibilities

The Detective is the first agent in the pipeline, responsible for gathering comprehensive GitHub profile data.

**Key Components:**
- **GitHubAPIClient**: Interfaces with GitHub REST API
- **ProfileDetective**: Fetches user profile information
- **RepositoryStalker**: Analyzes repositories (stars, forks, languages)
- **ExReadme**: Checks for existing README files
- **TechStackDetective**: Identifies technologies and frameworks

**Data Collected:**
```python
{
    "profile": {
        "name", "username", "bio", "location",
        "company", "public_repos", "followers", "following"
    },
    "repositories": [
        {
            "name", "description", "stars", "forks",
            "language", "topics", "is_pinned", "is_archived"
        }
    ],
    "social_proof": {
        "total_stars", "total_forks", "total_repos"
    },
    "contributions": {
        "total_commits", "active_streak"
    },
    "existing_readme": str  # If found
}
```

**Performance Optimization:**
- Parallel API requests using `asyncio`
- Smart caching for rate limit management
- Efficient data batching

</details>

<details>
<summary><b>🧠 CTO Agent - Technical Analysis (Click to expand)</b></summary>

### CTO Agent Responsibilities

The CTO Agent performs deep technical analysis of the developer's profile and codebase.

**Analysis Components:**

1. **Language Analysis**
   - Primary and secondary languages
   - Language distribution percentages
   - Specialization detection

2. **Tech Stack Mapping**
   - Framework identification
   - Tool detection
   - Technology categorization

3. **Developer Archetype**
   - Personality classification (e.g., "The Full-Stack Wizard", "The Backend Architect")
   - Based on language diversity and project patterns

4. **Grind Score Calculation**
   ```python
   factors = [
       ("Commit Frequency", 0.25),
       ("Code Consistency", 0.20),
       ("Project Diversity", 0.15),
       ("Community Impact", 0.20),
       ("Code Quality", 0.20)
   ]
   # Score: 0-100 with emoji indicators
   ```

5. **Key Projects Identification**
   - Sorts by stars, forks, and recency
   - Identifies most impactful repositories
   - Extracts project metadata

6. **Impact Metrics**
   - Social proof aggregation
   - Contribution patterns
   - Community engagement scores

**Output Structure:**
```python
{
    "grind_score": {"score": int, "label": str, "emoji": str},
    "developer_archetype": {"title": str, "full_title": str},
    "language_analysis": {"primary": dict, "distribution": list},
    "skill_mapping": {"languages": list, "frameworks": list, "tools": list},
    "tech_diversity": {"score": float, "description": str},
    "key_projects": list,
    "impact_metrics": dict
}
```

</details>

<details>
<summary><b>✍️ Ghostwriter Agent - Content Generation (Click to expand)</b></summary>

### Ghostwriter Agent Responsibilities

The Ghostwriter is the creative director, transforming raw data and analysis into engaging README content.

**Generation Process:**

1. **Tone Selection** (4 options)
   - **Professional**: Polished, corporate-ready language
   - **Creative**: Bold, expressive with personality
   - **Minimal**: Clean, data-focused, concise
   - **Detailed**: Comprehensive, thorough coverage

2. **Style Templates** (4 options)
   - **Professional Style**: Clean sections, organized skills, business impact
   - **Creative Style**: Unique formatting, storytelling, visual elements
   - **Minimal Style**: Essential info only, whitespace-focused
   - **Detailed Style**: Comprehensive sections, extensive project showcase

3. **LLM Integration**
   - Uses **Google Gemini Flash** (free tier)
   - Structured prompts with tone and style instructions
   - Custom requirements injection from user input
   - Post-processing for markdown formatting

4. **Content Structure**
   ```markdown
   # Personalized Header with Archetype
   ## About Me (tone-adjusted)
   ## Skills & Technologies (categorized)
   ## Featured Projects (key projects highlighted)
   ## GitHub Statistics (visual badges)
   ## Connect With Me (social links)
   ```

5. **Smart Features**
   - Shields.io badge integration
   - GitHub stats widgets
   - Responsive image handling
   - Markdown optimization

**Revision Support:**
- Maintains generation history
- Supports revision instructions
- Version tracking

</details>

<details>
<summary><b>🔄 Real-time Communication - SSE Implementation (Click to expand)</b></summary>

### Server-Sent Events (SSE) Architecture

GRWM uses SSE for real-time, unidirectional streaming from backend to frontend.

**Why SSE over WebSockets?**
- Simpler implementation for one-way updates
- Better for event streaming
- Automatic reconnection
- Lower overhead
- HTTP/2 multiplexing support

**Event Flow:**

```typescript
Frontend subscribes to SSE endpoint:
GET /api/generate/{session_id}/stream

Backend emits events:
{
  type: "detective_progress" | "detective_complete" |
        "cto_progress" | "cto_complete" |
        "ghostwriter_progress" | "ghostwriter_complete" |
        "awaiting_style_selection",
  stage: "detective" | "cto" | "ghostwriter",
  message: string,
  timestamp: ISO string,
  data?: any
}
```

**Session Management:**
- UUID-based session tracking
- In-memory storage (scalable to Redis)
- Thread-safe queues for event routing
- Automatic cleanup on completion

**Frontend Integration:**
```typescript
const eventSource = new EventSource(`/api/generate/${sessionId}/stream`);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Update UI based on event type
  setEvents(prev => [...prev, data]);
};
```

</details>

---

## 🛠️ Installation

### Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.11+ (for backend)
- **GitHub Personal Access Token** (for API access)
- **Google Gemini API Key** (free tier available)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOL
GITHUB_PAT=your_github_token_here
GEMINI_API_KEY=your_gemini_api_key_here
EOL

# Run the server
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env.local file
cat > .env.local << EOL
NEXT_PUBLIC_API_URL=http://localhost:8000
EOL

# Run development server
npm run dev
```

### Production Build

```bash
# Frontend
npm run build
npm start

# Backend (use gunicorn or uvicorn in production)
gunicorn api:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 📱 Usage

### Basic Flow

1. **Start the Application**
   - Open `http://localhost:3000` in your browser
   - Or visit the live demo at [getreadmewithme.vercel.app](https://getreadmewithme.vercel.app)

2. **Enter GitHub Username**
   - Type any public GitHub username
   - Press Enter or click "START"

3. **Watch the Agents Work**
   - 🔍 Detective gathers profile data (5-10 seconds)
   - 🧠 CTO analyzes your tech stack (5-8 seconds)
   - ⏸️ System awaits your style selection

4. **Customize Your README**
   - Choose from 4 style options
   - (Optional) Add custom description for specific requirements

5. **Get Your README**
   - ✍️ Ghostwriter generates your portfolio (10-15 seconds)
   - Preview in dark/light mode
   - Download, copy, or share

### Advanced Usage

<details>
<summary><b>Testing Individual Agents (Click to expand)</b></summary>

```bash
cd backend

# Test Detective Agent only
python test_agents.py
# Select option 1

# Test CTO Agent (requires Detective data)
python test_agents.py
# Select option 2

# Test Ghostwriter Agent (requires both)
python test_agents.py
# Select option 3

# Test complete pipeline
python test_agents.py
# Select option 4
```

</details>

<details>
<summary><b>Direct Agent Usage (Click to expand)</b></summary>

```python
from agents import (
    create_detective_graph,
    create_initial_state,
    GhostwriterAgent
)

# Create the agent graph
app = create_detective_graph()

# Initialize state
initial_state = create_initial_state(
    username="octocat",
    preferences={
        "tone": "professional",
        "style": "modern"
    }
)

# Run Detective and CTO
for event in app.stream(initial_state):
    print(event)

# Get final state
final_state = next(iter(event.values()))

# Run Ghostwriter separately
ghostwriter = GhostwriterAgent()
result = ghostwriter(final_state)

print(result["final_markdown"])
```

</details>

---

## 📡 API Documentation

### Endpoints

#### 1. **POST /api/generate**
Start a new README generation session.

**Request:**
```json
{
  "username": "octocat",
  "tone": "professional",
  "style": "modern"
}
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "message": "Generation started"
}
```

#### 2. **GET /api/generate/{session_id}/stream**
Server-Sent Events endpoint for real-time progress updates.

**Events:**
- `detective_progress`: Detective agent working
- `detective_complete`: Detective finished
- `cto_progress`: CTO agent analyzing
- `cto_complete`: CTO finished
- `awaiting_style_selection`: Waiting for user to choose style
- `ghostwriter_progress`: Ghostwriter generating
- `ghostwriter_complete`: README ready

#### 3. **POST /api/generate/{session_id}/continue**
Continue generation after style selection.

**Request:**
```json
{
  "style": "professional",
  "description": "Highlight my open-source contributions"
}
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "message": "Continuing with Ghostwriter"
}
```

#### 4. **GET /api/generate/{session_id}/result**
Get the final generated README.

**Response:**
```json
{
  "session_id": "uuid-string",
  "username": "octocat",
  "markdown": "# Full README content...",
  "analysis": {
    "grind_score": {...},
    "developer_archetype": {...}
  }
}
```

<details>
<summary><b>📋 Complete API Reference (Click to expand)</b></summary>

### Error Handling

All endpoints return standardized error responses:

```json
{
  "detail": "Error message",
  "error": "INTERNAL_ERROR | NOT_FOUND | VALIDATION_ERROR",
  "timestamp": "2025-12-29T12:00:00Z"
}
```

### Rate Limiting

- GitHub API: 5000 requests/hour (authenticated)
- Gemini API: Free tier limits apply
- SSE connections: 100 concurrent per server

### CORS Configuration

```python
allow_origins = [
    "http://localhost:3000",
    "https://*.vercel.app"
]
```

</details>

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run test suite
python test_agents.py

# Test options:
# 1. Detective Agent Only
# 2. CTO Agent Only  
# 3. Ghostwriter Agent Only
# 4. Complete Pipeline
```

### Frontend Tests

```bash
cd frontend

# Run type checking
npm run type-check

# Build test
npm run build

# Lint
npm run lint
```

---

## 🚀 Deployment

### Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel
```

### Backend (Railway/Render/Fly.io)

```bash
# Example: Railway
railway login
railway init
railway up
```

### Environment Variables

**Backend (.env):**
```env
GITHUB_PAT=ghp_xxxxxxxxxxxxx
GEMINI_API_KEY=AIxxxxxxxxxxxx
PORT=8000
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

---

## 🎨 Customization

<details>
<summary><b>Adding New Tones (Click to expand)</b></summary>

Edit `backend/agents.py`:

```python
def _get_tone_instructions(self, tone: str) -> str:
    instructions = {
        "professional": "...",
        "creative": "...",
        "minimal": "...",
        "your_new_tone": """
        TONE: Your Custom Tone Description
        - Instruction 1
        - Instruction 2
        """
    }
    return instructions.get(tone, instructions["professional"])
```

</details>

<details>
<summary><b>Adding New Styles (Click to expand)</b></summary>

Edit `backend/agents.py`:

```python
def _get_style_instructions(self, style: str) -> str:
    instructions = {
        "professional": "...",
        "creative": "...",
        "minimal": "...",
        "your_new_style": """
        STYLE: Your Custom Style
        SECTIONS TO INCLUDE:
        - Section 1
        - Section 2
        """
    }
    return instructions.get(style, instructions["professional"])
```

Update frontend `LoadingPanel.tsx`:

```typescript
const styles = [
    { id: 'professional', name: 'Professional', icon: Briefcase, color: 'bg-blue-50' },
    // Add your new style
    { id: 'your_new_style', name: 'Your Style', icon: YourIcon, color: 'bg-custom' },
];
```

</details>

---

## 📊 Tech Stack

### Frontend
- **Framework**: Next.js 16.1.1 (React 19.2.3)
- **Language**: TypeScript 5
- **Styling**: TailwindCSS 4 (Brutalist Design)
- **UI Components**: Custom + Lucide Icons
- **Markdown**: ReactMarkdown + remark-gfm + rehype-raw
- **PWA**: Service Worker + Web Manifest
- **Screenshot**: html2canvas-pro

### Backend
- **Framework**: FastAPI 0.115+
- **Language**: Python 3.11+
- **AI/ML**: LangGraph, LangChain, Google Gemini Flash
- **GitHub API**: PyGithub + httpx
- **State Management**: LangGraph MemorySaver
- **Async**: asyncio, uvicorn
- **Environment**: python-dotenv

### Infrastructure
- **Frontend Hosting**: Vercel
- **Backend Hosting**: Railway/Render/Fly.io
- **CDN**: Vercel Edge Network
- **Domain**: Custom domain support

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the Repository**
2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit Your Changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **Push to the Branch**
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Open a Pull Request**

### Development Guidelines
- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini** for providing free-tier AI models
- **LangGraph** for agent orchestration framework
- **GitHub API** for profile data access
- **Shields.io** for beautiful badges
- **Vercel** for seamless deployment

---

## 🐛 Known Issues & Roadmap

### Current Limitations
- Single session per user (no concurrent generations)
- In-memory session storage (not production-scalable)
- Limited to public GitHub profiles
- GitHub API rate limits apply

### Roadmap
- [ ] Redis-based session storage
- [ ] User authentication & saved READMEs
- [ ] Multiple README versions
- [ ] Private repository support (OAuth)
- [ ] More customization options
- [ ] Batch generation for organizations
- [ ] Analytics dashboard
- [ ] API key management for users

---

## 📞 Contact & Support

**Created by:** Parampreet Singh

**Email:** connectwithparam.30@gmail.com

**Portfolio:** [parampreetsingh.me](https://parampreetsingh.me)

**GitHub:** [@Param302](https://github.com/Param302)

**Live Demo:** [getreadmewithme.vercel.app](https://getreadmewithme.vercel.app)

---

<div align="center">

### ⭐ Star this repository if you found it helpful!

**Made with ❤️ by [Parampreet Singh](https://parampreetsingh.me)**

[![GitHub stars](https://img.shields.io/github/stars/Param302/GRWM?style=social)](https://github.com/Param302/GRWM)
[![Follow on GitHub](https://img.shields.io/github/followers/Param302?label=Follow&style=social)](https://github.com/Param302)

</div>
