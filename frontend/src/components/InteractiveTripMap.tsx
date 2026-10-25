'use client';

import React, { useEffect, useRef, useState } from 'react';
import 'leaflet/dist/leaflet.css';
import {
  MapPin, Navigation, Clock, DollarSign, ExternalLink,
  ChevronRight, Compass, Layers, Sparkles
} from 'lucide-react';

export interface MapWaypoint {
  id?: string | number;
  day_number: number;
  order: number;
  title: string;
  item_type: string;
  start_time: string;
  end_time: string;
  location: string;
  latitude: number;
  longitude: number;
  estimated_cost?: number;
  notes?: string;
}

interface InteractiveTripMapProps {
  days: any[];
  destinationName?: string;
  destinationAnalysis?: any;
}

export default function InteractiveTripMap({
  days,
  destinationName,
  destinationAnalysis,
}: InteractiveTripMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const [selectedDay, setSelectedDay] = useState<number | 'ALL'>('ALL');
  const [activeWaypoint, setActiveWaypoint] = useState<MapWaypoint | null>(null);

  // Extract all valid waypoints from days
  const allWaypoints: MapWaypoint[] = [];
  (days || []).forEach((day: any) => {
    const dayNum = day.day_number || 1;
    (day.items || []).forEach((item: any, idx: number) => {
      if (item.latitude && item.longitude) {
        allWaypoints.push({
          id: `${dayNum}-${idx}`,
          day_number: dayNum,
          order: idx + 1,
          title: item.title,
          item_type: item.item_type || 'ATTRACTION',
          start_time: item.start_time,
          end_time: item.end_time,
          location: item.location,
          latitude: Number(item.latitude),
          longitude: Number(item.longitude),
          estimated_cost: item.estimated_cost,
          notes: item.notes,
        });
      }
    });
  });

  const visibleWaypoints = selectedDay === 'ALL'
    ? allWaypoints
    : allWaypoints.filter((wp) => wp.day_number === selectedDay);

  // Initialize and update Leaflet Map
  useEffect(() => {
    if (typeof window === 'undefined' || !mapContainerRef.current) return;

    let isMounted = true;

    import('leaflet').then((L) => {
      if (!isMounted || !mapContainerRef.current) return;

      // Fix default marker icon assets
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      });

      // Default fallback coordinates if no waypoints
      const defaultCenter: [number, number] = destinationAnalysis?.latitude && destinationAnalysis?.longitude
        ? [destinationAnalysis.latitude, destinationAnalysis.longitude]
        : visibleWaypoints.length > 0
          ? [visibleWaypoints[0].latitude, visibleWaypoints[0].longitude]
          : [21.0285, 105.8542];

      if (!mapInstanceRef.current) {
        const map = L.map(mapContainerRef.current, {
          center: defaultCenter,
          zoom: 13,
          zoomControl: true,
        });

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
          maxZoom: 19,
        }).addTo(map);

        mapInstanceRef.current = map;
      }

      const map = mapInstanceRef.current;

      // Clear previous layers (except the base tile layer)
      map.eachLayer((layer: any) => {
        if (!layer._url) {
          map.removeLayer(layer);
        }
      });

      if (visibleWaypoints.length === 0) return;

      const latlngs: [number, number][] = [];

      visibleWaypoints.forEach((wp) => {
        const pos: [number, number] = [wp.latitude, wp.longitude];
        latlngs.push(pos);

        // Marker color styling by category
        let colorClass = 'bg-sky-600';
        if (wp.item_type.includes('HOTEL')) colorClass = 'bg-purple-600';
        else if (wp.item_type.includes('FLIGHT')) colorClass = 'bg-blue-700';
        else if (wp.item_type.includes('LUNCH') || wp.item_type.includes('DINNER') || wp.item_type.includes('RESTAURANT')) colorClass = 'bg-amber-600';
        else if (wp.item_type.includes('SHOPPING')) colorClass = 'bg-pink-600';
        else colorClass = 'bg-emerald-600';

        const customIcon = L.divIcon({
          className: 'custom-map-pin',
          html: `
            <div style="
              background-color: ${colorClass === 'bg-purple-600' ? '#9333ea' : colorClass === 'bg-amber-600' ? '#d97706' : colorClass === 'bg-emerald-600' ? '#059669' : '#0284c7'};
              color: white;
              width: 32px;
              height: 32px;
              border-radius: 50%;
              display: flex;
              align-items: center;
              justify-content: center;
              font-weight: 800;
              font-size: 13px;
              border: 3px solid white;
              box-shadow: 0 4px 10px rgba(0,0,0,0.35);
              transform: translate(-50%, -50%);
            ">
              ${wp.order}
            </div>
          `,
          iconSize: [32, 32],
          iconAnchor: [16, 16],
        });

        const marker = L.marker(pos, { icon: customIcon }).addTo(map);

        const googleMapsDirUrl = `https://www.google.com/maps/dir/?api=1&destination=${wp.latitude},${wp.longitude}`;

        const popupContent = `
          <div style="min-width: 220px; font-family: inherit;">
            <div style="font-size: 11px; font-weight: 700; color: #0284c7; text-transform: uppercase; margin-bottom: 3px;">
              Ngày ${wp.day_number} · Chặng ${wp.order}
            </div>
            <div style="font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 4px;">
              ${wp.title}
            </div>
            <div style="font-size: 12px; color: #64748b; margin-bottom: 6px;">
              ⏱️ ${wp.start_time} - ${wp.end_time}
            </div>
            <div style="font-size: 11px; color: #475569; margin-bottom: 8px;">
              📍 ${wp.location}
            </div>
            <a href="${googleMapsDirUrl}" target="_blank" rel="noopener noreferrer" style="
              display: inline-block;
              background-color: #0284c7;
              color: white;
              text-decoration: none;
              padding: 5px 10px;
              border-radius: 6px;
              font-size: 11px;
              font-weight: 600;
            ">
              🗺️ Chỉ đường Google Maps &rarr;
            </a>
          </div>
        `;

        marker.bindPopup(popupContent);
        marker.on('click', () => {
          setActiveWaypoint(wp);
        });
      });

      // Draw polyline connecting stops
      if (latlngs.length > 1) {
        const polyline = L.polyline(latlngs, {
          color: '#0284c7',
          weight: 4,
          opacity: 0.85,
          dashArray: '6, 8',
        }).addTo(map);

        map.fitBounds(polyline.getBounds(), { padding: [50, 50] });
      } else if (latlngs.length === 1) {
        map.setView(latlngs[0], 14);
      }
    });

    return () => {
      isMounted = false;
    };
  }, [visibleWaypoints, destinationAnalysis]);

  return (
    <div className="space-y-4">
      {/* Day Filter Segmented Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 bg-slate-100 p-2 rounded-xl border border-slate-200">
        <div className="flex flex-wrap items-center gap-1.5">
          <button
            onClick={() => setSelectedDay('ALL')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all shadow-sm ${
              selectedDay === 'ALL'
                ? 'bg-sky-600 text-white shadow-sky-500/20'
                : 'bg-white text-slate-700 hover:bg-slate-200'
            }`}
          >
            🗺️ Toàn bộ chuyến đi ({allWaypoints.length} điểm)
          </button>
          {days.map((d: any) => {
            const dayNum = d.day_number;
            const ptsInDay = allWaypoints.filter((w) => w.day_number === dayNum).length;
            return (
              <button
                key={dayNum}
                onClick={() => setSelectedDay(dayNum)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all shadow-sm ${
                  selectedDay === dayNum
                    ? 'bg-sky-600 text-white shadow-sky-500/20'
                    : 'bg-white text-slate-700 hover:bg-slate-200'
                }`}
              >
                Ngày {dayNum} ({ptsInDay} điểm)
              </button>
            );
          })}
        </div>

        <div className="text-xs text-slate-500 font-medium px-2 flex items-center gap-1.5">
          <Navigation className="w-3.5 h-3.5 text-sky-600" />
          <span>{visibleWaypoints.length} chặng di chuyển</span>
        </div>
      </div>

      {/* Map Canvas */}
      <div className="relative rounded-2xl overflow-hidden border border-slate-200 shadow-md">
        <div
          ref={mapContainerRef}
          className="w-full h-[460px] bg-slate-100 z-0"
        />

        {/* Legend Overlay */}
        <div className="absolute bottom-3 left-3 bg-white/95 backdrop-blur-md px-3 py-2 rounded-xl shadow-lg border border-slate-200 text-[11px] font-semibold text-slate-700 flex flex-wrap items-center gap-3 z-[400]">
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-600 inline-block" /> Vé bay
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-600 inline-block" /> Khách sạn
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-600 inline-block" /> Ăn uống
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-600 inline-block" /> Tham quan
          </span>
        </div>
      </div>

      {/* Waypoint Route Cards */}
      <div className="space-y-2">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
          <Compass className="w-3.5 h-3.5 text-sky-600" />
          Tuyến đường chặng trong {selectedDay === 'ALL' ? 'toàn bộ tour' : `Ngày ${selectedDay}`}
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 max-h-[300px] overflow-y-auto pr-1">
          {visibleWaypoints.map((wp) => (
            <div
              key={wp.id}
              onClick={() => {
                setActiveWaypoint(wp);
                if (mapInstanceRef.current) {
                  mapInstanceRef.current.flyTo([wp.latitude, wp.longitude], 15, { duration: 1.2 });
                }
              }}
              className={`p-3 rounded-xl border transition-all cursor-pointer text-left ${
                activeWaypoint?.id === wp.id
                  ? 'bg-sky-50 border-sky-300 ring-2 ring-sky-400/20'
                  : 'bg-white hover:bg-slate-50 border-slate-200 shadow-sm'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-sky-600 text-white flex items-center justify-center text-xs font-extrabold shrink-0">
                    {wp.order}
                  </span>
                  <div>
                    <h5 className="text-xs font-bold text-slate-800 line-clamp-1">{wp.title}</h5>
                    <p className="text-[11px] text-slate-500 flex items-center gap-1 mt-0.5">
                      <Clock className="w-3 h-3 text-sky-500" /> {wp.start_time} - {wp.end_time} · Ngày {wp.day_number}
                    </p>
                  </div>
                </div>

                <a
                  href={`https://www.google.com/maps/dir/?api=1&destination=${wp.latitude},${wp.longitude}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="p-1.5 text-slate-400 hover:text-sky-600 bg-slate-100 hover:bg-sky-50 rounded-lg transition shrink-0"
                  title="Mở Google Maps chỉ đường"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>

              <p className="text-[11px] text-slate-600 mt-2 line-clamp-1 flex items-center gap-1">
                <MapPin className="w-3 h-3 text-rose-500 shrink-0" />
                {wp.location}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
