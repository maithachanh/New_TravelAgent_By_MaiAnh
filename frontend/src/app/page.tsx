'use client';

import React, { useState } from 'react';
import ChatAgent from '@/components/ChatAgent';
import ItineraryTimeline from '@/components/ItineraryTimeline';
import TravelUtilitiesHub from '@/components/TravelUtilitiesHub';
import ReplanModal from '@/components/ReplanModal';
import { Globe, Sparkles, Navigation, Layers, ShieldCheck, HeartHandshake } from 'lucide-react';

export default function Home() {
  const [tripData, setTripData] = useState<any>(null);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [isReplanOpen, setIsReplanOpen] = useState(false);
  const [versionHistories, setVersionHistories] = useState<{ [version: number]: any[] }>({});
  const [currentVersion, setCurrentVersion] = useState<number>(1);

  const handleItineraryGenerated = (data: any) => {
    setTripData(data);
    const ver = data.version || 1;
    setCurrentVersion(ver);
    if (data.itinerary) {
      setVersionHistories({ [ver]: data.itinerary });
    }
  };

  const handleEditItem = (item: any) => {
    setSelectedItem(item);
    setIsReplanOpen(true);
  };

  const handleReplanSuccess = (newItinerary: any, newVersion?: number, newTotalCost?: number) => {
    const nextVer = newVersion || (tripData?.version || 1) + 1;
    setCurrentVersion(nextVer);
    setVersionHistories((prev) => ({
      ...prev,
      [nextVer]: newItinerary,
    }));

    if (tripData) {
      setTripData({
        ...tripData,
        itinerary: newItinerary,
        version: nextVer,
        total_cost: newTotalCost !== undefined ? newTotalCost : tripData.total_cost,
      });
    }
  };

  const handleVersionSelect = (ver: number) => {
    setCurrentVersion(ver);
    if (versionHistories[ver] && tripData) {
      setTripData({
        ...tripData,
        itinerary: versionHistories[ver],
        version: ver,
      });
    }
  };

  const destinationCurrency = tripData?.destination_analysis?.currency || 'EUR';
  const destinationCountry = tripData?.destination_analysis?.country || '';

  return (
    <div className="space-y-6">
      {/* Platform Banner */}
      <div className="bg-gradient-to-r from-sky-700 via-indigo-700 to-sky-900 text-white rounded-3xl p-6 sm:p-7 shadow-xl border border-sky-800/40 relative overflow-hidden">
        <div className="absolute right-0 top-0 bottom-0 opacity-10 pointer-events-none flex items-center pr-10">
          <Globe className="w-80 h-80 text-white" />
        </div>

        <div className="relative z-10 max-w-4xl">
          <div className="inline-flex items-center space-x-2 bg-white/10 backdrop-blur-md px-3 py-1 rounded-full text-xs font-semibold text-sky-200 border border-white/20 mb-3">
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            <span>Universal AI Travel Planning Platform • Toàn Cầu Hoá 100%</span>
          </div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight">
            Hệ Thống Travel Agent AI Tự Lập Kế Hoạch & Đồng Hành Toàn Cầu
          </h1>
          <p className="mt-2 text-sky-100 text-xs sm:text-sm leading-relaxed max-w-3xl">
            Tự động tiếp nhận bất kỳ quốc gia, thành phố hay ngôi làng nào trên thế giới qua ngôn ngữ tự nhiên. 
            Tích hợp định vị OpenStreetMap, tỷ giá thực tế Frankfurter API, tối ưu lộ trình Haversine TSP và bộ công cụ du lịch trực tuyến.
          </p>

          <div className="mt-4 flex flex-wrap gap-2 sm:gap-4 text-[11px] sm:text-xs font-medium text-sky-200">
            <span className="flex items-center space-x-1">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Zero-Hallucination Tools</span>
            </span>
            <span className="flex items-center space-x-1">
              <Navigation className="w-3.5 h-3.5 text-amber-300" />
              <span>Đệm Di Chuyển 30 Phút</span>
            </span>
            <span className="flex items-center space-x-1">
              <Layers className="w-3.5 h-3.5 text-sky-300" />
              <span>Dynamic Re-planning & Versioning</span>
            </span>
            <span className="flex items-center space-x-1">
              <HeartHandshake className="w-3.5 h-3.5 text-rose-300" />
              <span>Human-in-the-Loop Bookings</span>
            </span>
          </div>
        </div>
      </div>

      {/* 3-Panel Synchronized Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Panel 1: AI Planner Chatbot (Left - 32%) */}
        <div className="lg:col-span-4 h-full">
          <ChatAgent onItineraryGenerated={handleItineraryGenerated} />
        </div>

        {/* Panel 2: Interactive Itinerary & Timeline (Center - 44%) */}
        <div className="lg:col-span-5 h-full">
          <div className="bg-white p-4 sm:p-5 rounded-2xl shadow-xl border border-slate-200 min-h-[750px]">
            <ItineraryTimeline
              tripId={tripData?.trip_id}
              destinationAnalysis={tripData?.destination_analysis}
              destinationName={tripData?.destination}
              totalCost={tripData?.total_cost}
              version={currentVersion}
              availableVersions={Object.keys(versionHistories).map(Number)}
              onVersionSelect={handleVersionSelect}
              days={tripData?.itinerary || []}
              onEditItem={handleEditItem}
            />
          </div>
        </div>

        {/* Panel 3: Universal Travel Utilities Hub (Right - 24%) */}
        <div className="lg:col-span-3 h-full">
          <TravelUtilitiesHub
            tripId={tripData?.trip_id || 1}
            destinationCurrency={destinationCurrency}
            destinationCountry={destinationCountry}
            onBookingUpdated={() => {
              // Proactively refresh if needed
            }}
          />
        </div>
      </div>

      {/* Dynamic Re-planner Modal */}
      <ReplanModal
        isOpen={isReplanOpen}
        onClose={() => setIsReplanOpen(false)}
        tripId={tripData?.trip_id || 1}
        item={selectedItem}
        onReplanSuccess={handleReplanSuccess}
      />
    </div>
  );
}
