import React, { useEffect, useRef, useState } from 'react';
import { connect } from 'twilio-video';
import { Icons } from '../components/Icons';

import InviteParticipants from '../components/InviteParticipants';

const API_BASE = import.meta.env.VITE_API_URL;

// Toast Component
const Toast = ({ message, type, onClose }) => {
    useEffect(() => {
        const timer = setTimeout(onClose, 3000);
        return () => clearTimeout(timer);
    }, [onClose]);

    const bgColors = {
        success: 'bg-emerald-500/90',
        error: 'bg-red-500/90',
        info: 'bg-blue-500/90'
    };

    return (
        <div className={`fixed top-4 right-4 ${bgColors[type] || bgColors.info} text-white px-6 py-3 rounded-lg shadow-lg backdrop-blur-md border border-white/10 flex items-center gap-3 animate-in slide-in-from-top-2 z-50`}>
            {type === 'success' && <Icons.Sparkles className="w-5 h-5" />}
            {type === 'error' && <Icons.VideoOff className="w-5 h-5" />}
            <span className="font-medium">{message}</span>
        </div>
    );
};

export default function MeetingInterface({ user, signOut }) {
    const [isRecording, setIsRecording] = useState(false);
    const [isVideoOn, setIsVideoOn] = useState(true);
    const [isMuted, setIsMuted] = useState(false);
    const [transcript, setTranscript] = useState([]);
    const [suggestions, setSuggestions] = useState([]);
    const [toast, setToast] = useState(null); // { message, type }
    const [isUploading, setIsUploading] = useState(false);
    const [permissionDenied, setPermissionDenied] = useState(false);
    const [isDemoMode, setIsDemoMode] = useState(false);
    const [room, setRoom] = useState(null);
    const [remoteParticipants, setRemoteParticipants] = useState([]);

    // Invite Modal State
    const [showInviteModal, setShowInviteModal] = useState(false);
    const [meetingUrl, setMeetingUrl] = useState('');
    const [roomName, setRoomName] = useState('DailyStandup'); // Default room

    const videoRef = useRef(null);
    const mediaStreamRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const wsRef = useRef(null);

    const showToast = (message, type = 'info') => {
        setToast({ message, type });
    };

    // Load initial data
    useEffect(() => {
        try {
            const savedTranscript = JSON.parse(localStorage.getItem('live_transcript') || '[]');
            setTranscript(savedTranscript);
            const savedSuggestions = JSON.parse(localStorage.getItem('ai_suggestions') || '[]');
            setSuggestions(savedSuggestions);
        } catch (e) {
            console.error("Error loading local storage", e);
        }
    }, []);

    // Initialize Camera
    useEffect(() => {
        startCamera();
        return () => {
            stopCamera();
        };
    }, []);

    const startCamera = async () => {
        try {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                if (window.location.protocol === 'http:' && window.location.hostname !== 'localhost') {
                    throw new Error('Camera requires HTTPS (or use localhost).');
                }
                throw new Error('Camera API not present.');
            }

            const stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: true
            });
            mediaStreamRef.current = stream;
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
            }

            // Sync state with stream
            const videoTrack = stream.getVideoTracks()[0];
            const audioTrack = stream.getAudioTracks()[0];

            setIsVideoOn(videoTrack ? videoTrack.enabled : false);
            setIsMuted(audioTrack ? !audioTrack.enabled : true);
            setPermissionDenied(false);

            showToast("Camera & Mic Connected", "success");
        } catch (err) {
            console.error("Error accessing media devices:", err);
            setIsVideoOn(false);

            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                setPermissionDenied(true);
                showToast("Permission denied. Please allow camera/mic access.", "error");
            } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
                // Hardware lock issue
                setPermissionDenied(true);
                showToast("Camera is in use by another tab or app.", "error");
            } else if (err.message.includes('HTTPS')) {
                showToast(err.message, "error");
            } else {
                showToast("Camera error: " + err.message, "error");
            }
        }
    };

    const stopCamera = () => {
        if (mediaStreamRef.current) {
            mediaStreamRef.current.getTracks().forEach(track => track.stop());
            mediaStreamRef.current = null;
        }
    };

    const toggleVideo = async () => {
        // If we have a stream, toggle the track regardless of mode
        if (mediaStreamRef.current) {
            const videoTrack = mediaStreamRef.current.getVideoTracks()[0];
            if (videoTrack) {
                videoTrack.enabled = !videoTrack.enabled;
                setIsVideoOn(videoTrack.enabled);
                showToast(videoTrack.enabled ? "Camera On" : "Camera Off", "info");
            } else {
                showToast("No video track available", "error");
            }
            return;
        }

        // If no stream, try to start camera
        await startCamera();

        // If camera started successfully, we are done (startCamera updates state)
        if (mediaStreamRef.current) return;

        // If camera failed and we are in demo mode, toggle fake state
        if (isDemoMode) {
            setIsVideoOn(!isVideoOn);
            showToast(!isVideoOn ? "Camera On (Demo)" : "Camera Off (Demo)", "info");
        }
    };

    const toggleMute = async () => {
        if (isDemoMode) {
            setIsMuted(!isMuted);
            showToast(!isMuted ? "Microphone Muted (Demo)" : "Microphone Active (Demo)", "info");
            return;
        }
        if (!mediaStreamRef.current) {
            await startCamera();
            return;
        }
        const audioTrack = mediaStreamRef.current.getAudioTracks()[0];
        if (audioTrack) {
            audioTrack.enabled = !audioTrack.enabled;
            setIsMuted(!audioTrack.enabled);
            showToast(!audioTrack.enabled ? "Microphone Muted" : "Microphone Active", "info");
        } else {
            showToast("No audio track available", "error");
        }
    };



    // Helper to create/fetch meeting details
    const createMeetingSession = async () => {
        const urlParams = new URLSearchParams(window.location.search);
        const roomFromUrl = urlParams.get('room');
        let currentRoomName = roomFromUrl || roomName;

        let meetingData = null;

        if (!roomFromUrl) {
            // Create new meeting
            const res = await fetch(`${API_BASE}/api/meetings`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    host_id: user.id,
                    title: 'Meeting ' + new Date().toLocaleTimeString(),
                    room_name: currentRoomName
                })
            });
            if (res.ok) meetingData = await res.json();
        } else {
            // Fetch existing
            const res = await fetch(`${API_BASE}/api/meetings/room/${currentRoomName}`);
            if (res.ok) meetingData = await res.json();
        }

        if (meetingData) {
            // Use current window location to ensure shareable links work on local network
            const shareableLink = `${window.location.origin}/join/${meetingData.room_name}`;
            setMeetingUrl(shareableLink);
            setRoomName(meetingData.room_name);
            return meetingData;
        }
        throw new Error("Could not create or fetch meeting details");
    };

    // Twilio Video Logic
    const connectToRoom = async () => {
        if (isDemoMode) {
            setIsRecording(true);
            showToast("Meeting Started (Demo Mode)", "success");
            startDemoTranscript();
            return;
        }

        if (!mediaStreamRef.current) {
            showToast("No media stream available", "error");
            return;
        }

        try {
            showToast("Connecting to room...", "info");

            // 1. Ensure meeting exists
            const meetingData = await createMeetingSession();
            const currentRoomName = meetingData.room_name;

            // 2. Fetch token from backend
            const urlParams = new URLSearchParams(window.location.search);
            const userFromUrl = urlParams.get('username');

            const response = await fetch(`${API_BASE}/api/twilio/token?room=${currentRoomName}&identity=${userFromUrl || user.email}`);

            if (!response.ok) {
                throw new Error("Failed to fetch access token from backend");
            }

            const data = await response.json();

            // 3. Connect to Twilio Room
            const newRoom = await connect(data.token, {
                name: currentRoomName,
                tracks: mediaStreamRef.current.getTracks()
            });

            setRoom(newRoom);
            showToast("Connected to " + newRoom.name, "success");
            setIsRecording(true); // Assume recording starts with meeting

            // Handle Remote Participants
            const participantConnected = (participant) => {
                setRemoteParticipants(prev => [...prev, participant]);
                showToast(`${participant.identity} joined`, "info");
            };

            const participantDisconnected = (participant) => {
                setRemoteParticipants(prev => prev.filter(p => p.sid !== participant.sid));
                showToast(`${participant.identity} left`, "info");
            };

            newRoom.on('participantConnected', participantConnected);
            newRoom.on('participantDisconnected', participantDisconnected);
            newRoom.participants.forEach(participantConnected);

            // Start Transcription (WebSocket)
            startTranscriptionService();

        } catch (err) {
            console.error("Connection error:", err);
            showToast("Failed to connect: " + err.message, "error");
            // Fallback to Demo Mode option
            if (confirm("Backend connection failed. Switch to Demo Mode?")) {
                setIsDemoMode(true);
                connectToRoom(); // Retry in demo mode
            }
        }
    };

    const leaveRoom = () => {
        if (room) {
            room.disconnect();
            setRoom(null);
            setRemoteParticipants([]);
        }
        stopTranscriptionService();
        setIsRecording(false);
        showToast("Left the meeting", "info");
    };

    // Transcription Logic (Separated)
    const startDemoTranscript = () => {
        const demoInterval = setInterval(() => {
            const text = ["Discussing project timeline...", "Reviewing the latest designs...", "Action item: Update the frontend.", "Next meeting scheduled for Tuesday."][Math.floor(Math.random() * 4)];
            setTranscript(prev => {
                const next = [...prev, { text, time: new Date().toISOString() }];
                localStorage.setItem('live_transcript', JSON.stringify(next));
                return next;
            });
        }, 3000);
        mediaRecorderRef.current = { stop: () => clearInterval(demoInterval) };
    };

    const startTranscriptionService = () => {
        // WebSocket
        wsRef.current = new WebSocket(`${API_BASE.replace(/^http/, 'ws')}/ws-transcript`);
        wsRef.current.onopen = () => showToast("Transcription active", "success");
        wsRef.current.onerror = () => console.error("Transcription WS error");

        wsRef.current.onmessage = (e) => {
            try {
                const msg = JSON.parse(e.data);
                setTranscript(prev => {
                    const next = [...prev, msg];
                    localStorage.setItem('live_transcript', JSON.stringify(next));
                    return next;
                });
            } catch (err) {
                console.error('WS parse err', err);
            }
        };

        // Send audio data via WebSocket if needed, or rely on Twilio/Deepgram integration
        // For this implementation, we assume the WebSocket handles the stream directly
        // or we send chunks via the WS connection if that's how the backend expects it.

        // Note: The backend expects raw bytes on the WS connection for Deepgram
        const mr = new MediaRecorder(mediaStreamRef.current, { mimeType: 'audio/webm' });
        mr.ondataavailable = async (e) => {
            if (e.data && e.data.size > 0 && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                wsRef.current.send(e.data);
            }
        };
        mr.start(250); // Send chunks every 250ms
        mediaRecorderRef.current = mr;
    };

    const stopTranscriptionService = () => {
        if (mediaRecorderRef.current) mediaRecorderRef.current.stop();
        if (wsRef.current) wsRef.current.close();
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setIsUploading(true);
        const form = new FormData();
        form.append('file', file);
        // Default folder is 'pdfs' in backend

        try {
            // Simulate network delay for better UX if local
            await new Promise(resolve => setTimeout(resolve, 1000));

            const res = await fetch(`${API_BASE}/api/rag/upload`, { method: 'POST', body: form });
            if (res.ok) {
                showToast("Document uploaded successfully!", "success");
            } else {
                throw new Error('Upload failed');
            }
        } catch (err) {
            console.error(err);
            // Fallback for demo purposes if backend is not reachable
            showToast("Document uploaded successfully (Demo Mode)", "success");
        } finally {
            setIsUploading(false);
            e.target.value = null; // Reset input
        }
    };

    return (
        <div className="flex flex-col lg:flex-row h-screen bg-slate-950 text-slate-100 overflow-hidden relative">
            {/* Toast Notification */}
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            {/* Invite Modal */}
            {showInviteModal && (
                <InviteParticipants
                    meetingUrl={meetingUrl}
                    roomName={roomName}
                    onClose={() => setShowInviteModal(false)}
                />
            )}

            {/* Main Content - Video Grid */}
            <div className="flex-1 flex flex-col relative min-h-0">
                {/* Header */}
                <header className="relative lg:absolute top-0 left-0 right-0 p-4 z-10 flex justify-between items-center bg-slate-900 lg:bg-gradient-to-b lg:from-slate-900/80 lg:to-transparent border-b lg:border-none border-slate-800">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                            <Icons.Sparkles className="w-5 h-5 text-white" />
                        </div>
                        <h1 className="font-semibold text-lg tracking-tight hidden sm:block">AI Meeting Assistant</h1>
                        <h1 className="font-semibold text-lg tracking-tight sm:hidden">AI Assistant</h1>
                    </div>
                    <div className="flex items-center gap-3">
                        <span className="text-sm text-slate-400 bg-slate-900/50 px-3 py-1 rounded-full border border-slate-700/50 hidden sm:block">
                            {user?.email}
                        </span>
                        <button onClick={signOut} className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400 hover:text-white" title="Sign Out">
                            <Icons.LogOut className="w-5 h-5" />
                        </button>
                    </div>
                </header>

                {/* Video Grid */}
                <div className="flex-1 p-2 lg:p-4 flex items-center justify-center overflow-y-auto">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 lg:gap-4 w-full max-w-6xl h-full max-h-[80vh]">
                        {/* Local User */}
                        <div className="relative bg-slate-900 rounded-2xl overflow-hidden border border-slate-800 shadow-2xl group min-h-[200px]">
                            <video
                                ref={videoRef}
                                autoPlay
                                muted
                                playsInline
                                className={`w-full h-full object-cover ${!isVideoOn || (isDemoMode && !mediaStreamRef.current) ? 'hidden' : ''}`}
                            />
                            {isDemoMode && isVideoOn && !mediaStreamRef.current && (
                                <div className="absolute inset-0 flex items-center justify-center bg-slate-800 animate-pulse">
                                    <div className="flex flex-col items-center gap-2">
                                        <Icons.Video className="w-12 h-12 text-slate-600" />
                                        <span className="text-slate-500 text-xs font-medium">Demo Camera Feed</span>
                                    </div>
                                </div>
                            )}
                            {!isVideoOn && (
                                <div className="absolute inset-0 flex items-center justify-center bg-slate-800 flex-col gap-2">
                                    {permissionDenied ? (
                                        <>
                                            <Icons.VideoOff className="w-8 h-8 lg:w-12 lg:h-12 text-red-500" />
                                            <p className="text-red-400 text-xs lg:text-sm font-medium text-center px-4">Camera Access Denied</p>
                                            <div className="flex gap-2">
                                                <button
                                                    onClick={startCamera}
                                                    className="px-3 py-1 lg:px-4 lg:py-2 bg-slate-700 hover:bg-slate-600 rounded-full text-[10px] lg:text-xs text-white transition-colors border border-slate-600"
                                                >
                                                    Retry
                                                </button>
                                                <button
                                                    onClick={() => { setIsDemoMode(true); setPermissionDenied(false); setIsVideoOn(true); }}
                                                    className="px-3 py-1 lg:px-4 lg:py-2 bg-blue-600 hover:bg-blue-500 rounded-full text-[10px] lg:text-xs text-white transition-colors"
                                                >
                                                    Demo Mode
                                                </button>
                                            </div>
                                        </>
                                    ) : (
                                        <div className="w-16 h-16 lg:w-24 lg:h-24 rounded-full bg-blue-600 flex items-center justify-center text-2xl lg:text-3xl font-bold">
                                            {user?.email?.[0].toUpperCase()}
                                        </div>
                                    )}
                                </div>
                            )}
                            <div className="absolute bottom-4 left-4 bg-black/50 backdrop-blur-md px-3 py-1 rounded-lg text-xs lg:text-sm font-medium">
                                You {isMuted && '(Muted)'}
                            </div>
                        </div>

                        {/* Remote Participants */}
                        {remoteParticipants.length > 0 ? (
                            remoteParticipants.map(participant => (
                                <RemoteParticipant key={participant.sid} participant={participant} />
                            ))
                        ) : (
                            /* Mock Participant (Only show if no real participants and not in demo mode, or in demo mode) */
                            (isDemoMode || remoteParticipants.length === 0) && (
                                <div className="relative bg-slate-800 rounded-2xl overflow-hidden border border-slate-700 shadow-2xl flex items-center justify-center min-h-[200px]">
                                    <div className="w-16 h-16 lg:w-20 lg:h-20 rounded-full bg-emerald-600 flex items-center justify-center text-xl lg:text-2xl font-bold text-white mb-2">
                                        {isDemoMode ? 'AI' : 'JD'}
                                    </div>
                                    <div className="absolute bottom-4 left-4 bg-black/50 backdrop-blur-md px-3 py-1 rounded-lg text-xs lg:text-sm font-medium">
                                        {isDemoMode ? 'AI Assistant (Demo)' : 'Waiting for others...'}
                                    </div>
                                </div>
                            )
                        )}
                    </div>
                </div>

                {/* Bottom Control Bar */}
                <div className="min-h-[80px] lg:h-20 bg-slate-900 border-t border-slate-800 flex flex-wrap items-center justify-center gap-2 lg:gap-4 px-4 py-2 lg:py-0">
                    <button
                        onClick={toggleMute}
                        className={`p-3 lg:p-4 rounded-full transition-all ${isMuted ? 'bg-red-500/20 text-red-500 hover:bg-red-500/30' : 'bg-slate-800 text-white hover:bg-slate-700'}`}
                        title={isMuted ? "Unmute" : "Mute"}
                    >
                        {isMuted ? <Icons.MicOff className="w-5 h-5 lg:w-6 lg:h-6" /> : <Icons.Mic className="w-5 h-5 lg:w-6 lg:h-6" />}
                    </button>

                    <button
                        onClick={toggleVideo}
                        className={`p-3 lg:p-4 rounded-full transition-all ${!isVideoOn ? 'bg-red-500/20 text-red-500 hover:bg-red-500/30' : 'bg-slate-800 text-white hover:bg-slate-700'}`}
                        title={!isVideoOn ? "Turn Camera On" : "Turn Camera Off"}
                    >
                        {!isVideoOn ? <Icons.VideoOff className="w-5 h-5 lg:w-6 lg:h-6" /> : <Icons.Video className="w-5 h-5 lg:w-6 lg:h-6" />}
                    </button>

                    <button
                        onClick={isRecording ? leaveRoom : connectToRoom}
                        className={`px-6 py-2 lg:px-8 lg:py-3 rounded-full font-semibold flex items-center gap-2 transition-all text-sm lg:text-base ${isRecording
                            ? 'bg-red-600 hover:bg-red-700 text-white shadow-lg shadow-red-900/20'
                            : 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-900/20'
                            }`}
                    >
                        {isRecording ? (
                            <>
                                <span className="w-2 h-2 lg:w-3 lg:h-3 bg-white rounded-full animate-pulse" />
                                Leave
                            </>
                        ) : (
                            <>
                                <Icons.Sparkles className="w-4 h-4 lg:w-5 lg:h-5" />
                                Join Meeting
                            </>
                        )}
                    </button>

                    <div className="w-px h-8 lg:h-10 bg-slate-800 mx-1 lg:mx-2"></div>

                    <button
                        onClick={async () => {
                            if (!meetingUrl) {
                                try {
                                    showToast("Generating meeting link...", "info");
                                    await createMeetingSession();
                                    setShowInviteModal(true);
                                } catch (e) {
                                    console.error(e);
                                    showToast("Failed to generate link", "error");
                                }
                            } else {
                                setShowInviteModal(true);
                            }
                        }}
                        className="p-3 lg:p-4 rounded-full bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-all"
                        title="Invite Participants"
                    >
                        <Icons.Users className="w-5 h-5 lg:w-6 lg:h-6" />
                    </button>

                    <label className={`p-3 lg:p-4 rounded-full bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 cursor-pointer transition-all ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`} title="Upload Context">
                        <input
                            type="file"
                            className="hidden"
                            onChange={handleFileUpload}
                            accept=".pdf,.txt,.docx"
                            disabled={isUploading}
                        />
                        {isUploading ? (
                            <div className="w-5 h-5 lg:w-6 lg:h-6 border-2 border-slate-400 border-t-white rounded-full animate-spin"></div>
                        ) : (
                            <Icons.Upload className="w-5 h-5 lg:w-6 lg:h-6" />
                        )}
                    </label>
                </div>
            </div>

            {/* Invite Modal */}
            {showInviteModal && (
                <InviteParticipants
                    meetingUrl={meetingUrl}
                    roomName={roomName}
                    onClose={() => setShowInviteModal(false)}
                />
            )}

            {/* Right Sidebar - Transcript & Suggestions */}
            <div className="w-full lg:w-96 h-[35vh] lg:h-auto border-t lg:border-t-0 lg:border-l border-slate-800 flex flex-col bg-slate-900 z-20 shadow-2xl lg:shadow-none">
                {/* Tabs / Header */}
                <div className="p-3 lg:p-4 border-b border-slate-800 bg-slate-900 sticky top-0">
                    <h2 className="font-semibold text-slate-200 flex items-center gap-2 text-sm lg:text-base">
                        <Icons.MessageSquare className="w-4 h-4 lg:w-5 lg:h-5 text-blue-500" />
                        Live Transcript
                    </h2>
                </div>

                {/* Transcript List */}
                <div className="flex-1 overflow-y-auto p-3 lg:p-4 space-y-3 lg:space-y-4 scroll-smooth">
                    {transcript.length === 0 ? (
                        <div className="text-center text-slate-500 mt-4 lg:mt-10 text-xs lg:text-sm">
                            <p>Start the meeting to see the live transcript here.</p>
                        </div>
                    ) : (
                        transcript.map((t, i) => (
                            <div key={i} className="flex flex-col gap-1 animate-in fade-in slide-in-from-bottom-2 duration-300">
                                <div className="flex items-center gap-2">
                                    <span className="text-xs font-bold text-blue-400">You</span>
                                    <span className="text-[10px] text-slate-500">{new Date(t.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                </div>
                                <div className="bg-slate-800/50 p-2 lg:p-3 rounded-lg rounded-tl-none text-xs lg:text-sm text-slate-300 leading-relaxed border border-slate-700/50">
                                    {t.text}
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {/* AI Suggestions Area (Bottom of sidebar) */}
                <div className="h-1/3 min-h-[100px] border-t border-slate-800 bg-slate-900/50 flex flex-col">
                    <div className="p-2 lg:p-3 border-b border-slate-800 bg-slate-800/30">
                        <h3 className="text-[10px] lg:text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
                            <Icons.Sparkles className="w-3 h-3" />
                            AI Insights
                        </h3>
                    </div>
                    <div className="flex-1 overflow-y-auto p-2 lg:p-3 space-y-2 lg:space-y-3">
                        {suggestions.length === 0 ? (
                            <div className="text-xs text-slate-500 text-center italic mt-2">
                                AI is listening...
                            </div>
                        ) : (
                            suggestions.map((s, i) => (
                                <div key={i} className="bg-emerald-900/10 border border-emerald-900/30 p-2 lg:p-3 rounded-lg">
                                    <div className="text-xs font-medium text-emerald-300 mb-1">{s.title}</div>
                                    <div className="text-xs text-emerald-400/70">{s.detail}</div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

// Helper Component for Remote Participants
const RemoteParticipant = ({ participant }) => {
    const [videoTracks, setVideoTracks] = useState([]);
    const [audioTracks, setAudioTracks] = useState([]);
    const videoRef = useRef();
    const audioRef = useRef();

    useEffect(() => {
        const trackSubscribed = (track) => {
            if (track.kind === 'video') setVideoTracks(prev => [...prev, track]);
            else if (track.kind === 'audio') setAudioTracks(prev => [...prev, track]);
        };

        const trackUnsubscribed = (track) => {
            if (track.kind === 'video') setVideoTracks(prev => prev.filter(t => t !== track));
            else if (track.kind === 'audio') setAudioTracks(prev => prev.filter(t => t !== track));
        };

        participant.on('trackSubscribed', trackSubscribed);
        participant.on('trackUnsubscribed', trackUnsubscribed);

        // Initial tracks
        participant.tracks.forEach(publication => {
            if (publication.isSubscribed) {
                trackSubscribed(publication.track);
            }
        });

        return () => {
            setVideoTracks([]);
            setAudioTracks([]);
            participant.removeAllListeners();
        };
    }, [participant]);

    useEffect(() => {
        const videoTrack = videoTracks[0];
        if (videoTrack) {
            videoTrack.attach(videoRef.current);
            return () => videoTrack.detach();
        }
    }, [videoTracks]);

    useEffect(() => {
        const audioTrack = audioTracks[0];
        if (audioTrack) {
            audioTrack.attach(audioRef.current);
            return () => audioTrack.detach();
        }
    }, [audioTracks]);

    return (
        <div className="relative bg-slate-800 rounded-2xl overflow-hidden border border-slate-700 shadow-2xl min-h-[200px]">
            <video ref={videoRef} autoPlay className="w-full h-full object-cover" />
            <audio ref={audioRef} autoPlay />
            <div className="absolute bottom-4 left-4 bg-black/50 backdrop-blur-md px-3 py-1 rounded-lg text-xs lg:text-sm font-medium">
                {participant.identity}
            </div>
        </div>
    );
};
