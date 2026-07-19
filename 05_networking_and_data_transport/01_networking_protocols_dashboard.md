# Networking Protocols & Transport Optimization Masterclass

A deep-dive academic guide to client-server communication models (Short Polling, Long Polling, SSE, WebSockets), CORS preflight headers caching, and response payload compression.

---

## 1. Real-Time Transport Protocols (Why & What)

Dashboards require real-time updates. System designers must choose the appropriate transport protocol based on connection state requirements, latency limits, and server resource constraints.

### Short Polling
* **What**: The client sends regular HTTP requests at fixed intervals (e.g. every 5 seconds) to fetch updates.
* **Why (Pros)**: Extremely simple to implement, stateless, works natively with standard HTTP caching.
* **Why (Cons)**: High overhead due to repeated TCP/TLS connection handshakes, saturating server gateways even when no new data exists.

### Long Polling
* **What**: The client sends an HTTP request, and the server holds the connection open until new data is available. Once resolved, the client immediately opens a new connection.
* **Why (Pros)**: Lower latency than short polling, fallback compatibility for legacy proxy systems.
* **Why (Cons)**: Holds socket resources open on the server, leading to connection depletion issues under scale.

### Server-Sent Events (SSE)
* **What**: A unidirectional persistent connection where the server pushes updates to the client over standard HTTP.
* **Why (Pros)**: Runs over HTTP/2 (supporting multiplexing), handles automatic reconnections, has low protocol overhead, and is simple to scale behind standard reverse proxies.
* **Why (Cons)**: Unidirectional only (cannot send data from client to server over the same socket).

### WebSockets
* **What**: A full-duplex, bidirectional communication protocol running over a single TCP connection.
* **Why (Pros)**: Lowest latency, bidirectional messaging support.
* **Why (Cons)**: State-heavy connections make horizontal scaling and load balancing behind reverse proxies more complex (requires sticky sessions or Redis Pub/Sub backplanes).

```mermaid
graph TD
    subgraph Polling ["Short Polling"]
        C1[Client] -->|HTTP GET| S1[Server]
        S1 -->|Response: No data| C1
        C1 -->|Sleep 5s -> HTTP GET| S1
        S1 -->|Response: Data| C1
    end

    subgraph SSE ["Server-Sent Events"]
        C2[Client] -->|HTTP Connect Stream| S2[Server]
        S2 -->|Data Push 1| C2
        S2 -->|Data Push 2| C2
        Note over S2,C2: Persistent Unidirectional HTTP
    end

    subgraph WS ["WebSockets"]
        C3[Client] -->|Connection Upgrade request| S3[Server]
        C3 <-->|Bidirectional Data Frame transfer| S3
        Note over S3,C3: Bidirectional TCP Socket
    end
```

---

## 2. Advanced Networking Optimizations (Why & How)

### CORS Preflight Caching
Browsers protect users from cross-site scripts by executing preflight `OPTIONS` queries before writing cross-origin requests.
* **The Performance Issue**: If every dashboard action triggers a preflight request, the application incurs double the network roundtrips.
* **The Solution**: Instruct the browser to cache preflight responses locally using the `Access-Control-Max-Age` header.

### Compression Stack
* **Brotli / Gzip**: Compress JSON payloads before transmission. Compressing large metric arrays reduces transfer times significantly, decreasing first render times on the frontend.

---

## 3. Implementation Blueprints (How)

### Gist: websocket_metrics_server.py
A complete FastAPI WebSocket server broadcasting metrics to active connections.

```python
# Gist: websocket_metrics_server.py
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

class WebSocketConnectionManager:
    def __init__(self):
        # Track active socket connections
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # Push message frame to all active connections
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Handle connection drops silently
                pass

manager = WebSocketConnectionManager()

@app.websocket("/ws/telemetry/{tenant_id}")
async def telemetry_websocket(websocket: WebSocket, tenant_id: int):
    await manager.connect(websocket)
    try:
        while True:
            # Simulate real-time database polling
            telemetry_payload = {
                "tenant_id": tenant_id,
                "current_throughput": 87.5,
                "active_connections": 1400
            }
            await websocket.send_json(telemetry_payload)
            await asyncio.sleep(1)  # Stream updates once per second
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### Gist: use_websocket_metrics.ts
A React custom hook that consumes a WebSocket endpoint, updating local state and handling cleanup on unmount.

```typescript
// Gist: use_websocket_metrics.ts
import { useEffect, useState } from 'react';

interface TelemetryFrame {
  tenant_id: number;
  current_throughput: number;
  active_connections: number;
}

export const useWebSocketTelemetry = (tenantId: number) => {
  const [data, setData] = useState<TelemetryFrame | null>(null);
  const [connected, setConnected] = useState<boolean>(false);

  useEffect(() => {
    const wsUrl = `ws://localhost:8000/ws/telemetry/${tenantId}`;
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      setConnected(true);
    };

    socket.onmessage = (event) => {
      try {
        const payload: TelemetryFrame = JSON.parse(event.data);
        setData(payload);
      } catch (err) {
        console.error('WebSocket frame parsing failed:', err);
      }
    };

    socket.onclose = () => {
      setConnected(false);
    };

    // Cleanup: close connection when component unmounts
    // Why: Prevents memory leaks and orphaned connections in the background
    return () => {
      socket.close();
    };
  }, [tenantId]);

  return { data, connected };
};
```
