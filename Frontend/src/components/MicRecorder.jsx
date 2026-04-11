import { useRef, useState } from 'react';

const API_BASE = import.meta.env.VITE_API_URL;

export default function MicRecorder() {
	const [isRecording, setIsRecording] = useState(false);
	const [transcript, setTranscript] = useState(() => {
		try {
			return JSON.parse(localStorage.getItem('live_transcript') || '[]');
		} catch {
			return [];
		}
	});
	const mediaRef = useRef(null);
	const wsRef = useRef(null);

	// WebSocket logic (stub, can be expanded)
	const startWS = () => {
		wsRef.current = new window.WebSocket(`${API_BASE.replace(/^http/, 'ws')}/ws-transcript`);
		wsRef.current.onmessage = (e) => {
			try {
				const msg = JSON.parse(e.data);
				setTranscript((prev) => {
					const next = [...prev, msg];
					localStorage.setItem('live_transcript', JSON.stringify(next));
					return next;
				});
			} catch (err) {
				console.error('WS parse err', err);
			}
		};
		wsRef.current.onclose = () => console.log('WS closed');
		wsRef.current.onerror = (e) => console.error('WS err', e);
	};

	const sendChunk = async (blob, meetingId = 'demo') => {
		const form = new FormData();
		form.append('audio', blob, 'chunk.webm');
		form.append('meeting_id', meetingId);
		try {
			await fetch(`${API_BASE}/upload-audio-chunk`, { method: 'POST', body: form });
		} catch (err) {
			console.error('chunk send err', err);
		}
	};

	const startRecording = async () => {
		try {
			const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
			mediaRef.current = stream;
			const mr = new MediaRecorder(stream, { mimeType: 'audio/webm' });
			mr.ondataavailable = (e) => {
				if (e.data && e.data.size > 0) sendChunk(e.data);
			};
			mr.start(2000);
			startWS();
			setIsRecording(true);
			mediaRef.current.recorder = mr;
		} catch (err) {
			console.error('Mic error', err);
			alert('Please allow microphone permission');
		}
	};

	const stopRecording = () => {
		if (mediaRef.current?.recorder) mediaRef.current.recorder.stop();
		if (mediaRef.current?.getTracks) mediaRef.current.getTracks().forEach(t => t.stop());
		if (wsRef.current) wsRef.current.close();
		setIsRecording(false);
	};

	return (
		<div>
			<div className="flex gap-3 mb-3">
				<button
					onClick={() => isRecording ? stopRecording() : startRecording()}
					className={`px-4 py-2 rounded ${isRecording ? 'bg-red-600 text-white' : 'bg-green-600 text-white'}`}
				>
					{isRecording ? 'Stop' : 'Start'}
				</button>
				<button
					onClick={() => { setTranscript([]); localStorage.removeItem('live_transcript'); }}
					className="px-3 py-2 border rounded"
				>
					Clear
				</button>
			</div>
			<div className="h-96 overflow-auto p-3 border rounded bg-gray-50">
				{transcript.length === 0 && <div className="text-gray-500">No transcript yet</div>}
				{transcript.map((t, i) => (
					<div key={i} className="mb-2">
						<div className="text-xs text-gray-400">{new Date(t.time).toLocaleTimeString()}</div>
						<div>{t.text}</div>
					</div>
				))}
			</div>
		</div>
	);
}