'use client';

import React, { useState } from 'react';
import { Globe2, HeartHandshake, Layers3, Navigation, ShieldCheck, Sparkles } from 'lucide-react';
import ChatAgent from '@/components/ChatAgent';
import ItineraryTimeline from '@/components/ItineraryTimeline';
import ReplanModal from '@/components/ReplanModal';
import TravelUtilitiesHub from '@/components/TravelUtilitiesHub';

export default function Home() {
  const [tripData, setTripData] = useState<any>(null);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [isReplanOpen, setIsReplanOpen] = useState(false);
  const [versions, setVersions] = useState<Record<number, any[]>>({});
  const [currentVersion, setCurrentVersion] = useState(1);

  const handleItineraryGenerated = (data: any) => {
    setTripData(data);
    const version = data.version || 1;
    setCurrentVersion(version);
    if (data.itinerary?.length) setVersions({ [version]: data.itinerary });
  };

  const handleReplanSuccess = (itinerary: any[], version?: number, totalCost?: number) => {
    const nextVersion = version || currentVersion + 1;
    setVersions((previous) => ({ ...previous, [nextVersion]: itinerary }));
    setCurrentVersion(nextVersion);
    setTripData((previous: any) => previous ? { ...previous, itinerary, version: nextVersion, total_cost: totalCost ?? previous.total_cost } : previous);
  };

  const selectVersion = (version: number) => {
    if (!tripData || !versions[version]) return;
    setCurrentVersion(version);
    setTripData({ ...tripData, itinerary: versions[version], version });
  };

  return (
    <div className="space-y-6 pb-2">
      <section className="hero-surface relative overflow-hidden px-6 py-7 sm:px-8 sm:py-9">
        <div className="hero-orb -right-8 -top-10 h-52 w-52" style={{ animationDelay: '0s' }} />
        <div className="hero-orb -bottom-28 left-1/3 h-60 w-60 opacity-30" style={{ animationDelay: '2s' }} />
        <div className="hero-orb top-1/2 right-1/4 h-40 w-40 opacity-20" style={{ animationDelay: '4s' }} />
        <div className="relative max-w-4xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-semibold text-sky-100 backdrop-blur shadow-lg">
            <Sparkles className="h-3.5 w-3.5 text-amber-200 animate-pulse" /> Lập kế hoạch thông minh · Tối ưu theo nhu cầu
          </div>
          <h1 className="mt-4 max-w-3xl text-3xl font-black tracking-tight text-white sm:text-4xl animate-in fade-in slide-in-from-left-4 duration-700">
            Chuyến đi được thiết kế theo cách của bạn.
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed text-sky-100 sm:text-base animate-in fade-in slide-in-from-left-4 duration-700 delay-100">
            Nhập mong muốn bằng ngôn ngữ tự nhiên. TravelAgent AI sẽ phân tích điểm đến, ngân sách và sở thích để tạo lịch trình rõ ràng, dễ điều chỉnh.
          </p>
          <div className="mt-5 flex flex-wrap gap-x-5 gap-y-2 text-xs font-medium text-sky-100 animate-in fade-in slide-in-from-left-4 duration-700 delay-200">
            <span className="feature-chip hover-lift"><ShieldCheck className="h-3.5 w-3.5 text-emerald-300" /> Dữ liệu có trạng thái rõ ràng</span>
            <span className="feature-chip hover-lift"><Navigation className="h-3.5 w-3.5 text-amber-200" /> Tối ưu hành trình</span>
            <span className="feature-chip hover-lift"><Layers3 className="h-3.5 w-3.5 text-violet-200" /> Điều chỉnh phiên bản</span>
            <span className="feature-chip hover-lift"><HeartHandshake className="h-3.5 w-3.5 text-rose-200" /> Hỗ trợ xuyên suốt</span>
          </div>
        </div>
        <Globe2 className="absolute -right-4 -bottom-10 h-52 w-52 text-white/10 sm:right-8 animate-pulse" />
      </section>

      <section className="grid items-start gap-5 xl:grid-cols-12">
        <div className="xl:col-span-4 animate-in fade-in slide-in-from-bottom-4 duration-500"><ChatAgent onItineraryGenerated={handleItineraryGenerated} /></div>
        <div className="xl:col-span-5 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-100"><div className="panel-surface min-h-[720px] p-4 sm:p-5"><ItineraryTimeline tripId={tripData?.trip_id} destinationAnalysis={tripData?.destination_analysis} destinationName={tripData?.destination} totalCost={tripData?.total_cost} version={currentVersion} availableVersions={Object.keys(versions).map(Number)} onVersionSelect={selectVersion} days={tripData?.itinerary || []} onEditItem={(item: any) => { setSelectedItem(item); setIsReplanOpen(true); }} /></div></div>
        <div className="xl:col-span-3 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-200">
          <TravelUtilitiesHub
            tripId={tripData?.trip_id || 1}
            destinationCurrency={tripData?.destination_analysis?.currency || 'VND'}
            destinationCountry={tripData?.destination_analysis?.country}
            destination={tripData?.destination || 'Tokyo, Nhật Bản'}
            origin={tripData?.origin || 'TP. Hồ Chí Minh, Việt Nam'}
          />
        </div>
      </section>

      <ReplanModal isOpen={isReplanOpen} onClose={() => setIsReplanOpen(false)} tripId={tripData?.trip_id || 1} item={selectedItem} onReplanSuccess={handleReplanSuccess} />
    </div>
  );
}
