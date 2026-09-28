'use client';

import React from 'react';
import Link from 'next/link';
import { Compass, Calendar, Sparkles, Globe, DollarSign, ShieldCheck } from 'lucide-react';
import { useApp } from '@/contexts/AppContext';

export default function Navbar() {
  const { language, setLanguage, currency, setCurrency } = useApp();

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link href="/" className="flex items-center space-x-3">
          <div className="bg-gradient-to-tr from-sky-600 to-indigo-600 text-white p-2.5 rounded-xl shadow-md">
            <Compass className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-xl text-slate-900 tracking-tight">TravelAgent AI</span>
              <span className="text-[10px] font-bold px-2 py-0.5 bg-sky-100 text-sky-800 rounded-full border border-sky-200">
                Worldwide
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-medium">Toàn cầu hoá • Không giới hạn điểm đến</p>
          </div>
        </Link>

        {/* Global Controls & Links */}
        <div className="flex items-center space-x-3 sm:space-x-5">
          {/* Currency Switcher */}
          <div className="flex items-center space-x-1 bg-slate-100 px-2.5 py-1.5 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700">
            <DollarSign className="w-3.5 h-3.5 text-emerald-600" />
            <select
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              className="bg-transparent focus:outline-none cursor-pointer text-xs font-bold text-slate-800"
            >
              <option value="VND">VND (₫)</option>
              <option value="USD">USD ($)</option>
              <option value="EUR">EUR (€)</option>
              <option value="CHF">CHF (Fr)</option>
              <option value="KRW">KRW (₩)</option>
              <option value="JPY">JPY (¥)</option>
            </select>
          </div>

          {/* Language Switcher */}
          <div className="flex items-center space-x-1 bg-slate-100 px-2.5 py-1.5 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700">
            <Globe className="w-3.5 h-3.5 text-sky-600" />
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-transparent focus:outline-none cursor-pointer text-xs font-bold text-slate-800"
            >
              <option value="vi">Tiếng Việt</option>
              <option value="en">English</option>
              <option value="ko">한국어</option>
              <option value="ja">日本語</option>
              <option value="de">Deutsch</option>
              <option value="fr">Français</option>
            </select>
          </div>

          <div className="hidden md:flex items-center space-x-2 text-xs text-slate-500 font-medium pl-2 border-l border-slate-200">
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
            <span>OpenStreetMap & Frankfurter Live</span>
          </div>
        </div>
      </div>
    </header>
  );
}
