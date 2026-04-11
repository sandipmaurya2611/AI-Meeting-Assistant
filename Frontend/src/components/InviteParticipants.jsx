import React, { useState } from 'react';

const InviteParticipants = ({ meetingUrl, roomName, onClose }) => {
    const [copied, setCopied] = useState(false);
    const [emailText, setEmailText] = useState('');

    const copyToClipboard = () => {
        navigator.clipboard.writeText(meetingUrl);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const generateEmailText = () => {
        return `You're invited to join a meeting!

Meeting: ${roomName}
Join Link: ${meetingUrl}

Click the link above to join the meeting.

---
Powered by AI Meeting Assistant`;
    };

    const shareViaEmail = () => {
        const subject = encodeURIComponent(`Join Meeting: ${roomName}`);
        const body = encodeURIComponent(generateEmailText());
        window.location.href = `mailto:?subject=${subject}&body=${body}`;
    };

    const shareViaWhatsApp = () => {
        const text = encodeURIComponent(`Join my meeting: ${meetingUrl}`);
        window.open(`https://wa.me/?text=${text}`, '_blank');
    };

    const shareViaTwitter = () => {
        const text = encodeURIComponent(`Join my meeting: ${meetingUrl}`);
        window.open(`https://twitter.com/intent/tweet?text=${text}`, '_blank');
    };

    if (!meetingUrl) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden">
                {/* Header */}
                <div className="bg-black bg-opacity-20 px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <span className="text-3xl">📤</span>
                        <div>
                            <h3 className="text-white font-bold text-xl">Invite Participants</h3>
                            <p className="text-indigo-200 text-sm">Share this meeting link</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-white hover:bg-white hover:bg-opacity-20 rounded-lg p-2 transition-all"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-4">
                    {/* Copy Link */}
                    <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-2xl p-4">
                        <label className="block text-white text-sm font-semibold mb-2">
                            Meeting Link
                        </label>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={meetingUrl}
                                readOnly
                                className="flex-1 bg-white bg-opacity-90 border border-white border-opacity-20 rounded-xl px-4 py-3 text-gray-900 text-sm focus:outline-none font-medium"
                            />
                            <button
                                onClick={copyToClipboard}
                                className="bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-6 py-3 rounded-xl font-semibold transition-all flex items-center gap-2"
                            >
                                {copied ? (
                                    <>
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                        Copied!
                                    </>
                                ) : (
                                    <>
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                        </svg>
                                        Copy
                                    </>
                                )}
                            </button>
                        </div>
                    </div>

                    {/* Share Options */}
                    <div className="bg-white bg-opacity-10 rounded-2xl p-4">
                        <p className="text-white text-sm font-semibold mb-3">Share via</p>
                        <div className="grid grid-cols-3 gap-3">
                            <button
                                onClick={shareViaEmail}
                                className="bg-blue-500 hover:bg-blue-600 text-white p-4 rounded-xl transition-all flex flex-col items-center gap-2"
                            >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                </svg>
                                <span className="text-xs font-semibold">Email</span>
                            </button>

                            <button
                                onClick={shareViaWhatsApp}
                                className="bg-green-500 hover:bg-green-600 text-white p-4 rounded-xl transition-all flex flex-col items-center gap-2"
                            >
                                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z" />
                                </svg>
                                <span className="text-xs font-semibold">WhatsApp</span>
                            </button>

                            <button
                                onClick={shareViaTwitter}
                                className="bg-sky-500 hover:bg-sky-600 text-white p-4 rounded-xl transition-all flex flex-col items-center gap-2"
                            >
                                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" />
                                </svg>
                                <span className="text-xs font-semibold">Twitter</span>
                            </button>
                        </div>
                    </div>

                    {/* QR Code Option */}
                    <div className="bg-white bg-opacity-5 rounded-2xl p-4 border border-white border-opacity-10">
                        <p className="text-indigo-200 text-sm text-center">
                            💡 Tip: Anyone with this link can join the meeting
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default InviteParticipants;
