import React from 'react';

const TranscriptPanel = ({ news }) => {
    if (!news || news.length === 0) {
        return (
            <div className="p-4 text-gray-500 text-sm text-center">
                Đang chờ văn bản phân tích...
            </div>
        );
    }

    const latestNews = news[0];

    return (
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
            <h3 className="text-gray-400 text-xs font-bold uppercase tracking-wider mb-3">
                Văn bản & Bản dịch
            </h3>

            <div className="space-y-4">
                {/* Headline / OCR */}
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs text-blue-400 uppercase tracking-wider">Tiêu đề (OCR)</span>
                        <div className="flex-1 h-px bg-blue-900/30"></div>
                    </div>
                    <p className="text-blue-100 text-sm leading-relaxed font-medium">
                        {latestNews.ocr_text || "No text detected"}
                    </p>
                </div>

                {/* English Summary */}
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs text-gray-500 uppercase tracking-wider">Tóm tắt (English)</span>
                        <div className="flex-1 h-px bg-gray-800"></div>
                    </div>
                    <p className="text-gray-300 text-sm leading-relaxed">
                        {latestNews.english_summary || "No summary available"}
                    </p>
                </div>

                {/* Vietnamese Translation */}
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs text-yellow-500 uppercase tracking-wider">Bản dịch tiếng Việt</span>
                        <div className="flex-1 h-px bg-yellow-900/30"></div>
                    </div>
                    <p className="text-yellow-100 text-sm leading-relaxed font-medium">
                        {latestNews.vietnamese_translation || "Đang dịch..."}
                    </p>
                </div>

                {/* Metadata */}
                <div className="flex items-center gap-4 pt-2 border-t border-gray-800">
                    <span className="text-xs text-gray-500">
                        {new Date(latestNews.timestamp).toLocaleTimeString('vi-VN')}
                    </span>
                    <span className="text-xs text-blue-400">• {latestNews.source}</span>
                </div>
            </div>
        </div>
    );
};

export default TranscriptPanel;
