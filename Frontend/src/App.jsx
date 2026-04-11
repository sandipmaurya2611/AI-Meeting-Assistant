import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import ProtectedRoute from './components/ProtectedRoute';
import MeetingPage from "./Pages/MeetingPage";
import AuthPage from './Pages/AuthPage';
import JoinMeeting from './Pages/JoinMeeting';
import MeetingWithAI from './Pages/MeetingWithAI';

class ErrorBoundary extends React.Component {
	constructor(props) {
		super(props);
		this.state = { hasError: false, error: null };
	}

	static getDerivedStateFromError(error) {
		return { hasError: true, error };
	}

	componentDidCatch(error, info) {
		console.error('App error:', error, info);
	}

	render() {
		if (this.state.hasError) {
			return (
				<div className="min-h-screen bg-slate-950 flex items-center justify-center">
					<div className="p-8 bg-red-500/10 border border-red-500/50 rounded-2xl max-w-md">
						<h2 className="text-xl font-bold mb-2 text-red-400">Application Error</h2>
						<div className="text-red-300">{String(this.state.error)}</div>
						<button
							onClick={() => window.location.reload()}
							className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors"
						>
							Reload Page
						</button>
					</div>
				</div>
			);
		}
		return this.props.children;
	}
}

export default function App() {
	return (
		<ErrorBoundary>
			<BrowserRouter>
				<AuthProvider>
					<Routes>
						{/* Public Routes */}
						<Route path="/auth" element={<AuthPage />} />
						<Route path="/join/:roomName" element={<JoinMeeting />} />
						<Route path="/ai-demo" element={<MeetingWithAI />} />

						{/* Protected Routes */}
						<Route
							path="/"
							element={
								<ProtectedRoute>
									<MeetingPage />
								</ProtectedRoute>
							}
						/>
						<Route
							path="/meeting"
							element={
								<ProtectedRoute>
									<MeetingPage />
								</ProtectedRoute>
							}
						/>

						{/* Fallback */}
						<Route path="*" element={<Navigate to="/" />} />
					</Routes>
				</AuthProvider>
			</BrowserRouter>
		</ErrorBoundary>
	);
}