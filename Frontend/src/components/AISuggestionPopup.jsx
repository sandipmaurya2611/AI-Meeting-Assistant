import React, { useState, useEffect } from 'react';

const AISuggestionPopup = ({ suggestion, onClose }) => {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        if (suggestion) {
            setIsVisible(true);
        }
    }, [suggestion]);

    if (!suggestion || !isVisible) return null;

    return (
        <div className="fixed bottom-6 right-6 z-50 animate-slide-in">
            {/* Popup Container */}
            <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-2xl shadow-2xl max-w-md w-96 overflow-hidden">
                {/* Header */}
                <div className="bg-black bg-opacity-20 px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                            <span className="text-2xl">🧠</span>
                        </div>
                        <div>
                            <h3 className="text-white font-bold text-lg">AI Co-Pilot</h3>
                            <p className="text-indigo-200 text-xs">Real-time suggestion</p>
                        </div>
                    </div>
                    <button
                        onClick={() => {
                            setIsVisible(false);
                            setTimeout(() => onClose && onClose(), 300);
                        }}
                        className="text-white hover:bg-white hover:bg-opacity-20 rounded-lg p-2 transition-all"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="width" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-4">
                    {/* Suggestion */}
                    {suggestion.suggestion && (
                        <div className="bg-white bg-opacity-10 rounded-xl p-4 backdrop-blur-sm">
                            <div className="flex items-start gap-3">
                                <span className="text-2xl">💬</span>
                                <div className="flex-1">
                                    <p className="text-white font-semibold text-sm mb-1">Say Next:</p>
                                    <p className="text-white text-base leading-relaxed">
                                        "{suggestion.suggestion}"
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Confusion Alert */}
                    {suggestion.confusion_detected && (
                        <div className="bg-yellow-500 bg-opacity-20 border border-yellow-400 rounded-xl p-3">
                            <div className="flex items-center gap-2">
                                <span className="text-xl">⚠️</span>
                                <p className="text-yellow-100 text-sm font-medium">
                                    Client seems confused - clarify your point!
                                </p>
                            </div>
                        </div>
                    )}

                    {/* Follow-up Question */}
                    {suggestion.follow_up_question && (
                        <div className="bg-white bg-opacity-10 rounded-xl p-3">
                            <div className="flex items-start gap-2">
                                <span className="text-lg">❓</span>
                                <div>
                                    <p className="text-indigo-200 text-xs font-semibold mb-1">Then Ask:</p>
                                    <p className="text-white text-sm">{suggestion.follow_up_question}</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Talking Points */}
                    {suggestion.talking_points && suggestion.talking_points.length > 0 && (
                        <div className="bg-white bg-opacity-10 rounded-xl p-4">
                            <div className="flex items-start gap-2">
                                <span className="text-lg">📌</span>
                                <div className="flex-1">
                                    <p className="text-indigo-200 text-xs font-semibold mb-2">Key Points:</p>
                                    <ul className="space-y-1">
                                        {suggestion.talking_points.map((point, idx) => (
                                            <li key={idx} className="text-white text-sm flex items-start gap-2">
                                                <span className="text-indigo-300 mt-1">•</span>
                                                <span>{point}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Task Creation */}
                    {suggestion.task_creation && (
                        <div className="bg-green-500 bg-opacity-20 border border-green-400 rounded-xl p-3">
                            <div className="flex items-start gap-2">
                                <span className="text-lg">✅</span>
                                <div>
                                    <p className="text-green-200 text-xs font-semibold mb-1">Action Item:</p>
                                    <p className="text-white text-sm">{suggestion.task_creation}</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* CRM Update */}
                    {suggestion.crm_update && (
                        <div className="bg-white bg-opacity-5 rounded-xl p-3 border border-white border-opacity-10">
                            <div className="flex items-start gap-2">
                                <span className="text-lg">💼</span>
                                <div>
                                    <p className="text-indigo-200 text-xs font-semibold mb-1">CRM Update:</p>
                                    <p className="text-white text-sm">{suggestion.crm_update}</p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <style jsx>{`
        @keyframes slide-in {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }

        .animate-slide-in {
          animation: slide-in 0.3s ease-out;
        }
      `}</style>
        </div>
    );
};

export default AISuggestionPopup;
