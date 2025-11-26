import React from 'react';

const AnalyticsPanel = ({ data }) => {
    if (!data) return <div className="p-4 text-gray-500">Waiting for data...</div>;

    return (
        <div className="bg-gray-900 border-l border-gray-800 p-4 w-80 flex flex-col gap-6 h-full overflow-y-auto">
            <div>
                <h3 className="text-gray-400 text-xs font-bold uppercase tracking-wider mb-3">Real-time Sentiment</h3>
                <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-300">Global Score</span>
                    <span className={`text-lg font-bold ${data.sentiment_score > 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {data.sentiment_score > 0 ? '+' : ''}{data.sentiment_score}
                    </span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                    <div
                        className={`h-2 rounded-full transition-all duration-500 ${data.sentiment_score > 0 ? 'bg-green-500' : 'bg-red-500'}`}
                        style={{ width: `${Math.abs(data.sentiment_score) * 100}%` }}
                    ></div>
                </div>
            </div>

            <div>
                <h3 className="text-gray-400 text-xs font-bold uppercase tracking-wider mb-3">Trending Keywords</h3>
                <div className="flex flex-wrap gap-2">
                    {data.trending_keywords?.map((keyword, idx) => (
                        <span key={idx} className="bg-gray-800 text-gray-300 text-xs px-2 py-1 rounded border border-gray-700">
                            #{keyword}
                        </span>
                    ))}
                </div>
            </div>

            <div>
                <h3 className="text-gray-400 text-xs font-bold uppercase tracking-wider mb-3">Active Sources</h3>
                <div className="grid grid-cols-2 gap-2">
                    <div className="bg-gray-800 p-3 rounded border border-gray-700 text-center">
                        <div className="text-2xl font-bold text-white">{data.active_sources}</div>
                        <div className="text-xs text-gray-500">Channels</div>
                    </div>
                    <div className="bg-gray-800 p-3 rounded border border-gray-700 text-center">
                        <div className="text-2xl font-bold text-white">{data.total_mentions}</div>
                        <div className="text-xs text-gray-500">Mentions</div>
                    </div>
                </div>
            </div>

            <div className="mt-auto pt-4 border-t border-gray-800">
                <div className="bg-blue-900/20 border border-blue-900/50 p-3 rounded">
                    <h4 className="text-blue-400 text-xs font-bold mb-1">AI INSIGHT</h4>
                    <p className="text-gray-300 text-xs leading-relaxed">
                        High volume of mentions detected regarding "Trade War". Sentiment analysis indicates increasing tension. Recommended action: Monitor Asian markets.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default AnalyticsPanel;
