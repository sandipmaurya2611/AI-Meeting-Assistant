import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_URL;

const JoinMeeting = () => {
    const { roomName } = useParams();
    const navigate = useNavigate();
    const [meeting, setMeeting] = useState(null);
    const [username, setUsername] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Fetch meeting details
        const fetchMeeting = async () => {
            try {
                const response = await fetch(`${API_BASE}/api/meetings/room/${roomName}`);
                if (response.ok) {
                    const data = await response.json();
                    setMeeting(data);
                } else {
                    setError('Meeting not found');
                }
            } catch (err) {
                setError('Failed to load meeting');
            } finally {
                setLoading(false);
            }
        };

        if (roomName) {
            fetchMeeting();
        }
    }, [roomName]);

    const handleJoin = () => {
        if (!username.trim()) {
            alert('Please enter your name');
            return;
        }

        // Navigate to meeting interface with username and room
        navigate(`/meeting?room=${roomName}&username=${encodeURIComponent(username)}`);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
                <div className="text-white text-2xl">Loading...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center p-6">
                <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-3xl p-8 max-w-md w-full text-center">
                    <div className="text-6xl mb-4">❌</div>
                    <h1 className="text-3xl font-bold text-white mb-2">Meeting Not Found</h1>
                    <p className="text-gray-300 mb-6">{error}</p>
                    <button
                        onClick={() => navigate('/')}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-xl font-semibold transition-all"
                    >
                        Go Home
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center p-6">
            <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-3xl p-8 max-w-lg w-full">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="text-6xl mb-4">🎥</div>
                    <h1 className="text-4xl font-bold text-white mb-2">Join Meeting</h1>
                    <p className="text-gray-300 text-lg">{meeting?.title}</p>
                </div>

                {/* Meeting Info */}
                <div className="bg-white bg-opacity-10 rounded-2xl p-6 mb-6">
                    <div className="space-y-3">
                        <div className="flex items-center gap-3">
                            <span className="text-2xl">📋</span>
                            <div>
                                <p className="text-gray-400 text-sm">Room Name</p>
                                <p className="text-white font-semibold">{meeting?.room_name}</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <span className="text-2xl">🔗</span>
                            <div className="flex-1">
                                <p className="text-gray-400 text-sm">Meeting Link</p>
                                <p className="text-white text-sm break-all">{meeting?.meeting_url}</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Join Form */}
                <div className="space-y-4">
                    <div>
                        <label className="block text-white font-semibold mb-2">
                            Your Name
                        </label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Enter your name..."
                            className="w-full bg-white bg-opacity-10 border border-white border-opacity-20 rounded-xl px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            onKeyPress={(e) => e.key === 'Enter' && handleJoin()}
                        />
                    </div>

                    <button
                        onClick={handleJoin}
                        className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white py-4 rounded-xl font-bold text-lg transition-all transform hover:scale-105 shadow-lg"
                    >
                        Join Meeting
                    </button>
                </div>

                {/* Info */}
                <div className="mt-6 text-center text-gray-400 text-sm">
                    <p>✓ HD Video & Audio</p>
                    <p>✓ Real-time AI Transcription</p>
                    <p>✓ AI Meeting Co-Pilot</p>
                </div>
            </div>
        </div>
    );
};

export default JoinMeeting;
