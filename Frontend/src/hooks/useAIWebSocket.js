import { useEffect, useState } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_URL = API_BASE.replace(/^http/, 'ws') + '/ws/ai';

export const useAIWebSocket = (url = WS_URL) => {
    const [aiSuggestion, setAiSuggestion] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const ws = new WebSocket(url);

        ws.onopen = () => {
            console.log('Connected to AI WebSocket');
            setIsConnected(true);
            setError(null);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                // Ignore keepalive messages
                if (data.type === 'keepalive') {
                    return;
                }

                console.log('Received AI suggestion:', data);
                setAiSuggestion(data);
            } catch (err) {
                console.error('Error parsing WebSocket message:', err);
            }
        };

        ws.onerror = (event) => {
            console.error('WebSocket error:', event);
            setError('WebSocket connection error');
            setIsConnected(false);
        };

        ws.onclose = () => {
            console.log('Disconnected from AI WebSocket');
            setIsConnected(false);
        };

        // Heartbeat to keep connection alive
        const heartbeatInterval = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send('ping');
            }
        }, 25000);

        // Cleanup
        return () => {
            clearInterval(heartbeatInterval);
            ws.close();
        };
    }, [url]);

    return { aiSuggestion, isConnected, error };
};
