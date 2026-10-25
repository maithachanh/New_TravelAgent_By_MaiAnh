'use client';

import Link from 'next/link';
import { Compass, Globe2, ShieldCheck, WalletCards } from 'lucide-react';
import { useApp } from '@/contexts/AppContext';

export default function Navbar() {
  const { currency, language, setCurrency, setLanguage } = useApp();
  return (
    <header className="sticky top-0 z-50 border-b border-white/60 bg-white/80 backdrop-blur-xl">
      <div className="mx-auto flex h-[72px] max-w-[1680px] items-center justify-between gap-3 px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex min-w-0 items-center gap-3">
          <span className="grid h-10 w-10 shrink-0 place-items-center rounded-2xl bg-gradient-to-br from-sky-600 to-indigo-700 text-white shadow-lg shadow-sky-200"><Compass className="h-5 w-5" /></span>
          <span className="min-w-0"><span className="block truncate text-base font-extrabold tracking-tight text-slate-900 sm:text-lg">TravelAgent AI</span><span className="hidden text-[10px] font-medium text-slate-500 sm:block">Lập kế hoạch tự tin, khám phá trọn vẹn</span></span>
        </Link>
        <div className="flex items-center gap-2 sm:gap-3">
          <label className="control-select"><WalletCards className="h-3.5 w-3.5 text-emerald-600" /><select value={currency} onChange={(event) => setCurrency(event.target.value)} aria-label="Đơn vị tiền tệ"><option value="VND">VND</option><option value="USD">USD</option><option value="EUR">EUR</option><option value="JPY">JPY</option><option value="KRW">KRW</option></select></label>
          <label className="control-select"><Globe2 className="h-3.5 w-3.5 text-sky-600" /><select value={language} onChange={(event) => setLanguage(event.target.value)} aria-label="Ngôn ngữ giao diện"><option value="vi">VI</option><option value="en">EN</option><option value="ja">JA</option><option value="ko">KO</option><option value="de">DE</option></select></label>
          <span className="hidden items-center gap-1.5 border-l border-slate-200 pl-3 text-[11px] font-medium text-slate-500 md:flex"><ShieldCheck className="h-4 w-4 text-emerald-500" /> Lập kế hoạch có kiểm tra</span>
        </div>
      </div>
    </header>
  );
}
