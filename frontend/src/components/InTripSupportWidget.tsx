'use client';

import React, { useState } from 'react';
import { MessageSquare, Send, Compass, MapPin, Clock } from 'lucide-react';
import { askInTripSupport } from '@/lib/api';

export default function InTripSupportWidget({ tripId }: { tripId?: number }) {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || loading) return;
    setLoading(true);
    try {
      const res = await askInTripSupport(tripId || 1, query);
      setResponse(res.agent_response);
    } catch (err) {
      setResponse('Rất tiếc, có lỗi xảy ra. Hãy thử lại.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gradient-to-br from-indigo-900 to-slate-900 text-white p-6 rounded-2xl shadow-xl border border-indigo-700/50">
      <div className="flex items-center space-x-3 mb-4">
        <div className="p-2 bg-indigo-500/20 rounded-xl border border-indigo-400/30">
          <Compass className="w-5 h-5 text-indigo-300" />
        </div>
        <div>
          <h3 className="font-bold text-base">Hỗ Trợ Khách Trong Chuyến Đi (In-Trip Assistant)</h3>
          <p className="text-xs text-indigo-200">Nhắc lịch • Đề xuất địa điểm gần GPS • Thay đổi khẩn cấp</p>
        </div>
      </div>

      <form onSubmit={handleAsk} className="flex space-x-2 mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ví dụ: Bây giờ ăn tối ở đâu ngon gần đây?..."
          className="flex-1 bg-white/10 border border-indigo-400/30 rounded-xl px-4 py-2.5 text-sm placeholder-indigo-300 text-white focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2.5 rounded-xl font-medium text-sm flex items-center space-x-1 shadow"
        >
          <Send className="w-4 h-4" />
          <span>Hỏi AI</span>
        </button>
      </form>

      {response && (
        <div className="bg-white/10 border border-indigo-400/20 p-4 rounded-xl text-sm leading-relaxed text-indigo-100">
          {response}
        </div>
      )}
    </div>
  );
}
