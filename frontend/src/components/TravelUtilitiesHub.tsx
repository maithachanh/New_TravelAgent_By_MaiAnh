'use client';

import React, { useEffect, useRef, useState } from 'react';
import {
  ArrowRightLeft, CalendarCheck, Check, Clipboard, DollarSign, Languages,
  LifeBuoy, LoaderCircle, RefreshCw, Send, Sparkles, Hotel, Plane, Compass,
  CheckCircle2, XCircle, AlertCircle, Info, ExternalLink
} from 'lucide-react';
import { askInTripSupport, bookingsAPI, BookingItem, currencyAPI, translationAPI } from '@/lib/api';

interface TravelUtilitiesHubProps {
  tripId?: number;
  destinationCurrency?: string;
  destinationCountry?: string;
  destination?: string;
  origin?: string;
  startDate?: string;
  endDate?: string;
  onBookingUpdated?: () => void;
}

type Tab = 'currency' | 'translation' | 'bookings' | 'support';

const currencies = [
  ['VND', 'Việt Nam đồng'], ['USD', 'Đô la Mỹ'], ['EUR', 'Euro'], ['JPY', 'Yên Nhật'],
  ['KRW', 'Won Hàn Quốc'], ['THB', 'Baht Thái'], ['CHF', 'Franc Thụy Sĩ'], ['GBP', 'Bảng Anh'],
  ['SGD', 'Đô la Singapore'], ['AUD', 'Đô la Úc'],
];

