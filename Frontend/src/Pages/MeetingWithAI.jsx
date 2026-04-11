import React, { useState } from 'react';
import { useAIWebSocket } from '../hooks/useAIWebSocket';
import AISuggestionPopup from '../components/AISuggestionPopup';

const API_BASE = import.meta.env.VITE_API_URL;

const MeetingWithAI = () => {
    const { aiSuggestion, isConnected, error } = useAIWebSocket();
    const [transcript, setTranscript] = useState('');
    const [meetingId] = useState('demo_meeting_' + Date.now());

    const handleSendTranscript = async () => {
        if (!transcript.trim()) return;

        try {
            const response = await fetch(`${API_BASE}/process-transcript`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    transcript: transcript,
                    meeting_id: meetingId,
                    speaker: 'Client',
                    use_rag: true,
                    top_k: 3
                })
            });

            if (response.ok) {
                console.log('Transcript processed successfully');
                setTranscript(''); // Clear input
            }
        } catch (err) {
            console.error('Error processing transcript:', err);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-indigo-900 p-8">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-6 mb-6">
                    <h1 className="text-4xl font-bold text-white mb-2">
                        AI Meeting Co-Pilot Demo
                    </h1>
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
                            <span className="text-white text-sm">
                                {isConnected ? 'AI Connected' : 'Disconnected'}
                            </span>
                        </div>
                        <span className="text-gray-300 text-sm">Meeting ID: {meetingId}</span>
                    </div>
                </div>

                {/* Transcript Input */}
                <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-6">
                    <h2 className="text-2xl font-semibold text-white mb-4">
                        Simulated Client Speech
                    </h2>
                    <textarea
                        value={transcript}
                        onChange={(e) => setTranscript(e.target.value)}
                        placeholder="Type what the client said... (e.g., 'I'm interested in your pricing plans')"
                        className="w-full h-32 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-xl p-4 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <button
                        onClick={handleSendTranscript}
                        disabled={!transcript.trim() || !isConnected}
                        className="mt-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold px-6 py-3 rounded-xl transition-all"
                    >
                        Process Transcript & Get AI Suggestion
                    </button>
                </div>

                {/* Example Transcripts */}
                <div className="mt-6 bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Try These Examples:</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <button
                            onClick={() => setTranscript("I'm interested in your pricing plans and discounts.")}
                            className="bg-purple-600 hover:bg-purple-700 text-white p-4 rounded-xl text-left transition-all"
                        >
                            <p className="font-semibold mb-1">💰 Pricing Question</p>
                            <p className="text-sm opacity-90">Ask about pricing plans</p>
                        </button>
                        <button
                            onClick={() => setTranscript("Wait, I'm confused about the contract terms. Can you explain again?")}
                            className="bg-red-600 hover:bg-red-700 text-white p-4 rounded-xl text-left transition-all"
                        >
                            <p className="font-semibold mb-1">⚠️ Confusion</p>
                            <p className="text-sm opacity-90">Trigger confusion detection</p>
                        </button>
                        <button
                            onClick={() => setTranscript("This sounds great! Can you send me a detailed proposal?")}
                            className="bg-green-600 hover:bg-green-700 text-white p-4 rounded-xl text-left transition-all"
                        >
                            <p className="font-semibold mb-1">✅ Task Creation</p>
                            <p className="text-sm opacity-90">Generate action items</p>
                        </button>
                        <button
                            onClick={() => setTranscript("What integrations do you support?")}
                            className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-xl text-left transition-all"
                        >
                            <p className="font-semibold mb-1">🔌 Technical Question</p>
                            <p className="text-sm opacity-90">Ask about features</p>
                        </button>
                    </div>
                </div>

                {/* Error Display */}
                {error && (
                    <div className="mt-6 bg-red-500 bg-opacity-20 border border-red-400 rounded-xl p-4">
                        <p className="text-white">Error: {error}</p>
                    </div>
                )}
            </div>

            {/* AI Suggestion Popup */}
            <AISuggestionPopup
                suggestion={aiSuggestion}
                onClose={() => { }}
            />
        </div>
    );
};

export default MeetingWithAI;
