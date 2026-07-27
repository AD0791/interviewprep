// Use Case: Custom Hook for Live WebSocket Metrics Consumer
// Purpose: Establishes connections, handles frame decoding, and cleans up sockets on unmount.
// Key features: WebSocket initialization, state sync, and hook cleanups.

import { useEffect, useState } from 'react';

interface LiveTelemetry {
  tenant_id: number;
  current_throughput: number;
  active_users: number;
}

export const useWebSocketMetrics = (tenantId: number) => {
  const [telemetry, setTelemetry] = useState<LiveTelemetry | null>(null);
  const [status, setStatus] = useState<'connecting' | 'open' | 'closed'>('connecting');

  useEffect(() => {
    const wsUrl = `ws://localhost:8000/ws/metrics/${tenantId}`;
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      setStatus('open');
    };

    socket.onmessage = (event) => {
      try {
        const data: LiveTelemetry = JSON.parse(event.data);
        setTelemetry(data);
      } catch (err) {
        console.error('Failed parsing live message payload', err);
      }
    };

    socket.onclose = () => {
      setStatus('closed');
    };

    socket.onerror = (error) => {
      console.error('WebSocket encountered an error:', error);
    };

    // Cleanup: close connection when component unmounts
    // Why: Prevents memory leaks and orphaned connections in the background
    return () => {
      socket.close();
    };
  }, [tenantId]);

  return { telemetry, status };
};