const languages: [string, string][] = [
  // Phổ biến nhất
  ['en', 'Tiếng Anh (English)'],
  ['ja', 'Tiếng Nhật (日本語)'],
  ['ko', 'Tiếng Hàn (한국어)'],
  ['zh-CN', 'Tiếng Trung Giản thể (简体中文)'],
  ['zh-TW', 'Tiếng Trung Phồn thể (繁體中文)'],
  ['fr', 'Tiếng Pháp (Français)'],
  ['de', 'Tiếng Đức (Deutsch)'],
  ['it', 'Tiếng Ý (Italiano)'],
  ['es', 'Tiếng Tây Ban Nha (Español)'],
  ['th', 'Tiếng Thái (ไทย)'],
  ['ru', 'Tiếng Nga (Русский)'],
  // Châu Á & Đông Nam Á
  ['id', 'Tiếng Indonesia (Bahasa Indonesia)'],
  ['ms', 'Tiếng Mã Lai (Bahasa Melayu)'],
  ['tl', 'Tiếng Filipino / Tagalog'],
  ['km', 'Tiếng Khmer / Campuchia (ភាសាខ្មែរ)'],
  ['lo', 'Tiếng Lào (ພາສາລາວ)'],
  ['my', 'Tiếng Miến Điện / Myanmar (မြန်မာ)'],
  ['hi', 'Tiếng Hindi (हिन्दी)'],
  ['bn', 'Tiếng Bengal (বাংলা)'],
  ['ne', 'Tiếng Nepal (नेपाली)'],
  ['si', 'Tiếng Sinhala / Sri Lanka (සිංහල)'],
  ['ta', 'Tiếng Tamil (தமிழ்)'],
  ['te', 'Tiếng Telugu (తెలుగు)'],
  ['ur', 'Tiếng Urdu (اردو)'],
  ['mn', 'Tiếng Mông Cổ (Монгол)'],
  // Châu Âu
  ['pt', 'Tiếng Bồ Đào Nha (Português)'],
  ['nl', 'Tiếng Hà Lan (Nederlands)'],
  ['el', 'Tiếng Hy Lạp (Ελληνικά)'],
  ['tr', 'Tiếng Thổ Nhĩ Kỳ (Türkçe)'],
  ['pl', 'Tiếng Ba Lan (Polski)'],
  ['cs', 'Tiếng Séc (Čeština)'],
  ['sk', 'Tiếng Slovakia (Slovenčina)'],
  ['hu', 'Tiếng Hungary (Magyar)'],
  ['ro', 'Tiếng Romania (Română)'],
  ['bg', 'Tiếng Bulgaria (Български)'],
  ['uk', 'Tiếng Ukraina (Українська)'],
  ['hr', 'Tiếng Croatia (Hrvatski)'],
  ['sr', 'Tiếng Serbia (Српски)'],
  ['sl', 'Tiếng Slovenia (Slovenščina)'],
  ['bs', 'Tiếng Bosnia (Bosanski)'],
  ['sq', 'Tiếng Albania (Shqip)'],
  ['mk', 'Tiếng Macedonia (Македонски)'],
  // Bắc Âu & Baltic
  ['sv', 'Tiếng Thụy Điển (Svenska)'],
  ['no', 'Tiếng Na Uy (Norsk)'],
  ['da', 'Tiếng Đan Mạch (Dansk)'],
  ['fi', 'Tiếng Phần Lan (Suomi)'],
  ['is', 'Tiếng Iceland (Íslenska)'],
  ['et', 'Tiếng Estonia (Eesti)'],
  ['lv', 'Tiếng Latvia (Latviešu)'],
  ['lt', 'Tiếng Litva (Lietuvių)'],
  ['ga', 'Tiếng Ireland / Gaeilge'],
  // Trung Đông & Trung Á
  ['ar', 'Tiếng Ả Rập (العربية)'],
  ['he', 'Tiếng Do Thái (עברית)'],
  ['fa', 'Tiếng Ba Tư (فارسی)'],
  ['ku', 'Tiếng Kurd (Kurdî)'],
  ['az', 'Tiếng Azerbaijan (Azərbaycan)'],
  ['ka', 'Tiếng Gruzia / Georgia (ქართული)'],
  ['hy', 'Tiếng Armenia (Հայերեն)'],
  ['kk', 'Tiếng Kazakh (Қазақ)'],
  ['uz', 'Tiếng Uzbek (Oʻzbek)'],
  ['ky', 'Tiếng Kyrgyz (Кыргызча)'],
  ['tg', 'Tiếng Tajik (Тоҷикӣ)'],
  ['ps', 'Tiếng Pashto (پښتو)'],
  // Châu Phi & Khác
  ['af', 'Tiếng Afrikaans (Nam Phi)'],
  ['sw', 'Tiếng Swahili (Đông Phi)'],
  ['am', 'Tiếng Amharic / Ethiopia (አማርኛ)'],
  ['ha', 'Tiếng Hausa (Nigeria)'],
  ['yo', 'Tiếng Yoruba'],
  ['ig', 'Tiếng Igbo'],
  ['zu', 'Tiếng Zulu'],
  ['xh', 'Tiếng Xhosa'],
  ['mg', 'Tiếng Malagasy (Madagascar)'],
  ['so', 'Tiếng Somali'],
  // Châu Mỹ & Châu Đại Dương
  ['haw', 'Tiếng Hawaii (ʻŌlelo Hawaiʻi)'],
  ['sm', 'Tiếng Samoa (Gagana Sāmoa)'],
  ['mi', 'Tiếng Maori (New Zealand)'],
  ['gu', 'Tiếng Gujarati (ગુજરાતી)'],
  ['kn', 'Tiếng Kannada (ಕನ್ನಡ)'],
  ['ml', 'Tiếng Malayalam (മലയാളം)'],
  ['mr', 'Tiếng Marathi (मराठी)'],
  ['pa', 'Tiếng Punjabi (ਪੰਜਾਬੀ)'],
  ['ca', 'Tiếng Catalan (Català)'],
  ['eu', 'Tiếng Basque (Euskara)'],
  ['gl', 'Tiếng Galicia (Galego)'],
  ['lb', 'Tiếng Luxembourg (Lëtzebuergesch)'],
  ['mt', 'Tiếng Malta (Malti)'],
  ['cy', 'Tiếng Wales / Cymraeg'],
  ['eo', 'Tiếng Esperanto (Quốc tế ngữ)'],
  ['la', 'Tiếng Latinh (Latina)'],
  ['yi', 'Tiếng Yiddish (ייִדיש)'],
  ['su', 'Tiếng Sunda (Basa Sunda)'],
  ['jv', 'Tiếng Java (Basa Jawa)'],
];

const quickPhrases = [
  'Xin chào',
  'Bao nhiêu tiền một đêm?',
  'Cho tôi xem thực đơn',
  'Có món chay không?',
  'Tính tiền, làm ơn',
  'Tôi cần giúp đỡ khẩn cấp'
];

