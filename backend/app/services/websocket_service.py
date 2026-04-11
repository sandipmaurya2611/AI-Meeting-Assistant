import asyncio
from queue import Queue
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect
import logging
import json

logger = logging.getLogger(__name__)

# Global AI queue
ai_queue: Queue = Queue()

# Active WebSocket connections
active_connections: Set[WebSocket] = set()


def push_ai_suggestion(data: dict):
    """
    Push AI suggestion to the queue.
    This will be picked up by all connected WebSocket clients.
    
    Args:
        data: Dictionary containing AI suggestion data
    """
    logger.info(f"Pushing AI suggestion to queue: {data.get('suggestion', 'N/A')[:50]}...")
    ai_queue.put(data)


async def broadcast_ai_suggestions():
    """
    Background task that continuously reads from ai_queue
    and broadcasts to all connected WebSocket clients.
    """
    while True:
        try:
            if not ai_queue.empty():
                try:
                    result = ai_queue.get_nowait()
                except:
                    continue
                
                # Broadcast to all connected clients
                disconnected = set()
                for connection in active_connections:
                    try:
                        await connection.send_json(result)
                        logger.info(f"Sent AI suggestion to WebSocket client")
                    except Exception as e:
                        logger.error(f"Error sending to WebSocket: {e}")
                        disconnected.add(connection)
                
                # Remove disconnected clients
                for conn in disconnected:
                    active_connections.remove(conn)
            
            # Small delay to prevent CPU spinning
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in broadcast task: {e}")
            await asyncio.sleep(1)


async def websocket_manager(websocket: WebSocket):
    """
    Handle individual WebSocket connection lifecycle.
    
    Args:
        websocket: The WebSocket connection
    """
    await websocket.accept()
    active_connections.add(websocket)
    logger.info(f"WebSocket connected. Total connections: {len(active_connections)}")
    
    try:
        # Keep connection alive
        while True:
            # Receive any messages (for heartbeat/ping)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                # Echo back for heartbeat
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                # Send keepalive
                try:
                    await websocket.send_json({"type": "keepalive"})
                except:
                    break
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        logger.info(f"WebSocket removed. Total connections: {len(active_connections)}")
