'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';

const InteractiveTripMap = dynamic(() => import('@/components/InteractiveTripMap'), { ssr: false });
import {
  Clock,
  MapPin,
  DollarSign,
  Edit3,
  Plane,
  Hotel,
  Utensils,
  Compass,
  ShoppingBag,
  FileDown,
  Navigation,
  Globe2,
  Calendar,
  Layers,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { exportTripPDF } from '@/lib/api';

interface ItineraryTimelineProps {
  tripId?: number;
  destinationAnalysis?: any;
  destinationName?: string;
  totalCost?: number;
  version?: number;
  days: any[];
  currency?: string;
  onEditItem?: (item: any) => void;
  onVersionSelect?: (ver: number) => void;
  availableVersions?: number[];
  onSelectSuggestion?: (suggestion: string) => void;
}

export default function ItineraryTimeline({

  tripId,
  destinationAnalysis,
  destinationName,
  totalCost,
  version = 1,
  days,
  currency = 'VND',
  onEditItem,
  onVersionSelect,
  availableVersions = [1],
  onSelectSuggestion
}: ItineraryTimelineProps) {
  const [viewMode, setViewMode] = useState<'timeline' | 'map'>('timeline');
  const getItemIcon = (type: string) => {
    switch (type) {
      case 'FLIGHT':
        return <Plane className="w-4 h-4 text-sky-600" />;
      case 'HOTEL_CHECKIN':
      case 'HOTEL_CHECKOUT':
      case 'HOTEL':
        return <Hotel className="w-4 h-4 text-purple-600" />;
      case 'LUNCH':
      case 'DINNER':
      case 'BREAKFAST':
      case 'RESTAURANT':
        return <Utensils className="w-4 h-4 text-amber-600" />;
      case 'SHOPPING':
        return <ShoppingBag className="w-4 h-4 text-pink-600" />;
      default:
        return <Compass className="w-4 h-4 text-emerald-600" />;
    }
  };

  if (!days || days.length === 0) {
    return (
      <div className="bg-white p-12 text-center rounded-2xl border border-slate-200 shadow-sm flex flex-col items-center justify-center min-h-[500px]">
        <div className="w-16 h-16 bg-sky-50 text-sky-600 rounded-2xl flex items-center justify-center mb-4 border border-sky-100">
          <Globe2 className="w-8 h-8 animate-pulse" />
        </div>
        <h3 className="font-bold text-slate-800 text-lg mb-2">Chưa Có Lịch Trình Nào</h3>
        <p className="text-slate-500 text-sm max-w-md leading-relaxed mb-6">
          Hãy nhập yêu cầu điểm đến tại khung chat bên trái (như Hallstatt, Zermatt, Seoul, Sa Pa...) để AI Agent tự động phân tích và tạo lịch trình hoàn chỉnh!
        </p>
        <div className="flex flex-wrap gap-2 justify-center">
          <button
            onClick={() => onSelectSuggestion ? onSelectSuggestion('Lên lịch Hallstatt, Áo 3 ngày 2 đêm cho 2 người, ngân sách 1.500 EUR, thích hồ và ẩm thực địa phương.') : onEditItem?.({ suggestion: 'Hallstatt, Áo' })}
            className="px-4 py-2 bg-sky-50 hover:bg-sky-100 text-sky-700 rounded-lg text-sm font-medium transition-colors border border-sky-200 shadow-sm"
          >
            Hallstatt, Áo
          </button>
          <button
            onClick={() => onSelectSuggestion ? onSelectSuggestion('Đi Seoul 4 ngày 3 đêm cho 2 người từ Hà Nội, ngân sách 35 triệu VND, thích ẩm thực và mua sắm.') : onEditItem?.({ suggestion: 'Seoul, Hàn Quốc' })}
            className="px-4 py-2 bg-sky-50 hover:bg-sky-100 text-sky-700 rounded-lg text-sm font-medium transition-colors border border-sky-200 shadow-sm"
          >
            Seoul, Hàn Quốc
          </button>
          <button
            onClick={() => onSelectSuggestion ? onSelectSuggestion('Lập kế hoạch Đà Nẵng 3 ngày 2 đêm cho gia đình 4 người, ngân sách 18 triệu, thích biển và đồ ăn.') : onEditItem?.({ suggestion: 'Đà Nẵng, Việt Nam' })}
            className="px-4 py-2 bg-sky-50 hover:bg-sky-100 text-sky-700 rounded-lg text-sm font-medium transition-colors border border-sky-200 shadow-sm"
          >
            Đà Nẵng, Việt Nam
          </button>
        </div>
      </div>
    );
  }

  const airport = destinationAnalysis?.nearest_airport;
  const localCur = destinationAnalysis?.currency;

  return (
    <div className="space-y-6">
      {/* Destination Hero Card */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white rounded-2xl p-5 shadow-lg border border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-xs font-semibold text-sky-400 mb-1">
              <MapPin className="w-4 h-4 text-rose-400" />
              <span>ĐIỂM ĐẾN QUỐC TẾ TỐI ƯU</span>
            </div>
            <h2 className="text-2xl font-black tracking-tight text-white flex items-center space-x-2">
              <span>{destinationName || destinationAnalysis?.city_or_village || 'Lịch Trình Du Lịch'}</span>
            </h2>
            {destinationAnalysis?.country && (
              <p className="text-xs text-slate-300 mt-0.5">
                Quốc gia: <span className="font-semibold text-white">{destinationAnalysis.country}</span>
                {destinationAnalysis.latitude && (
                  <span className="ml-2 font-mono text-slate-400 text-[11px]">
                    (GPS: {destinationAnalysis.latitude.toFixed(3)}, {destinationAnalysis.longitude.toFixed(3)})
                  </span>
                )}
              </p>
            )}
          </div>

          <div className="flex items-center space-x-3">
            {totalCost !== undefined && (
              <div className="bg-white/10 backdrop-blur-md px-4 py-2 rounded-xl border border-white/20 text-right">
                <span className="text-[10px] uppercase font-bold text-slate-300 block">Tổng Chi Phí Ước Tính</span>
                <span className="text-base font-extrabold text-emerald-400">
                  {totalCost.toLocaleString()} VND
                </span>
              </div>
            )}

            {tripId && (
              <button
                onClick={() => exportTripPDF(tripId)}
                className="bg-sky-600 hover:bg-sky-500 text-white px-3.5 py-2.5 rounded-xl text-xs font-semibold flex items-center space-x-1.5 shadow transition"
              >
                <FileDown className="w-4 h-4" />
                <span className="hidden sm:inline">Xuất PDF</span>
              </button>
            )}
          </div>
        </div>

        {/* Global Metadata Badges */}
        <div className="mt-4 pt-3 border-t border-white/10 grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
          {airport && (
            <div className="bg-white/5 rounded-lg p-2 border border-white/10">
              <span className="text-slate-400 block text-[10px]">Sân bay quốc tế gần nhất:</span>
              <span className="font-bold text-sky-300 font-mono">
                {airport.name} ({airport.iata}) ~{airport.distance_km}km
              </span>
            </div>
          )}

          {localCur && (
            <div className="bg-white/5 rounded-lg p-2 border border-white/10">
              <span className="text-slate-400 block text-[10px]">Tiền tệ bản địa:</span>
              <span className="font-bold text-amber-300 font-mono">
                {localCur} (Tra cứu tỷ giá ở bảng bên phải)
              </span>
            </div>
          )}

          <div className="bg-white/5 rounded-lg p-2 border border-white/10 col-span-2 sm:col-span-1">
            <span className="text-slate-400 block text-[10px]">Phiên bản lịch trình:</span>
            <span className="font-bold text-emerald-300 flex items-center space-x-1">
              <Layers className="w-3.5 h-3.5" />
              <span>Trip Version {version}</span>
            </span>
          </div>
        </div>
      </div>

      {/* Version Selector Bar */}
      {availableVersions && availableVersions.length > 1 && (
        <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs text-slate-700">
            <Layers className="w-4 h-4 text-sky-600" />
            <span className="font-bold">Lịch sử điều chỉnh (Dynamic Re-plan):</span>
          </div>
          <div className="flex items-center space-x-1.5">
            {availableVersions.map((v) => (
              <button
                key={v}
                onClick={() => onVersionSelect && onVersionSelect(v)}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition ${
                  version === v
                    ? 'bg-sky-600 text-white shadow'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                }`}
              >
                Version {v} {v === version ? '(Hiện tại)' : ''}
              </button>
            ))}
          </div>
        </div>
      )}


      {/* View Mode Toggle: Timeline vs Interactive Map */}
      <div className="flex items-center justify-between bg-slate-100 p-1.5 rounded-xl border border-slate-200">
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setViewMode('timeline')}
            className={`px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-2 transition ${
              viewMode === 'timeline'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
            }`}
          >
            <Clock className="w-4 h-4 text-sky-600" />
            <span>Lịch trình chi tiết (Timeline)</span>
          </button>
          <button
            onClick={() => setViewMode('map')}
            className={`px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-2 transition ${
              viewMode === 'map'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
            }`}
          >
            <MapPin className="w-4 h-4 text-rose-500" />
            <span>Bản đồ số tương tác (Interactive Map)</span>
          </button>
        </div>

        <span className="text-[11px] font-semibold text-slate-500 pr-2 hidden sm:inline">
          {viewMode === 'map' ? 'Đang xem bản đồ GPS & lộ trình' : `${days.length} ngày khám phá`}
        </span>
      </div>

      {viewMode === 'map' ? (
        <InteractiveTripMap
          days={days}
          destinationName={destinationName}
          destinationAnalysis={destinationAnalysis}
        />
      ) : (
        <div className="space-y-6">
        {days.map((day, dIdx) => (
          <div key={dIdx} className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
            {/* Day Header */}
            <div className="bg-slate-50 px-6 py-3.5 border-b border-slate-200 flex items-center justify-between">
              <h3 className="font-bold text-slate-800 flex items-center space-x-3">
                <span className="bg-sky-600 text-white w-7 h-7 rounded-lg flex items-center justify-center text-xs font-extrabold shadow">
                  {day.day_number}
                </span>
                <span>Ngày {day.day_number} ({day.date})</span>
              </h3>
              <span className="text-xs font-semibold text-slate-600 bg-white px-3 py-1 rounded-full border border-slate-200 shadow-sm">
                {day.items?.length || 0} hoạt động
              </span>
            </div>

            {/* Timeline Activities */}
            <div className="p-6 relative">
              <div className="absolute left-9 top-8 bottom-8 w-0.5 bg-slate-200" />

              <div className="space-y-6 relative">
                {day.items?.map((item: any, iIdx: number) => (
                  <React.Fragment key={iIdx}>
                    <div className="flex items-start space-x-4">
                      {/* Time Slot */}
                      <div className="w-14 shrink-0 text-right pt-1">
                        <span className="text-xs font-bold text-slate-700 block">{item.start_time}</span>
                        <span className="text-[10px] text-slate-400 block">{item.end_time}</span>
                      </div>

                      {/* Icon Node */}
                      <div className="w-8 h-8 rounded-full bg-white border-2 border-sky-500 flex items-center justify-center z-10 shadow-sm shrink-0">
                        {getItemIcon(item.item_type)}
                      </div>

                      {/* Content Card */}
                      <div className="flex-1 bg-slate-50/80 rounded-xl p-4 border border-slate-200 hover:border-sky-400 hover:bg-sky-50/20 transition group">
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <div className="flex items-center space-x-2">
                              <h4 className="font-bold text-slate-900 text-sm">{item.title}</h4>
                              <span className="text-[10px] font-semibold bg-sky-100 text-sky-700 px-2 py-0.5 rounded-full border border-sky-200">
                                {item.item_type}
                              </span>
                            </div>

                            <div className="flex items-center flex-wrap gap-3 text-xs text-slate-500 mt-1.5">
                              <span className="flex items-center space-x-1">
                                <MapPin className="w-3.5 h-3.5 text-slate-400" />
                                <span>{item.location}</span>
                              </span>
                              <span className="flex items-center space-x-1">
                                <Clock className="w-3.5 h-3.5 text-slate-400" />
                                <span>{item.duration_minutes || 60} phút</span>
                              </span>
                            </div>
                          </div>

                          <div className="text-right shrink-0">
                            <span className="text-xs font-bold text-emerald-600 flex items-center space-x-0.5 justify-end">
                              <DollarSign className="w-3.5 h-3.5" />
                              <span>{item.estimated_cost?.toLocaleString()} VND</span>
                            </span>

                            {onEditItem && (
                              <button
                                onClick={() => onEditItem(item)}
                                className="mt-2 text-xs font-semibold text-sky-600 hover:text-sky-800 flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition justify-end ml-auto"
                              >
                                <Edit3 className="w-3.5 h-3.5" />
                                <span>Đổi lịch / Re-plan</span>
                              </button>
                            )}
                          </div>
                        </div>

                        {item.notes && (
                          <p className="mt-2.5 text-xs text-slate-600 bg-white p-2.5 rounded-lg border border-slate-200/80 italic">
                            💡 {item.notes}
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Transit Buffer between items */}
                    {iIdx < (day.items?.length - 1) && (
                      <div className="flex items-center space-x-4 pl-[72px] text-[11px] text-slate-400 py-1">
                        <div className="flex items-center space-x-1 bg-white px-2 py-0.5 rounded-full border border-slate-200">
                          <Navigation className="w-3 h-3 text-sky-500" />
                          <span>Khoảng đệm di chuyển & dự phòng: ~30 phút</span>
                        </div>
                      </div>
                    )}
                  </React.Fragment>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
      )}
    </div>
  );
}
