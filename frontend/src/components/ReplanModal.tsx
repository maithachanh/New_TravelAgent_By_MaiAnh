'use client';

import React, { useState } from 'react';
import { X, RefreshCw, AlertCircle } from 'lucide-react';
import { replanTrip } from '@/lib/api';

interface ReplanModalProps {
  isOpen: boolean;
  onClose: () => void;
  tripId: number;
  item: any;
  onReplanSuccess: (newItinerary: any, newVersion?: number, newTotalCost?: number) => void;
}

export default function ReplanModal({ isOpen, onClose, tripId, item, onReplanSuccess }: ReplanModalProps) {
  const [newStartTime, setNewStartTime] = useState(item?.start_time || '10:00');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen || !item) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await replanTrip(tripId, item.id || 1, notes, newStartTime);
      onReplanSuccess(res.updated_itinerary, res.version, res.total_cost);
      onClose();
    } catch (err) {
      alert('Không thể thực hiện điều chỉnh lịch trình. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 border border-slate-200">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <h3 className="font-bold text-lg text-slate-900 flex items-center space-x-2">
            <RefreshCw className="w-5 h-5 text-sky-600" />
            <span>AI Dynamic Re-planner</span>
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div className="bg-sky-50 p-3 rounded-xl text-xs text-sky-800 border border-sky-200 flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-sky-600 mt-0.5" />
            <p>
              Khi bạn thay đổi giờ hoặc hủy hoạt động <b>"{item.title}"</b>, AI Agent sẽ tự động điều chỉnh khoảng thời gian và khoảng cách cho toàn bộ các lịch trình tiếp theo!
            </p>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Giờ bắt đầu mới</label>
            <input
              type="time"
              value={newStartTime}
              onChange={(e) => setNewStartTime(e.target.value)}
              className="w-full border border-slate-300 rounded-xl px-3 py-2 text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Ghi chú hoặc lý do thay đổi</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="VD: Muốn dành thêm thời gian chụp ảnh hoặc dời sang chiều..."
              className="w-full border border-slate-300 rounded-xl px-3 py-2 text-sm h-20 focus:ring-2 focus:ring-sky-500 focus:outline-none"
            />
          </div>

          <div className="flex items-center justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-300 text-slate-700 rounded-xl text-sm font-medium hover:bg-slate-50"
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-sm font-medium flex items-center space-x-1.5 shadow-sm disabled:opacity-50"
            >
              {loading && <RefreshCw className="w-4 h-4 animate-spin" />}
              <span>Tự Động Re-Plan</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
