# Use Case: Real-time Telemetry Push Server (WebSockets)
# Purpose: Pushes low-latency JSON telemetry payloads dynamically.
# Key features: WebSocket connection manager, broadcast, and exception safety.

import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_json(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Connection might be dead, handled silently here
                pass

manager = ConnectionManager()

@app.websocket("/ws/metrics/{tenant_id}")
async def websocket_metrics_endpoint(websocket: WebSocket, tenant_id: int):
    await manager.connect(websocket)
    try:
        while True:
            # Simulate real-time metric polling from Redis or DB
            mock_metrics = {
                "tenant_id": tenant_id,
                "current_throughput": 45.2,
                "active_users": 184
            }
            await websocket.send_json(mock_metrics)
            # Sleep 2 seconds before pushing next update
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