export default function TravelUtilitiesHub({
  tripId = 1,
  destinationCurrency,
  destinationCountry,
  destination = 'Tokyo, Nhật Bản',
  origin = 'TP. Hồ Chí Minh, Việt Nam',
  startDate,
  endDate,
  onBookingUpdated
}: TravelUtilitiesHubProps) {
  const [activeTab, setActiveTab] = useState<Tab>('currency');

  // --- CURRENCY CONVERTER STATE ---
  const [amount, setAmount] = useState('100');
  const [fromCurrency, setFromCurrency] = useState(destinationCurrency || 'USD');
  const [toCurrency, setToCurrency] = useState('VND');
  const [conversion, setConversion] = useState<any>(null);
  const [currencyLoading, setCurrencyLoading] = useState(false);
  const [currencyError, setCurrencyError] = useState('');
  const convertRequestRef = useRef(0);

  const convert = async () => {
    const numericAmount = Number(amount);
    if (!Number.isFinite(numericAmount) || numericAmount <= 0) {
      setCurrencyError('Hãy nhập số tiền lớn hơn 0.');
      return;
    }
    const requestId = ++convertRequestRef.current;
    setCurrencyLoading(true);
    setCurrencyError('');
    try {
      const result = await currencyAPI.convert({ amount: numericAmount, from_currency: fromCurrency, to_currency: toCurrency });
      if (requestId === convertRequestRef.current) setConversion(result);
    } catch (error: any) {
      if (requestId === convertRequestRef.current) {
        setConversion(null);
        setCurrencyError(error?.response?.data?.detail || 'Không thể lấy tỷ giá lúc này. Vui lòng thử lại.');
      }
    } finally {
      if (requestId === convertRequestRef.current) setCurrencyLoading(false);
    }
  };

  useEffect(() => {
    if (destinationCurrency && currencies.some(([code]) => code === destinationCurrency)) {
      setFromCurrency(destinationCurrency);
    }
  }, [destinationCurrency]);

  useEffect(() => { void convert(); }, [fromCurrency, toCurrency]);

  // --- TRANSLATION STATE ---
  const [sourceText, setSourceText] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('en');
  const [translation, setTranslation] = useState<any>(null);
  const [translationLoading, setTranslationLoading] = useState(false);
  const [translationError, setTranslationError] = useState('');
  const [copyNotice, setCopyNotice] = useState(false);

  const translate = async (override?: string) => {
    const text = (override ?? sourceText).trim();
    if (!text) return;
    setSourceText(text);
    setTranslationLoading(true);
    setTranslationError('');
    try {
      const result = await translationAPI.translate(text, targetLanguage, 'vi');
      setTranslation(result);
      if (!result.success && !result.translated_text) {
        setTranslationError(result.error || 'Chưa thể dịch câu này lúc này.');
      }
    } catch (error: any) {
      setTranslation(null);
      setTranslationError(error?.response?.data?.detail || 'Không thể dịch lúc này. Vui lòng thử lại.');
    } finally {
      setTranslationLoading(false);
    }
  };

  const copyTranslation = async () => {
    if (!translation?.translated_text) return;
    try {
      await navigator.clipboard.writeText(translation.translated_text);
      setCopyNotice(true);
      setTimeout(() => setCopyNotice(false), 2000);
    } catch { /* optional */ }
  };

  // --- BOOKINGS (HUMAN-IN-THE-LOOP) STATE ---
  const [bookings, setBookings] = useState<BookingItem[]>([]);
  const [bookingsLoading, setBookingsLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [recLoading, setRecLoading] = useState(false);
  const [bookingActionMsg, setBookingActionMsg] = useState('');

  const loadBookings = async () => {
    setBookingsLoading(true);
    try {
      const data = await bookingsAPI.list();
      setBookings(data || []);
    } catch (e) {
      // Fallback
    } finally {
      setBookingsLoading(false);
    }
  };

  const loadRecommendations = async () => {
    setRecLoading(true);
    try {
      const rec = await bookingsAPI.getRecommendations(destination, origin, tripId);
      setRecommendations(rec);
    } catch (e) {
      // Fallback
    } finally {
      setRecLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'bookings') {
      void loadBookings();
      void loadRecommendations();
    }
  }, [activeTab, destination, origin]);

  const updateBooking = async (id: number, action: 'confirm' | 'cancel') => {
    try {
      await bookingsAPI[action](id);
      await loadBookings();
      setBookingActionMsg(action === 'confirm' ? '✓ Đã xác nhận dịch vụ!' : '✕ Đã hủy yêu cầu.');
      setTimeout(() => setBookingActionMsg(''), 3000);
      onBookingUpdated?.();
    } catch (e) {
      // Ignore
    }
  };

  const handleBookService = async (category: 'hotel' | 'flight' | 'activity', item: any) => {
    try {
      const dynamicCheckIn = startDate || new Date(Date.now() + 14 * 86400000).toISOString().split('T')[0];
      const dynamicCheckOut = endDate || new Date(Date.now() + 18 * 86400000).toISOString().split('T')[0];
      const dynamicActivityDate = startDate || new Date(Date.now() + 15 * 86400000).toISOString().split('T')[0];

      if (category === 'hotel') {
        await bookingsAPI.bookHotel({
          trip_id: tripId,
          hotel_name: item.name,
          city: destination,
          check_in: dynamicCheckIn,
          check_out: dynamicCheckOut,
          price: item.price_per_night || 2000000,
          guests: 2
        });
      } else if (category === 'flight') {
        await bookingsAPI.bookFlight({
          trip_id: tripId,
          flight_number: item.flight_number || 'VN100',
          airline: item.airline || 'Vietnam Airlines',
          origin: origin,
          destination: destination,
          price: item.price_per_person || 4000000,
          passengers: 2
        });
      } else if (category === 'activity') {
        await bookingsAPI.bookActivity({
          trip_id: tripId,
          activity_name: item.name || 'Tour trải nghiệm',
          location: destination,
          date: dynamicActivityDate,
          price: item.price || 350000
        });
      }
      await loadBookings();
      setBookingActionMsg('✓ Đã thêm dịch vụ vào danh sách chờ xác nhận!');
      setTimeout(() => setBookingActionMsg(''), 3000);
      onBookingUpdated?.();
    } catch (e) {
      // Ignore
    }
  };

  // --- IN-TRIP SUPPORT STATE ---
  const [supportQuestion, setSupportQuestion] = useState('');
  const [supportAnswer, setSupportAnswer] = useState('');
  const [supportLoading, setSupportLoading] = useState(false);

  const askSupport = async (queryToAsk?: string) => {
    const q = (queryToAsk ?? supportQuestion).trim();
    if (!q || supportLoading) return;
    setSupportQuestion(q);
    setSupportLoading(true);
    try {
      const res = await askInTripSupport(tripId, q);
      setSupportAnswer(res.agent_response);
    } catch {
      setSupportAnswer('Không thể kết nối trợ lý hành trình. Vui lòng thử lại.');
    } finally {
      setSupportLoading(false);
    }
  };

  const tabs: { id: Tab; label: string; icon: React.ElementType }[] = [
    { id: 'currency', label: 'Đổi tiền', icon: DollarSign },
    { id: 'translation', label: 'Dịch thuật', icon: Languages },
    { id: 'bookings', label: 'Đặt chỗ', icon: CalendarCheck },
    { id: 'support', label: 'Hỗ trợ', icon: LifeBuoy },
  ];

  return (
    <section className="panel-surface flex h-[760px] flex-col overflow-hidden shadow-lg border border-slate-200/80">
      {/* Top Header */}
      <div className="bg-slate-950 px-4 pb-3 pt-4 text-white">
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="rounded-lg bg-amber-400/20 p-1.5 ring-1 ring-amber-400/30">
              <Sparkles className="h-4 w-4 text-amber-300" />
            </span>
            <div>
              <h2 className="text-sm font-bold tracking-tight">Tiện Ích Hành Trình</h2>
              <p className="text-[11px] text-slate-400">Tỷ giá thực tế · Dịch thuật · Đặt chỗ · Hỗ trợ</p>
            </div>
          </div>
        </div>

        {/* Tab Buttons */}
        <div className="grid grid-cols-4 gap-1 rounded-xl bg-white/5 p-1 ring-1 ring-white/10">
          {tabs.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`rounded-lg px-1 py-2 text-[10px] font-semibold transition sm:text-xs ${
                activeTab === id
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-400 hover:bg-white/10 hover:text-white'
              }`}
            >
              <Icon className="mx-auto mb-1 h-3.5 w-3.5" />
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Tab Content */}
      <div className="flex-1 overflow-y-auto bg-slate-50/70 p-4">
        {/* ================= TAB 1: CURRENCY ================= */}
        {activeTab === 'currency' && (
          <div className="space-y-4 animate-in fade-in duration-300">
            <div className="rounded-2xl bg-gradient-to-br from-emerald-600 via-teal-600 to-emerald-700 p-4 text-white shadow-lg shadow-emerald-500/10">
              <div className="flex items-center justify-between">
                <p className="text-xs font-medium text-emerald-100">Quy đổi tỷ giá trực tiếp</p>
                <span className="rounded-full bg-white/20 px-2 py-0.5 text-[10px] font-bold text-white">Live Market</span>
              </div>
              {currencyLoading ? (
                <div className="py-4 text-center">
                  <LoaderCircle className="mx-auto h-7 w-7 animate-spin text-white" />
                  <p className="mt-1 text-xs text-emerald-100">Đang truy vấn tỷ giá thời gian thực...</p>
                </div>
              ) : conversion ? (
                <>
                  <p className="mt-2 text-2xl font-black tracking-tight">{conversion.formatted}</p>
                  <p className="mt-1 text-[11px] text-emerald-100">
                    1 {fromCurrency} ≈ {Number(conversion.rate).toLocaleString('vi-VN')} {toCurrency}
                  </p>
                </>
              ) : (
                <p className="mt-2 text-sm text-emerald-100">Nhập số tiền để quy đổi</p>
              )}
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
              <label className="field-label" htmlFor="currency-amount">Số tiền cần đổi</label>
              <input
                id="currency-amount"
                inputMode="decimal"
                value={amount}
                onChange={(event) => setAmount(event.target.value)}
                className="field-control mt-1.5 text-base font-bold text-slate-800"
                placeholder="100"
              />

              <div className="mt-3 grid grid-cols-[1fr_auto_1fr] items-end gap-2">
                <label className="field-label">
                  Từ
                  <select
                    value={fromCurrency}
                    onChange={(event) => setFromCurrency(event.target.value)}
                    className="field-control mt-1.5 text-xs font-semibold"
                  >
                    {currencies.map(([code, name]) => (
                      <option key={code} value={code}>{code} · {name}</option>
                    ))}
                  </select>
                </label>

                <button
                  onClick={() => { setFromCurrency(toCurrency); setToCurrency(fromCurrency); }}
                  className="mb-0.5 rounded-xl border border-slate-200 p-2 text-sky-700 transition hover:bg-sky-50"
                  aria-label="Đảo chiều tiền tệ"
                  title="Đảo chiều"
                >
                  <ArrowRightLeft className="h-4 w-4" />
                </button>

                <label className="field-label">
                  Sang
                  <select
                    value={toCurrency}
                    onChange={(event) => setToCurrency(event.target.value)}
                    className="field-control mt-1.5 text-xs font-semibold"
                  >
                    {currencies.map(([code, name]) => (
                      <option key={code} value={code}>{code} · {name}</option>
                    ))}
                  </select>
                </label>
              </div>

              <button
                onClick={() => void convert()}
                disabled={currencyLoading}
                className="primary-button mt-4 w-full justify-center"
              >
                {currencyLoading ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                Cập nhật tỷ giá mới nhất
              </button>

              {currencyError && <p role="alert" className="mt-3 text-xs font-medium text-rose-600">{currencyError}</p>}
              
              {conversion && (
                <div className="mt-3 rounded-lg bg-slate-50 p-2.5 text-[11px] text-slate-500 border border-slate-100">
                  <p><strong>Nguồn:</strong> {conversion.source}</p>
                  <p className="mt-0.5 text-[10px] text-slate-400">Cập nhật lúc: {conversion.last_updated}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ================= TAB 2: TRANSLATION ================= */}
        {activeTab === 'translation' && (
          <div className="space-y-4 animate-in fade-in duration-300">
            <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
              <label className="field-label" htmlFor="target-language">Dịch sang ngôn ngữ</label>
              <select
                id="target-language"
                value={targetLanguage}
                onChange={(event) => setTargetLanguage(event.target.value)}
                className="field-control mt-1.5 text-xs font-semibold"
              >
                {languages.map(([code, name]) => (
                  <option key={code} value={code}>{name}</option>
                ))}
              </select>

              <label className="field-label mt-3 block" htmlFor="translate-source">Câu tiếng Việt</label>
              <textarea
                id="translate-source"
                rows={3}
                value={sourceText}
                onChange={(event) => setSourceText(event.target.value)}
                placeholder="Ví dụ: Cho tôi xem thực đơn, làm ơn."
                className="field-control mt-1.5 resize-none text-sm"
              />

              <button
                onClick={() => void translate()}
                disabled={translationLoading || !sourceText.trim()}
                className="primary-button mt-3 w-full justify-center"
              >
                {translationLoading ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <Languages className="h-4 w-4" />}
                Dịch ngay
              </button>

              {translation && (
                <div className="mt-4 rounded-xl border border-indigo-100 bg-indigo-50/70 p-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="text-[10px] font-bold uppercase tracking-wider text-indigo-600">Bản dịch bản địa</p>
                      <p className="mt-1 text-sm font-bold leading-relaxed text-slate-900">{translation.translated_text}</p>
                    </div>
                    <button
                      onClick={() => void copyTranslation()}
                      className="rounded-lg border border-indigo-200 bg-white p-1.5 text-indigo-600 shadow-sm transition hover:bg-indigo-50"
                      title="Sao chép bản dịch"
                    >
                      {copyNotice ? <Check className="h-4 w-4 text-emerald-600" /> : <Clipboard className="h-4 w-4" />}
                    </button>
                  </div>
                  {copyNotice && <p className="mt-1 text-[10px] font-semibold text-emerald-600">Đã sao chép vào bộ nhớ tạm!</p>}
                </div>
              )}

              {translationError && <p role="alert" className="mt-3 text-xs font-medium text-rose-600">{translationError}</p>}
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-3 shadow-sm">
              <p className="mb-2 text-xs font-bold text-slate-700">Mẫu câu du lịch thông dụng</p>
              <div className="flex flex-wrap gap-1.5">
                {quickPhrases.map((phrase) => (
                  <button
                    key={phrase}
                    onClick={() => void translate(phrase)}
                    className="rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-[11px] text-slate-700 transition hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700"
                  >
                    {phrase}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ================= TAB 3: BOOKINGS (HUMAN-IN-THE-LOOP) ================= */}
        {activeTab === 'bookings' && (
          <div className="space-y-4 animate-in fade-in duration-300">
            {/* Purpose & Explanation Banner */}
            <div className="rounded-2xl border border-sky-200 bg-sky-50/80 p-3.5 text-slate-800 shadow-sm">
              <div className="flex items-start gap-2.5">
                <Info className="h-4 w-4 text-sky-600 shrink-0 mt-0.5" />
                <div>
                  <h3 className="text-xs font-bold text-sky-900">Quản lý Đặt Chỗ (Human-in-the-Loop)</h3>
                  <p className="mt-1 text-[11px] leading-relaxed text-slate-600">
                    AI Agent đề xuất vé máy bay, phòng khách sạn và tour tốt nhất cho chuyến đi.
                    Mọi dịch vụ ban đầu ở trạng thái <strong>CHỜ DUYỆT (PENDING)</strong> để bạn toàn quyền xác nhận hoặc hủy theo ý muốn.
                  </p>
                </div>
              </div>
            </div>

            {/* Action Feedback Toast */}
            {bookingActionMsg && (
              <div className="rounded-xl bg-emerald-50 border border-emerald-200 px-3 py-2 text-xs font-bold text-emerald-800 flex items-center gap-1.5 animate-in fade-in">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                {bookingActionMsg}
              </div>
            )}

            {/* Section 1: Active Bookings */}
            <div className="space-y-2.5">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600">Dịch Vụ Đã Đề Xuất</h4>
                  <p className="text-[11px] text-slate-400">Kiểm tra và duyệt các dịch vụ cho lịch trình</p>
                </div>
                <button
                  onClick={() => { void loadBookings(); void loadRecommendations(); }}
                  className="rounded-lg p-1.5 text-slate-500 hover:bg-white hover:text-slate-700"
                  title="Tải lại danh sách"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${bookingsLoading ? 'animate-spin' : ''}`} />
                </button>
              </div>

              {bookingsLoading ? (
                <div className="py-6 text-center">
                  <LoaderCircle className="mx-auto h-6 w-6 animate-spin text-sky-600" />
                  <p className="mt-1.5 text-xs text-slate-500">Đang tải danh sách đặt chỗ...</p>
                </div>
              ) : bookings.length === 0 ? (
                <div className="rounded-xl border border-dashed border-slate-300 bg-white p-5 text-center text-xs text-slate-500">
                  <p>Chưa có yêu cầu đặt chỗ nào trong hệ thống.</p>
                  <p className="mt-1 text-[11px] text-slate-400">Hãy chọn một trong các dịch vụ gợi ý bên dưới để đặt ngay!</p>
                </div>
              ) : (
                bookings.map((booking) => (
                  <article key={booking.id} className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm transition hover:border-slate-300">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-start gap-2">
                        <span className={`p-1.5 rounded-lg shrink-0 mt-0.5 ${
                          booking.category === 'flight' ? 'bg-sky-50 text-sky-600' :
                          booking.category === 'hotel' ? 'bg-amber-50 text-amber-600' :
                          'bg-violet-50 text-violet-600'
                        }`}>
                          {booking.category === 'flight' ? <Plane className="h-4 w-4" /> :
                           booking.category === 'hotel' ? <Hotel className="h-4 w-4" /> :
                           <Compass className="h-4 w-4" />}
                        </span>
                        <div>
                          <p className="text-xs font-bold text-slate-900 leading-snug">{booking.service_name}</p>
                          <p className="mt-0.5 text-[11px] font-semibold text-emerald-600">
                            {Number(booking.price).toLocaleString('vi-VN')} VND
                          </p>
                          <p className="mt-0.5 text-[10px] text-slate-400 font-mono">Mã: {booking.booking_reference}</p>
                        </div>
                      </div>

                      <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-bold ${
                        booking.status === 'CONFIRMED' ? 'bg-emerald-100 text-emerald-800' :
                        booking.status === 'CANCELLED' ? 'bg-slate-100 text-slate-500' :
                        'bg-amber-100 text-amber-800 ring-1 ring-amber-300'
                      }`}>
                        {booking.status === 'CONFIRMED' ? 'ĐÃ DUYỆT' :
                         booking.status === 'CANCELLED' ? 'ĐÃ HỦY' :
                         'CHỜ DUYỆT'}
                      </span>
                    </div>

                    {booking.status === 'PENDING' && (
                      <div className="mt-2.5 flex items-center gap-2 pt-2 border-t border-slate-100">
                        <button
                          onClick={() => void updateBooking(booking.id, 'confirm')}
                          className="flex-1 rounded-lg bg-emerald-600 px-3 py-1.5 text-[11px] font-bold text-white shadow-sm hover:bg-emerald-700 transition"
                        >
                          ✓ Xác Nhận Đặt Chỗ
                        </button>
                        <button
                          onClick={() => void updateBooking(booking.id, 'cancel')}
                          className="rounded-lg border border-slate-200 px-2.5 py-1.5 text-[11px] font-semibold text-slate-600 hover:bg-slate-50 transition"
                        >
                          ✕ Hủy
                        </button>
                      </div>
                    )}
                  </article>
                ))
              )}
            </div>

            {/* Section 2: Recommended Services for this Trip */}
            <div className="space-y-2.5 pt-2 border-t border-slate-200">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">Đề Xuất Dịch Vụ Theo Điểm Đến</h4>
                <p className="text-[11px] text-slate-500">Dịch vụ tối ưu tại {destination} bạn có thể đặt thêm</p>
              </div>

              {recLoading ? (
                <div className="py-4 text-center">
                  <LoaderCircle className="mx-auto h-5 w-5 animate-spin text-slate-400" />
                  <p className="mt-1 text-[11px] text-slate-400">Đang tìm các lựa chọn khách sạn & tour...</p>
                </div>
              ) : recommendations ? (
                <div className="space-y-2">
                  {/* Recommended Hotel */}
                  {recommendations.recommended_hotels?.[0] && (
                    <div className="rounded-xl border border-amber-200/80 bg-amber-50/40 p-2.5 flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <Hotel className="h-4 w-4 text-amber-600 shrink-0" />
                        <div>
                          <p className="text-xs font-bold text-slate-800">{recommendations.recommended_hotels[0].name}</p>
                          <p className="text-[10px] text-slate-500">
                            {recommendations.recommended_hotels[0].rating} ⭐ · {Number(recommendations.recommended_hotels[0].price_per_night).toLocaleString('vi-VN')} VND/đêm
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => void handleBookService('hotel', recommendations.recommended_hotels[0])}
                        className="rounded-lg bg-amber-600 hover:bg-amber-700 text-white px-2.5 py-1 text-[10px] font-bold shrink-0 transition shadow-sm"
                      >
                        Đặt Ngay
                      </button>
                    </div>
                  )}

                  {/* Recommended Flight */}
                  {recommendations.recommended_flights?.[0] && (
                    <div className="rounded-xl border border-sky-200/80 bg-sky-50/40 p-2.5 flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <Plane className="h-4 w-4 text-sky-600 shrink-0" />
                        <div>
                          <p className="text-xs font-bold text-slate-800">{recommendations.recommended_flights[0].airline}</p>
                          <p className="text-[10px] text-slate-500">
                            {recommendations.recommended_flights[0].flight_number} · {Number(recommendations.recommended_flights[0].price_per_person).toLocaleString('vi-VN')} VND/khách
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => void handleBookService('flight', recommendations.recommended_flights[0])}
                        className="rounded-lg bg-sky-600 hover:bg-sky-700 text-white px-2.5 py-1 text-[10px] font-bold shrink-0 transition shadow-sm"
                      >
                        Đặt Vé
                      </button>
                    </div>
                  )}

                  {/* Recommended Activity */}
                  {recommendations.recommended_activities?.[0] && (
                    <div className="rounded-xl border border-violet-200/80 bg-violet-50/40 p-2.5 flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <Compass className="h-4 w-4 text-violet-600 shrink-0" />
                        <div>
                          <p className="text-xs font-bold text-slate-800">{recommendations.recommended_activities[0].name}</p>
                          <p className="text-[10px] text-slate-500">
                            {Number(recommendations.recommended_activities[0].price).toLocaleString('vi-VN')} VND · {recommendations.recommended_activities[0].duration_minutes} phút
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => void handleBookService('activity', recommendations.recommended_activities[0])}
                        className="rounded-lg bg-violet-600 hover:bg-violet-700 text-white px-2.5 py-1 text-[10px] font-bold shrink-0 transition shadow-sm"
                      >
                        Đặt Tour
                      </button>
                    </div>
                  )}
                </div>
              ) : null}
            </div>
          </div>
        )}

        {/* ================= TAB 4: IN-TRIP SUPPORT ================= */}
        {activeTab === 'support' && (
          <div className="space-y-4 animate-in fade-in duration-300">
            <div className="rounded-2xl bg-gradient-to-br from-violet-600 via-indigo-600 to-purple-700 p-4 text-white shadow-lg shadow-violet-500/10">
              <LifeBuoy className="h-5 w-5 text-violet-200" />
              <h3 className="mt-2 font-bold text-sm">Trợ Lý Thông Minh Trong Hành Trình</h3>
              <p className="mt-1 text-xs leading-relaxed text-violet-100">
                Hỏi quán ăn ngon bổ rẻ, dự báo thời tiết, cách đi tàu điện ngầm hoặc gợi ý điểm đến theo thời gian thực.
              </p>
            </div>

            {/* Quick Prompt Questions */}
            <div className="space-y-1.5">
              <p className="text-[11px] font-bold text-slate-600">Câu hỏi mẫu:</p>
              <div className="flex flex-col gap-1.5">
                <button
                  onClick={() => void askSupport(`Tôi hiện đang ở Seoul, hãy đề xuất cho tôi các quán ăn ngon bổ rẻ xung quanh Seoul này`)}
                  className="rounded-xl border border-slate-200 bg-white p-2 text-left text-xs font-medium text-slate-700 hover:border-violet-300 hover:bg-violet-50 transition"
                >
                  🍲 Gợi ý quán ăn ngon bổ rẻ tại Seoul
                </button>
                <button
                  onClick={() => void askSupport(`Thời tiết hôm nay thế nào và nên mang trang phục gì?`)}
                  className="rounded-xl border border-slate-200 bg-white p-2 text-left text-xs font-medium text-slate-700 hover:border-violet-300 hover:bg-violet-50 transition"
                >
                  🌤️ Dự báo thời tiết & trang phục phù hợp
                </button>
                <button
                  onClick={() => void askSupport(`Cách đi tàu điện ngầm và mua thẻ giao thông thuận tiện?`)}
                  className="rounded-xl border border-slate-200 bg-white p-2 text-left text-xs font-medium text-slate-700 hover:border-violet-300 hover:bg-violet-50 transition"
                >
                  🚇 Hướng dẫn đi tàu điện ngầm & thẻ giao thông
                </button>
              </div>
            </div>

            <form
              onSubmit={(event) => {
                event.preventDefault();
                void askSupport();
              }}
              className="rounded-2xl border border-slate-200 bg-white p-3.5 shadow-sm"
            >
              <label className="field-label block" htmlFor="support-query">Đặt câu hỏi cho AI Agent</label>
              <textarea
                id="support-query"
                rows={3}
                value={supportQuestion}
                onChange={(event) => setSupportQuestion(event.target.value)}
                className="field-control mt-1.5 resize-none text-xs"
                placeholder="Ví dụ: Tôi hiện đang ở Seoul, hãy đề xuất cho tôi các quán ăn ngon bổ rẻ xung quanh Seoul này..."
              />
              <button
                type="submit"
                disabled={!supportQuestion.trim() || supportLoading}
                className="primary-button mt-3 w-full justify-center"
              >
                {supportLoading ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                Gửi câu hỏi
              </button>
            </form>

            {supportAnswer && (
              <div className="rounded-2xl border border-sky-100 bg-white p-4 text-xs leading-relaxed text-slate-800 shadow-sm whitespace-pre-line animate-in fade-in">
                {supportAnswer}
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
