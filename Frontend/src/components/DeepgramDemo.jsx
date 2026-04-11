import React, { useState, useRef, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
// Ensure we use ws:// or wss://
const WS_URL = API_BASE.replace(/^http/, 'ws') + '/ws-transcript';

export default function DeepgramDemo() {
    const [isRecording, setIsRecording] = useState(false);
    const [transcript, setTranscript] = useState([]);
    const socketRef = useRef(null);
    const mediaRecorderRef = useRef(null);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // Connect to WebSocket
            // You can append ?meeting_id=... to save to DB
            socketRef.current = new WebSocket(WS_URL);

            socketRef.current.onopen = () => {
                console.log('WebSocket Connected');
                setIsRecording(true);
                startAudioProcessing(stream);
            };

            socketRef.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'transcript') {
                        setTranscript(prev => {
                            // If the last item is not final, replace it. Otherwise add new.
                            const last = prev[prev.length - 1];
                            if (last && !last.is_final) {
                                return [...prev.slice(0, -1), data];
                            }
                            return [...prev, data];
                        });
                    }
                } catch (e) {
                    console.error("Error parsing message", e);
                }
            };

            socketRef.current.onerror = (error) => {
                console.error('WebSocket Error:', error);
            };

            socketRef.current.onclose = () => {
                console.log('WebSocket Closed');
                setIsRecording(false);
            };

        } catch (err) {
            console.error('Error accessing microphone:', err);
        }
    };

    const startAudioProcessing = (stream) => {
        // Create AudioContext with 16k sample rate to match backend config
        const audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
        const source = audioContext.createMediaStreamSource(stream);
        // Buffer size 4096, 1 input channel, 1 output channel
        const processor = audioContext.createScriptProcessor(4096, 1, 1);

        source.connect(processor);
        processor.connect(audioContext.destination);

        processor.onaudioprocess = (e) => {
            if (socketRef.current?.readyState === WebSocket.OPEN) {
                const inputData = e.inputBuffer.getChannelData(0);
                // Convert float32 audio to 16-bit PCM
                const pcmData = floatTo16BitPCM(inputData);
                socketRef.current.send(pcmData);
            }
        };

        mediaRecorderRef.current = {
            stop: () => {
                source.disconnect();
                processor.disconnect();
                audioContext.close();
                stream.getTracks().forEach(track => track.stop());
            }
        };
    };

    const floatTo16BitPCM = (input) => {
        const output = new Int16Array(input.length);
        for (let i = 0; i < input.length; i++) {
            const s = Math.max(-1, Math.min(1, input[i]));
            // Convert to 16-bit integer
            output[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        return output.buffer;
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
        }
        if (socketRef.current) {
            socketRef.current.close();
        }
        setIsRecording(false);
    };

    return (
        <div className="p-6 bg-slate-900 text-white rounded-xl shadow-lg border border-slate-800 max-w-2xl mx-auto mt-10">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold flex items-center gap-2">
                    <span className="text-blue-500">🎙️</span> Real-time Transcription
                </h2>
                <div className="flex gap-2">
                    {!isRecording ? (
                        <button
                            onClick={startRecording}
                            className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-full font-semibold transition-colors shadow-lg shadow-blue-900/20"
                        >
                            Start Recording
                        </button>
                    ) : (
                        <button
                            onClick={stopRecording}
                            className="bg-red-600 hover:bg-red-700 px-6 py-2 rounded-full font-semibold transition-colors shadow-lg shadow-red-900/20 animate-pulse"
                        >
                            Stop Recording
                        </button>
                    )}
                </div>
            </div>

            <div className="h-96 overflow-y-auto bg-slate-950 p-4 rounded-lg border border-slate-800 font-mono text-sm leading-relaxed scroll-smooth">
                {transcript.length === 0 && (
                    <div className="text-slate-600 text-center mt-32 italic">
                        Start recording to see transcript...
                    </div>
                )}
                {transcript.map((t, i) => (
                    <span key={i} className={`${t.is_final ? 'text-slate-200' : 'text-blue-400'} transition-colors duration-300`}>
                        {t.text}
                    </span>
                ))}
            </div>

            <div className="mt-4 text-xs text-slate-500 text-center">
                Powered by Deepgram Streaming API
            </div>
        </div>
    );
}
