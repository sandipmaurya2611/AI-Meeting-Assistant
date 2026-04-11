import React from 'react';
export default function SuggestionsPanel() {
	const [suggestions] = React.useState(() => {
		try {
			const s = JSON.parse(localStorage.getItem('ai_suggestions') || '[]');
			return Array.isArray(s) ? s : [];
		} catch {
			return [];
		}
	});

	return (
		<div>
			<h2 className="font-semibold mb-2">AI Suggestions</h2>
			<div className="space-y-3">
				{suggestions.length === 0 && (
					<div className="text-sm text-gray-500">No suggestions yet. Start a meeting.</div>
				)}
				{suggestions.map((s, i) => (
					<div key={i} className="p-2 border rounded">
						<div className="text-xs text-gray-400">{s.time ? new Date(s.time).toLocaleTimeString() : ''}</div>
						<div className="font-medium">{s.title}</div>
						<div className="text-sm text-gray-700">{s.detail}</div>
					</div>
				))}
			</div>
		</div>
	);
}