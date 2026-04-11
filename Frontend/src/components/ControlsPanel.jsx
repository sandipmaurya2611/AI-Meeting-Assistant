export default function ControlsPanel() {
return (
<div className="mb-4">
<h2 className="font-semibold mb-2">Controls</h2>
<div className="text-sm text-gray-600 mb-2">Upload context docs (PDF/TXT) for RAG</div>
<input type="file" accept=".pdf,.txt,.docx" onChange={async (e) => {
const file = e.target.files[0];
if (!file) return alert('Select a file');


const API_BASE = import.meta.env.VITE_API_URL;
const form = new FormData();
form.append('file', file);
try {
const res = await fetch(`${API_BASE}/upload-doc`, { method: 'POST', body: form });
if (!res.ok) throw new Error('Upload failed');
alert('Uploaded for RAG');
} catch (err) { console.error(err); alert('Upload failed'); }
}} />
</div>
);
}