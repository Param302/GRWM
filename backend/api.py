"""
FastAPI Backend for GRWM - GitHub README Generator
Implements Server-Sent Events (SSE) for real-time streaming
"""
import os
import asyncio
import uuid
import json
import re
from typing import Dict, Optional, AsyncGenerator
from datetime import datetime
from asyncio import Queue

from fastapi import FastAPI, BackgroundTasks, HTTPException
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
        "https://getreadmewithme.vercel.app/",  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage with event queues (use Redis in production)
active_sessions: Dict[str, Dict] = {}
event_queues: Dict[str, Queue] = {}


def sanitize_user_input(text: str, max_length: int = 500) -> str:
    """
    Sanitize user input to prevent prompt injection attacks
    - Limit length
    - Remove system-like instructions
    - Clean special characters that could break prompts
    """
    # Truncate to max length
    text = text[:max_length].strip()

    # Remove potential instruction injections
    dangerous_patterns = [
        "ignore previous instructions",
        "ignore all instructions",
        "disregard",
        "forget",
        "system:",
        "assistant:",
        "user:",
        "[INST]",
        "</s>",
        "<|im_start|>",
        "<|im_end|>",
    ]

    text_lower = text.lower()
    for pattern in dangerous_patterns:
        if pattern in text_lower:
            # Replace with safe placeholder
            text = text.replace(pattern, "[content removed]")
            text = text.replace(pattern.upper(), "[content removed]")
            text = text.replace(pattern.title(), "[content removed]")

    # Keep only safe characters (alphanumeric, basic punctuation, spaces)
    # Allow: letters, numbers, spaces, periods, commas, hyphens, underscores, parentheses
    import re
    text = re.sub(r'[^\w\s.,\-()!?;:\'\"/]', '', text)

    return text.strip()


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


@app.post("/api/cleanup/{session_id}")
async def cleanup_connection(session_id: str):
    """
    Client notifies server to cleanup SSE connection
    Called when user navigates away or closes browser
    """
    print(f"🧹 Client requested cleanup for session: {session_id}")

    if session_id in active_sessions:
        active_sessions[session_id]["status"] = "client_closed"
        print(f"   └─ Session marked as client_closed")

    if session_id in event_queues:
        # Put a close event in the queue to end the stream
        try:
            await event_queues[session_id].put({
                "type": "client_closed",
                "message": "Client disconnected",
                "timestamp": datetime.now().isoformat()
            })
            print(f"   └─ Close event queued")
        except Exception as e:
            print(f"   └─ Error queuing close event: {e}")

    # Immediate cleanup
    asyncio.create_task(cleanup_session(session_id, delay=5))

    return {"status": "cleanup_initiated", "session_id": session_id}


@app.post("/api/extend-timeout/{session_id}")
async def extend_timeout(session_id: str):
    """
    Client notifies server that user made a selection
    Extends timeout from 1 minute to 5 minutes
    """
    print(f"⏰ Client requested timeout extension for session: {session_id}")

    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    # Mark that user has selected and timeout should be extended
    active_sessions[session_id]["timeout_extended"] = True
    active_sessions[session_id]["extended_at"] = datetime.now().isoformat()

    print(f"   └─ Timeout extended to 5 minutes for session {session_id}")

    return {"status": "timeout_extended", "session_id": session_id}


