"""
FastAPI Backend for GRWM - GitHub README Generator
Implements Server-Sent Events (SSE) for real-time streaming
"""
import os
import asyncio
import uuid
import json
from typing import Dict, Optional, AsyncGenerator
from datetime import datetime

from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents import create_detective_graph, create_initial_state

app = FastAPI(title="GRWM API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://*.vercel.app",   # Vercel deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (use Redis in production)
active_sessions: Dict[str, Dict] = {}


class GenerateRequest(BaseModel):
    username: str
    tone: str = "professional"
    style: str = "modern"


@app.get("/")
async def root():
    return {
        "service": "GRWM API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "active_sessions": len(active_sessions),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/generate")
async def start_generation(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Start README generation and return session_id
    Client uses this to connect to SSE endpoint
    """
    session_id = str(uuid.uuid4())
    print(f"\n{'='*60}")
    print(
        f"🚀 NEW REQUEST: Username='{request.username}', Tone='{request.tone}'")
    print(f"📋 Session ID: {session_id}")
    print(f"{'='*60}\n")

    # Initialize session
    active_sessions[session_id] = {
        "status": "starting",
        "username": request.username,
        "events": [],
        "created_at": datetime.now().isoformat(),
        "preferences": {
            "tone": request.tone,
            "style": request.style
        }
    }
    print(f"✅ Session initialized: {session_id}")

    # Start agent in background
    print(f"🔄 Starting background task for agent execution...")
    background_tasks.add_task(
        run_agent,
        session_id,
        request.username,
        request.tone,
        request.style
    )
    print(f"✅ Background task queued\n")

    return {
        "session_id": session_id,
        "message": "Generation started",
        "stream_url": f"/api/stream/{session_id}"
    }


async def run_agent(session_id: str, username: str, tone: str, style: str):
    """
    Run the LangGraph agent and store events in session
    """
    try:
        active_sessions[session_id]["status"] = "running"

        # Send initial event
        active_sessions[session_id]["events"].append({
            "type": "init",
            "message": f"Starting investigation for @{username}...",
            "timestamp": datetime.now().isoformat()
        })

        # Create graph
        app_graph = create_detective_graph()
        initial_state = create_initial_state(
            username,
            preferences={"tone": tone, "style": style}
        )

        config = {
            "configurable": {"thread_id": session_id},
            "recursion_limit": 15
        }

        # Stream events from graph
        for event in app_graph.stream(initial_state, config):
            event_name = list(event.keys())[0]
            state = event[event_name]
            print(f"   └─ Event type: {event_name}")

            # Transform event to frontend-friendly format
            print(f"   └─ Transforming event for frontend...")
            event_data = transform_event(event_name, state, username)

            if event_data:
                print(
                    f"   └─ ✅ Event data created: {event_data.get('type', 'unknown')}")
                # Store event
                active_sessions[session_id]["events"].append(event_data)
                print(
                    f"   └─ 📤 Event stored in session (total: {len(active_sessions[session_id]['events'])})")

                # Small delay to simulate streaming effect
                await asyncio.sleep(0.2)
            else:
                print(f"   └─ ⚠️ No event data returned from transform")
        active_sessions[session_id]["events"].append({
            "type": "complete",
            "message": "README generation complete! 🎉",
            "timestamp": datetime.now().isoformat()
        })
        print(f"🎉 Session marked as completed\n")

    except Exception as e:
        print(f"\n❌ ERROR in run_agent: {str(e)}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")

        active_sessions[session_id]["status"] = "error"
        active_sessions[session_id]["events"].append({
            "type": "error",
            "message": f"Error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })
        print(f"💾 Error event stored in session\n")


def transform_event(event_name: str, state: Dict, username: str) -> Optional[Dict]:
    """Transform agent state into frontend-friendly event"""
    print(f"\n🔄 transform_event called: {event_name}")

    if event_name == "detective":
        # Check for errors first
        if state.get("error"):
            return {
                "type": "error",
                "stage": "detective",
                "message": state["error"],
                "timestamp": datetime.now().isoformat()
            }

        # Check if data collection is complete
        if state.get("raw_data"):
            raw_data = state["raw_data"]
            profile = raw_data.get("profile", {})

            return {
                "type": "detective_complete",
                "stage": "detective",
                "data": {
                    "profile": {
                        "name": profile.get("name", username),
                        "username": username,
                        "bio": profile.get("bio", ""),
                        "avatar_url": profile.get("avatar_url", ""),
                        "location": profile.get("location", ""),
                        "company": profile.get("company", ""),
                        "email": profile.get("email", ""),
                        "twitter": profile.get("twitter_username", ""),
                        "website": profile.get("blog", ""),
                        "public_repos": profile.get("public_repos", 0),
                        "followers": profile.get("followers", 0),
                        "following": profile.get("following", 0),
                    },
                    "stats": {
                        "repos_count": len(raw_data.get("repositories", [])),
                        "total_stars": raw_data.get("social_proof", {}).get("total_stars", 0),
                        "total_forks": raw_data.get("social_proof", {}).get("total_forks", 0),
                    },
                    # Top 5
                    "repositories": raw_data.get("repositories", [])[:5],
                },
                "message": f"✅ Profile found! Analyzed {len(raw_data.get('repositories', []))} repositories",
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Still in progress
            return {
                "type": "detective_progress",
                "stage": "detective",
                "message": f"🔍 Investigating @{username}'s GitHub profile...",
                "timestamp": datetime.now().isoformat()
            }

    elif event_name == "cto":
        # Check for errors
        if state.get("error"):
            return {
                "type": "error",
                "stage": "cto",
                "message": state["error"],
                "timestamp": datetime.now().isoformat()
            }

        # Check if analysis is complete
        if state.get("analysis"):
            analysis = state["analysis"]

            return {
                "type": "cto_complete",
                "stage": "cto",
                "data": {
                    "archetype": analysis.get("developer_archetype", {}).get("full_title", "Unknown"),
                    "grind_score": analysis.get("grind_score", {}),
                    "primary_language": analysis.get("language_dominance", {}).get("primary_language", {}),
                    "top_languages": analysis.get("language_dominance", {}).get("top_5_languages", []),
                    "key_projects": analysis.get("key_projects", [])[:3],
                    "impact_metrics": analysis.get("impact_metrics", {}),
                    "tech_diversity": analysis.get("tech_diversity", {}),
                    "primary_domains": analysis.get("skill_domains", {}).get("primary_domains", []),
                },
                "message": f"🧠 Analysis complete: {analysis.get('skill_domains', {}).get('personality_comment', '')}",
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Still analyzing
            return {
                "type": "cto_progress",
                "stage": "cto",
                "message": "🧠 The CTO is analyzing your tech stack and contribution patterns...",
                "timestamp": datetime.now().isoformat()
            }

    elif event_name == "ghostwriter":
        # Check for errors
        if state.get("error"):
            return {
                "type": "error",
                "stage": "ghostwriter",
                "message": state["error"],
                "timestamp": datetime.now().isoformat()
            }

        # Check if README is complete
        if state.get("final_markdown"):
            return {
                "type": "ghostwriter_complete",
                "stage": "ghostwriter",
                "data": {
                    "markdown": state["final_markdown"],
                    "length": len(state["final_markdown"]),
                    "word_count": len(state["final_markdown"].split()),
                },
                "message": "✍️ README crafted with love and sarcasm!",
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Still writing
            return {
                "type": "ghostwriter_progress",
                "stage": "ghostwriter",
                "message": "✍️ The Ghostwriter is crafting your README...",
                "timestamp": datetime.now().isoformat()
            }

    return None


@app.get("/api/stream/{session_id}")
async def stream_events(session_id: str):
    """
    Server-Sent Events (SSE) endpoint
    Streams agent events to frontend in real-time
    """
    print(f"\n{'='*60}")
    print(f"🌊 SSE STREAM REQUESTED")
    print(f"Session ID: {session_id}")
    print(f"{'='*60}\n")

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events"""

        if session_id not in active_sessions:
            print(f"❌ Session not found: {session_id}")
            yield f"data: {json.dumps({'type': 'error', 'message': 'Session not found'})}\n\n"
            return

        print(f"✅ Session found, starting event streaming...")

        last_event_idx = 0
        max_wait_time = 180  # 3 minutes timeout
        start_time = datetime.now()

        # Stream events until completion
        while True:
            # Check timeout
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > max_wait_time:
                yield f"data: {json.dumps({'type': 'timeout', 'message': 'Session timeout'})}\n\n"
                break

            session = active_sessions[session_id]
            events = session["events"]

            # Send new events
            if len(events) > last_event_idx:
                new_events = events[last_event_idx:]
                print(f"📤 Sending {len(new_events)} new events to client")
                for i, event in enumerate(new_events):
                    print(
                        f"   └─ Event {last_event_idx + i + 1}: {event.get('type', 'unknown')}")
                    yield f"data: {json.dumps(event)}\n\n"
                last_event_idx = len(events)

            # Check if done
            if session["status"] in ["completed", "error"]:
                # Send final status
                yield f"data: {json.dumps({'type': 'done', 'status': session['status']})}\n\n"

                # Cleanup session after 5 minutes
                asyncio.create_task(cleanup_session(session_id, delay=300))
                break

            # Wait before checking again
            await asyncio.sleep(0.3)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


async def cleanup_session(session_id: str, delay: int = 300):
    """Cleanup session after delay"""
    await asyncio.sleep(delay)
    if session_id in active_sessions:
        del active_sessions[session_id]
        print(f"Cleaned up session: {session_id}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