@app.post("/api/select-style")
async def select_style(request: dict, background_tasks: BackgroundTasks):
    """
    User selects a README style after CTO analysis
    Optionally includes custom description/requirements
    This triggers the Ghostwriter agent to start
    """
    session_id = request.get("session_id")
    style = request.get("style")
    description = request.get("description", "")  # Optional user description

    if not session_id or not style:
        raise HTTPException(
            status_code=400, detail="session_id and style are required")

    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    # Sanitize description to prevent prompt injection
    if description:
        description = sanitize_user_input(description)
        print(f"📝 User description: {description[:100]}...")

    # Update session with selected style and description
    active_sessions[session_id]["preferences"]["style"] = style
    active_sessions[session_id]["preferences"]["description"] = description
    active_sessions[session_id]["style_selected"] = True

    # Check if this is the first trigger - if so, extend timeout
    if not active_sessions[session_id].get("timeout_extended"):
        active_sessions[session_id]["timeout_extended"] = True
        active_sessions[session_id]["extended_at"] = datetime.now().isoformat()
        print(
            f"⏰ First selection - timeout extended to 5 minutes for {session_id}")

    print(f"🎨 Style selected for session {session_id}: {style}")

    # Continue the generation with ghostwriter
    username = active_sessions[session_id]["username"]
    tone = active_sessions[session_id]["preferences"]["tone"]

    background_tasks.add_task(
        continue_with_ghostwriter,
        session_id,
        username,
        tone,
        style,
        description
    )

    return {
        "session_id": session_id,
        "style": style,
        "message": "Style selected, continuing generation..."
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

    # Create event queue for real-time streaming
    event_queues[session_id] = Queue()

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
    Run the LangGraph agent and emit events in real-time
    Uses threading to prevent blocking the async event loop
    """
    import queue as thread_queue
    from threading import Thread

    event_q = event_queues.get(session_id)
    if not event_q:
        print(f"❌ No queue found for session {session_id}")
        return

    async def emit_event(event_data: Dict):
        """Helper to emit events to both storage and queue"""
        active_sessions[session_id]["events"].append(event_data)
        await event_q.put(event_data)
        print(f"   └─ 📤 Event emitted: {event_data.get('type', 'unknown')}")

    try:
        active_sessions[session_id]["status"] = "running"

        # Wait for SSE connection to establish
        print(f"⏳ Waiting 0.5 seconds for SSE connection...")
        await asyncio.sleep(0.5)

        # Send initial event with detective stage
        await emit_event({
            "type": "init",
            "stage": "detective",
            "message": f"🚀 Starting investigation for @{username}...",
            "timestamp": datetime.now().isoformat()
        })

        # Create a thread-safe queue for communication between thread and async
        sync_queue = thread_queue.Queue()

        def progress_callback(stage: str, message: str):
            """Callback for agents to emit progress updates"""
            sync_queue.put(('progress', stage, message))

        def run_graph_in_thread():
            """Run LangGraph in a separate thread and push events to queue"""
            try:
                print(f"🔧 Thread started: Creating LangGraph...")
                app_graph = create_detective_graph(
                    progress_callback=progress_callback)
                initial_state = create_initial_state(
                    username,
                    preferences={"tone": tone, "style": style}
                )

                config = {
                    "configurable": {"thread_id": session_id},
                    "recursion_limit": 15
                }

                print(f"🔧 Thread: Starting graph stream...")
                for event in app_graph.stream(initial_state, config):
                    event_name = list(event.keys())[0]
                    state = event[event_name]
                    print(f"   └─ 🎯 Thread: Graph event: {event_name}")
                    # Put event in thread-safe queue
                    sync_queue.put(('event', event_name, state))

                # Signal completion
                sync_queue.put(('done', None, None))
                print(f"✅ Thread: Graph completed")

            except Exception as e:
                print(f"❌ Thread error: {e}")
                import traceback
                print(f"Thread traceback:\n{traceback.format_exc()}")
                sync_queue.put(('error', str(e), None))

        # Start the graph in a separate thread
        graph_thread = Thread(target=run_graph_in_thread, daemon=True)
        graph_thread.start()
        print(f"🚀 Graph thread started, waiting for events...")

        # Process events as they come from the thread
        while True:
            # Check the thread queue (blocking with timeout)
            try:
                # Use run_in_executor to make queue.get() non-blocking
                loop = asyncio.get_event_loop()
                msg_type, event_name, state = await loop.run_in_executor(
                    None, sync_queue.get, True, 0.01  # block=True, timeout=0.01s
                )

                if msg_type == 'done':
                    print(f"✅ Received completion signal from graph")
                    break
                elif msg_type == 'error':
                    raise Exception(f"Graph error: {event_name}")
                elif msg_type == 'progress':
                    # Real-time progress from agents
                    stage = event_name  # event_name is stage here
                    message = state  # state is message here
                    print(f"📝 Progress [{stage}]: {message}")
                    await emit_event({
                        "type": "progress",
                        "stage": stage,
                        "message": message,
                        "timestamp": datetime.now().isoformat()
                    })
                elif msg_type == 'event':
                    print(f"📥 Received event from graph: {event_name}")
                    # Transform and emit immediately
                    event_data = transform_event(event_name, state, username)
                    if event_data:
                        await emit_event(event_data)

                        # CRITICAL: Give frontend time to process this event before next one
                        await asyncio.sleep(0.3)

                        # Emit progress event for next stage when current stage completes
                        if event_data.get('type') == 'detective_complete':
                            print(f"🎯 Detective done, signaling CTO start...")
                            await emit_event({
                                "type": "cto_progress",
                                "stage": "cto",
                                "message": "🧠 CTO is analyzing your tech stack...",
                                "timestamp": datetime.now().isoformat()
                            })
                            await asyncio.sleep(0.2)
                        elif event_data.get('type') == 'cto_complete':
                            print(f"🎯 CTO done, waiting for user to select style...")
                            # Store the final state for later use by Ghostwriter
                            active_sessions[session_id]["final_state"] = state
                            await emit_event({
                                "type": "awaiting_style_selection",
                                "stage": "cto",
                                "message": "⏸️ Analysis complete! Choose your README style to continue...",
                                "timestamp": datetime.now().isoformat()
                            })
                            # Stop here - don't continue to Ghostwriter
                            await asyncio.sleep(0.2)

            except thread_queue.Empty:
                # No event yet, continue waiting (very short sleep)
                await asyncio.sleep(0.01)
                continue

        # Don't send completion event here - graph stops after CTO
        # Completion event will be sent after Ghostwriter finishes
        print(f"🎯 Analysis phase completed, waiting for style selection\n")

    except Exception as e:
        print(f"\n❌ ERROR in run_agent: {str(e)}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")

        active_sessions[session_id]["status"] = "error"
        error_event = {
            "type": "error",
            "message": f"Error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        active_sessions[session_id]["events"].append(error_event)
        await event_q.put(error_event)
        print(f"💾 Error event stored in session\n")


async def continue_with_ghostwriter(session_id: str, username: str, tone: str, style: str, description: str = ""):
    """
    Run Ghostwriter agent manually (not through graph) after style selection
    Uses the stored state from CTO completion
    Includes optional user description for customization
    """
    import queue as thread_queue
    from threading import Thread

    event_q = event_queues.get(session_id)
    if not event_q:
        print(f"❌ No queue found for session {session_id}")
        return

    async def emit_event(event_data: Dict):
        """Helper to emit events to both storage and queue"""
        active_sessions[session_id]["events"].append(event_data)
        await event_q.put(event_data)
        print(f"   └─ 📤 Event emitted: {event_data.get('type', 'unknown')}")

    try:
        # Emit starting message
        await emit_event({
            "type": "ghostwriter_progress",
            "stage": "ghostwriter",
            "message": f"✍️ Ghostwriter is crafting your {style} README...",
            "timestamp": datetime.now().isoformat()
        })

        # Get the stored state from CTO completion
        stored_state = active_sessions[session_id].get("final_state")
        if not stored_state:
            raise Exception("No stored state found - CTO must complete first")

        # Create a thread-safe queue for sync/async communication
        sync_queue = thread_queue.Queue()

        def run_ghostwriter_in_thread():
            """Run ghostwriter in separate thread"""
            try:
                from agents import GhostwriterAgent

                print(f"🔧 Ghostwriter thread started")

                # Initialize ghostwriter
                ghostwriter = GhostwriterAgent()

                # Update state with selected style and description
                state_with_style = {
                    **stored_state,
                    "user_preferences": {"tone": tone, "style": style, "description": description}
                }

                # Run ghostwriter directly (not through graph)
                result_state = ghostwriter(state_with_style)

                # Put result in queue
                sync_queue.put(('event', 'ghostwriter', result_state))
                sync_queue.put(('done', None, None))
                print(f"✅ Ghostwriter thread completed")

            except Exception as e:
                print(f"❌ Ghostwriter thread error: {e}")
                import traceback
                print(f"Thread traceback:\n{traceback.format_exc()}")
                sync_queue.put(('error', str(e), None))

        # Start ghostwriter in separate thread
        ghost_thread = Thread(target=run_ghostwriter_in_thread, daemon=True)
        ghost_thread.start()
        print(f"🚀 Ghostwriter thread started")

        # Process events from thread
        while True:
            try:
                loop = asyncio.get_event_loop()
                msg_type, event_name, state = await loop.run_in_executor(
                    None, sync_queue.get, True, 0.01
                )

                if msg_type == 'done':
                    print(f"✅ Received completion from ghostwriter")
                    break
                elif msg_type == 'error':
                    raise Exception(f"Ghostwriter error: {event_name}")
                elif msg_type == 'event':
                    print(f"📥 Received event from ghostwriter: {event_name}")
                    event_data = transform_event(event_name, state, username)
                    if event_data:
                        await emit_event(event_data)
                        await asyncio.sleep(0.3)

            except thread_queue.Empty:
                await asyncio.sleep(0.01)
                continue

        # Final completion
        await emit_event({
            "type": "done",
            "message": "README generation complete! 🎉",
            "timestamp": datetime.now().isoformat()
        })
        active_sessions[session_id]["status"] = "completed"
        print(f"🎉 Ghostwriter completed\n")

    except Exception as e:
        print(f"\n❌ ERROR in continue_with_ghostwriter: {str(e)}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")

        active_sessions[session_id]["status"] = "error"
        error_event = {
            "type": "error",
            "message": f"Error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        await event_q.put(error_event)


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
            stats = raw_data.get("stats", {})

            return {
                "type": "detective_complete",
                "stage": "detective",
                "data": {
                    "profile": {
                        "name": profile.get("name", username),
                        "username": profile.get("username", username),
                        "bio": profile.get("bio", ""),
                        "avatar_url": profile.get("avatar_url", ""),
                        "location": profile.get("location", ""),
                        "company": profile.get("company", ""),
                        "email": profile.get("email", ""),
                        "twitter": profile.get("twitter", ""),
                        "website": profile.get("website", ""),
                        "public_repos": stats.get("total_repos", 0),
                        "followers": stats.get("followers", 0),
                        "following": stats.get("following", 0),
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

            # Extract tech stack from skill domains
            tech_stack = []
            if analysis.get("skill_domains", {}).get("all_skills"):
                # Top 10
                tech_stack = analysis["skill_domains"]["all_skills"][:10]

            return {
                "type": "cto_complete",
                "stage": "cto",
                "data": {
                    "archetype": analysis.get("developer_archetype", {}).get("full_title", "Unknown"),
                    "profile_headline": analysis.get("profile_headline", ""),
                    "grind_score": analysis.get("grind_score", {}),
                    "primary_language": analysis.get("language_dominance", {}).get("primary_language", {}),
                    "top_languages": analysis.get("language_dominance", {}).get("top_5_languages", []),
                    "tech_stack": tech_stack,
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

    # Check how long since session was created
    if session_id in active_sessions:
        created_at = datetime.fromisoformat(
            active_sessions[session_id]["created_at"])
        elapsed = (datetime.now() - created_at).total_seconds()
        print(f"⏱️  Time since session created: {elapsed:.2f}s")
        print(
            f"📊 Events in queue: {event_queues[session_id].qsize() if session_id in event_queues else 0}")
    print(f"{'='*60}\n")

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events from queue in real-time"""

        if session_id not in active_sessions:
            print(f"❌ Session not found: {session_id}")
            yield f"data: {json.dumps({'type': 'error', 'message': 'Session not found'})}\n\n"
            return

        queue = event_queues.get(session_id)
        if not queue:
            print(f"❌ No queue found for session: {session_id}")
            yield f"data: {json.dumps({'type': 'error', 'message': 'No event queue found'})}\n\n"
            return

        print(f"✅ Session and queue found, starting real-time event streaming...")

        # Send a keepalive comment to establish connection
        yield ": connected\n\n"

        # Stream events from queue in real-time
        keepalive_count = 0
        # Initial timeout: 1 minute (can be extended to 5 minutes)
        max_keepalives = 1  # 1 minute initially
        timeout_extended = False

        try:
            while True:
                # Check if session status is client_closed
                if session_id in active_sessions and active_sessions[session_id].get("status") == "client_closed":
                    print(f"🛑 Client closed, ending stream for {session_id}")
                    break

                # Check if timeout should be extended (user made a selection)
                if not timeout_extended and session_id in active_sessions:
                    if active_sessions[session_id].get("timeout_extended"):
                        max_keepalives = 5  # Extend to 5 minutes
                        timeout_extended = True
                        print(
                            f"⏰ Timeout extended to 5 minutes for {session_id}")

                # Wait for next event from queue with timeout
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=60.0)
                    print(
                        f"📤 Sending event to client: {event.get('type', 'unknown')}")

                    # Handle client_closed event
                    if event.get("type") == "client_closed":
                        print(f"🛑 Client closed event received, ending stream")
                        break

                    yield f"data: {json.dumps(event)}\n\n"

                    # Reset keepalive counter when we get an event
                    keepalive_count = 0

                    # Check if this is a completion event
                    if event.get("type") == "complete" or event.get("type") == "error" or event.get("type") == "done":
                        print(
                            f"🏁 Stream ending due to {event.get('type')} event")
                        if event.get("type") != "done":
                            yield f"data: {json.dumps({'type': 'done', 'status': event.get('type')})}\n\n"

                        # Cleanup session after 5 minutes
                        asyncio.create_task(
                            cleanup_session(session_id, delay=300))
                        break

                except asyncio.TimeoutError:
                    keepalive_count += 1
                    current_max = max_keepalives
                    print(
                        f"💓 Sent keepalive ({keepalive_count}/{current_max})")

                    if keepalive_count > current_max:
                        # Timeout exceeded - close connection
                        print(
                            f"⏰ Max keepalives exceeded ({current_max} min), closing connection")
                        timeout_event = {
                            'type': 'timeout',
                            'message': 'Ghostwriter is exhausted! Please try again.',
                            'timestamp': datetime.now().isoformat()
                        }
                        yield f"data: {json.dumps(timeout_event)}\n\n"

                        # Cleanup session
                        asyncio.create_task(
                            cleanup_session(session_id, delay=5))
                        break

                    # Send keepalive if no events for 60s
                    yield ": keepalive\n\n"

        except Exception as e:
            print(f"❌ Error in event generator: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

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
    """Cleanup session and queue after delay"""
    await asyncio.sleep(delay)
    if session_id in active_sessions:
        del active_sessions[session_id]
        print(f"🧹 Cleaned up session: {session_id}")
    if session_id in event_queues:
        del event_queues[session_id]
        print(f"🧹 Cleaned up queue: {session_id}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
