'use client';

import React, { useState, useEffect } from 'react';
import {
  DollarSign,
  Languages,
  CalendarCheck,
  LifeBuoy,
  RefreshCw,
  CheckCircle,
  XCircle,
  ArrowRightLeft,
  Volume2,
  Copy,
  AlertTriangle,
  PhoneCall,
  ShieldAlert,
  Send,
  Sparkles
} from 'lucide-react';
import { currencyAPI, translationAPI, bookingsAPI, askInTripSupport, BookingItem } from '@/lib/api';

interface TravelUtilitiesHubProps {
  tripId?: number;
  destinationCurrency?: string;
  destinationCountry?: string;
  onBookingUpdated?: () => void;
}

export default function TravelUtilitiesHub({
  tripId = 1,
  destinationCurrency = 'EUR',
  destinationCountry = 'Áo',
  onBookingUpdated
}: TravelUtilitiesHubProps) {
  const [activeTab, setActiveTab] = useState<'currency' | 'translation' | 'bookings' | 'intrip'>('currency');

  // --- Currency Converter State ---
  const [amount, setAmount] = useState<number>(100);
  const [fromCurrency, setFromCurrency] = useState<string>('EUR');
  const [toCurrency, setToCurrency] = useState<string>('VND');
  const [convertedResult, setConvertedResult] = useState<number | null>(null);
  const [exchangeRate, setExchangeRate] = useState<number | null>(null);
  const [currencyLoading, setCurrencyLoading] = useState<boolean>(false);

  // Sync destination currency when changed
  useEffect(() => {
    if (destinationCurrency && destinationCurrency !== fromCurrency) {
      setFromCurrency(destinationCurrency);
    }
  }, [destinationCurrency]);

  const handleConvert = async () => {
    if (amount <= 0) return;
    setCurrencyLoading(true);
    try {
      const res = await currencyAPI.convert({
        amount,
        from_currency: fromCurrency,
        to_currency: toCurrency
      });
      setConvertedResult(res.converted_amount);
      setExchangeRate(res.rate);
    } catch (err) {
      console.error('Lỗi chuyển đổi ngoại tệ:', err);
    } finally {
      setCurrencyLoading(false);
    }
  };

  useEffect(() => {
    handleConvert();
  }, [fromCurrency, toCurrency]);

  // --- Translation State ---
  const [textToTranslate, setTextToTranslate] = useState<string>('');
  const [targetLang, setTargetLang] = useState<string>('de');
  const [translatedText, setTranslatedText] = useState<string>('');
  const [translationLoading, setTranslationLoading] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);

  const quickPhrases = [
    { vi: 'Xin chào, bạn có nói tiếng Anh không?', de: 'Hallo, sprechen Sie Englisch?', ko: '안녕하세요, 영어 하실 수 있나요?', ja: 'こんにちは、英語を話せますか？' },
    { vi: 'Bao nhiêu tiền một đêm?', de: 'Wie viel kostet eine Nacht?', ko: '하룻밤에 얼마인가요?', ja: '一泊いくらですか？' },
    { vi: 'Cho tôi xem thực đơn được không?', de: 'Kann ich die Speisekarte sehen?', ko: '메뉴판 좀 볼 수 있을까요?', ja: 'メニューを見せてもらえますか？' },
    { vi: 'Làm ơn chỉ đường tới ga tàu gần nhất', de: 'Bitte zeigen Sie mir den Weg zum nächsten Bahnhof', ko: '가장 가까운 기차역으로 가는 길을 알려주세요', ja: '最寄りの駅への道を教えてください' },
    { vi: 'Tôi cần giúp đỡ khẩn cấp!', de: 'Ich brauche dringend Hilfe!', ko: '긴급한 도움이 필요합니다!', ja: '緊急の助けが必要です！' },
    { vi: 'Xin tính tiền / Làm ơn đưa hóa đơn', de: 'Die Rechnung, bitte', ko: '계산서 부탁드립니다', ja: 'お会計をお願いします' }
  ];

  const handleTranslate = async (textOverride?: string) => {
    const text = textOverride || textToTranslate;
    if (!text.trim()) return;
    setTranslationLoading(true);
    try {
      const res = await translationAPI.translate(text, targetLang, 'vi');
      setTranslatedText(res.translated_text);
    } catch (err) {
      console.error('Lỗi dịch thuật:', err);
    } finally {
      setTranslationLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // --- Bookings State ---
  const [bookings, setBookings] = useState<BookingItem[]>([]);
  const [bookingsLoading, setBookingsLoading] = useState<boolean>(false);
  const [bookingFilter, setBookingFilter] = useState<string>('ALL');

  const fetchBookings = async () => {
    setBookingsLoading(true);
    try {
      const data = await bookingsAPI.list();
      setBookings(data || []);
    } catch (err) {
      console.error('Lỗi tải danh sách bookings:', err);
    } finally {
      setBookingsLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'bookings') {
      fetchBookings();
    }
  }, [activeTab]);

  const handleConfirmBooking = async (id: number) => {
    try {
      await bookingsAPI.confirm(id);
      fetchBookings();
      if (onBookingUpdated) onBookingUpdated();
    } catch (err) {
      alert('Không thể xác nhận đặt chỗ. Vui lòng thử lại.');
    }
  };

  const handleCancelBooking = async (id: number) => {
    if (!confirm('Bạn có chắc chắn muốn hủy dịch vụ này?')) return;
    try {
      await bookingsAPI.cancel(id);
      fetchBookings();
      if (onBookingUpdated) onBookingUpdated();
    } catch (err) {
      alert('Không thể hủy đặt chỗ. Vui lòng thử lại.');
    }
  };

  // --- In-Trip Support State ---
  const [inTripQuery, setInTripQuery] = useState('');
  const [inTripAnswer, setInTripAnswer] = useState('');
  const [inTripLoading, setInTripLoading] = useState(false);

  const handleAskInTrip = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inTripQuery.trim() || inTripLoading) return;
    setInTripLoading(true);
    try {
      const res = await askInTripSupport(tripId, inTripQuery);
      setInTripAnswer(res.agent_response);
    } catch (err) {
      setInTripAnswer('Rất tiếc, đã có lỗi kết nối trợ lý hành trình. Hãy thử lại.');
    } finally {
      setInTripLoading(false);
    }
  };

  const filteredBookings = bookings.filter((b) => {
    if (bookingFilter === 'ALL') return true;
    return b.status === bookingFilter;
  });

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden flex flex-col h-[750px]">
      {/* Header Tabs */}
      <div className="bg-slate-900 text-white p-3 border-b border-slate-800">
        <div className="flex items-center space-x-2 mb-2 px-1">
          <Sparkles className="w-4 h-4 text-amber-400" />
          <h2 className="font-bold text-sm tracking-wide uppercase text-slate-200">
            Travel Utilities Hub
          </h2>
          <span className="text-[10px] bg-sky-500/20 text-sky-300 border border-sky-400/30 px-2 py-0.5 rounded-full font-medium">
            Toàn Cầu 24/7
          </span>
        </div>

        {/* Tab Switchers */}
        <div className="grid grid-cols-4 gap-1 bg-slate-800/80 p-1 rounded-xl text-xs font-semibold">
          <button
            onClick={() => setActiveTab('currency')}
            className={`py-2 px-1 rounded-lg flex items-center justify-center space-x-1 transition ${
              activeTab === 'currency'
                ? 'bg-sky-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
            }`}
          >
            <DollarSign className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Tỷ Giá</span>
          </button>

          <button
            onClick={() => setActiveTab('translation')}
            className={`py-2 px-1 rounded-lg flex items-center justify-center space-x-1 transition ${
              activeTab === 'translation'
                ? 'bg-sky-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
            }`}
          >
            <Languages className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Dịch</span>
          </button>

          <button
            onClick={() => setActiveTab('bookings')}
            className={`py-2 px-1 rounded-lg flex items-center justify-center space-x-1 transition relative ${
              activeTab === 'bookings'
                ? 'bg-sky-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
            }`}
          >
            <CalendarCheck className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Đặt Chỗ</span>
            {bookings.some((b) => b.status === 'PENDING') && (
              <span className="w-2 h-2 rounded-full bg-amber-400 absolute top-1.5 right-1.5 animate-ping" />
            )}
          </button>

          <button
            onClick={() => setActiveTab('intrip')}
            className={`py-2 px-1 rounded-lg flex items-center justify-center space-x-1 transition ${
              activeTab === 'intrip'
                ? 'bg-sky-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
            }`}
          >
            <LifeBuoy className="w-3.5 h-3.5 text-amber-300" />
            <span className="hidden sm:inline">In-Trip</span>
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-4 bg-slate-50/50">
        {/* ================= TAB 1: CURRENCY ================= */}
        {activeTab === 'currency' && (
          <div className="space-y-4">
            <div className="bg-gradient-to-br from-sky-50 to-indigo-50 border border-sky-100 rounded-xl p-4">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-700 mb-2">
                <span>Tỷ giá thực tế (Frankfurter API)</span>
                <span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full text-[10px]">
                  Cập nhật thời gian thực
                </span>
              </div>
              {exchangeRate && (
                <div className="text-sm font-bold text-sky-900">
                  1 {fromCurrency} ≈ {exchangeRate.toLocaleString()} {toCurrency}
                </div>
              )}
            </div>

            <div className="space-y-3 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Số tiền</label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(Number(e.target.value))}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-sm font-semibold focus:ring-2 focus:ring-sky-500 focus:outline-none"
                  min="1"
                />
              </div>

              <div className="grid grid-cols-2 gap-3 items-center">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Từ tiền tệ</label>
                  <select
                    value={fromCurrency}
                    onChange={(e) => setFromCurrency(e.target.value)}
                    className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:ring-2 focus:ring-sky-500 focus:outline-none bg-slate-50"
                  >
                    <option value="EUR">EUR - Euro (Châu Âu / Áo / Pháp / Đức)</option>
                    <option value="CHF">CHF - Franc Thụy Sĩ (Zermatt)</option>
                    <option value="KRW">KRW - Won Hàn Quốc (Seoul)</option>
                    <option value="JPY">JPY - Yên Nhật (Tokyo)</option>
                    <option value="USD">USD - Đô la Mỹ</option>
                    <option value="VND">VND - Đồng Việt Nam (Sa Pa / Hà Nội)</option>
                    <option value="GBP">GBP - Bảng Anh</option>
                    <option value="THB">THB - Baht Thái Lan</option>
                    <option value="SGD">SGD - Đô la Singapore</option>
                    <option value="AUD">AUD - Đô la Úc</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Sang tiền tệ</label>
                  <select
                    value={toCurrency}
                    onChange={(e) => setToCurrency(e.target.value)}
                    className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:ring-2 focus:ring-sky-500 focus:outline-none bg-slate-50"
                  >
                    <option value="VND">VND - Đồng Việt Nam</option>
                    <option value="USD">USD - Đô la Mỹ</option>
                    <option value="EUR">EUR - Euro</option>
                    <option value="CHF">CHF - Franc Thụy Sĩ</option>
                    <option value="KRW">KRW - Won Hàn Quốc</option>
                    <option value="JPY">JPY - Yên Nhật</option>
                  </select>
                </div>
              </div>

              <button
                onClick={handleConvert}
                disabled={currencyLoading}
                className="w-full bg-sky-600 hover:bg-sky-700 text-white py-2.5 rounded-xl font-medium text-xs flex items-center justify-center space-x-1.5 transition shadow-sm"
              >
                {currencyLoading ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <ArrowRightLeft className="w-3.5 h-3.5" />
                )}
                <span>Tính Toán Quy Đổi</span>
              </button>
            </div>

            {convertedResult !== null && (
              <div className="bg-emerald-50 border border-emerald-200 p-4 rounded-xl text-center">
                <span className="text-xs text-emerald-700 font-medium block">Kết quả chuyển đổi:</span>
                <span className="text-xl font-extrabold text-emerald-900 mt-1 block">
                  {convertedResult.toLocaleString()} {toCurrency}
                </span>
                <span className="text-[11px] text-emerald-600 mt-1 block">
                  (Dành cho chi tiêu ăn uống, vé tham quan & mua sắm tại điểm đến)
                </span>
              </div>
            )}
          </div>
        )}

        {/* ================= TAB 2: TRANSLATION ================= */}
        {activeTab === 'translation' && (
          <div className="space-y-4">
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-slate-700">Ngôn ngữ điểm đến:</label>
                <select
                  value={targetLang}
                  onChange={(e) => setTargetLang(e.target.value)}
                  className="border border-slate-300 rounded-lg px-2.5 py-1 text-xs font-medium bg-slate-50 focus:outline-none"
                >
                  <option value="de">Tiếng Đức (Áo / Thụy Sĩ / Hallstatt)</option>
                  <option value="ko">Tiếng Hàn (Hàn Quốc / Seoul)</option>
                  <option value="ja">Tiếng Nhật (Nhật Bản / Tokyo)</option>
                  <option value="en">Tiếng Anh (Quốc tế / Toàn cầu)</option>
                  <option value="fr">Tiếng Pháp (Pháp / Paris / Zermatt)</option>
                  <option value="it">Tiếng Ý (Ý / Rome / Venice)</option>
                  <option value="es">Tiếng Tây Ban Nha (Tây Ban Nha)</option>
                  <option value="vi">Tiếng Việt (Việt Nam / Sa Pa)</option>
                </select>
              </div>

              <div>
                <textarea
                  value={textToTranslate}
                  onChange={(e) => setTextToTranslate(e.target.value)}
                  placeholder="Nhập câu tiếng Việt bạn muốn nói..."
                  className="w-full border border-slate-300 rounded-xl p-3 text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none h-20"
                />
              </div>

              <button
                onClick={() => handleTranslate()}
                disabled={translationLoading || !textToTranslate.trim()}
                className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white py-2 rounded-xl text-xs font-semibold flex items-center justify-center space-x-1.5 transition"
              >
                {translationLoading ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Languages className="w-3.5 h-3.5" />
                )}
                <span>Dịch Ngay (Smart Local Translation)</span>
              </button>

              {translatedText && (
                <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-3 relative">
                  <span className="text-[10px] font-bold text-indigo-700 uppercase tracking-wider block mb-1">
                    Bản Dịch:
                  </span>
                  <p className="text-sm font-semibold text-slate-800 pr-8">{translatedText}</p>
                  <button
                    onClick={() => copyToClipboard(translatedText)}
                    className="absolute top-2.5 right-2.5 text-indigo-600 hover:text-indigo-800 p-1"
                    title="Sao chép"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  {copied && (
                    <span className="text-[10px] text-indigo-600 absolute bottom-1 right-2 font-medium">
                      Đã chép!
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* Quick Phrases */}
            <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
              <span className="text-xs font-bold text-slate-700 block mb-2">
                Mẫu câu giao tiếp thông dụng:
              </span>
              <div className="space-y-1.5">
                {quickPhrases.map((phrase, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setTextToTranslate(phrase.vi);
                      handleTranslate(phrase.vi);
                    }}
                    className="w-full text-left p-2 rounded-lg bg-slate-50 hover:bg-sky-50 hover:text-sky-700 border border-slate-200 text-[11px] text-slate-700 transition"
                  >
                    • {phrase.vi}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ================= TAB 3: BOOKINGS ================= */}
        {activeTab === 'bookings' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex space-x-1 text-xs">
                {['ALL', 'PENDING', 'CONFIRMED', 'CANCELLED'].map((st) => (
                  <button
                    key={st}
                    onClick={() => setBookingFilter(st)}
                    className={`px-2 py-1 rounded-md text-[11px] font-semibold transition ${
                      bookingFilter === st
                        ? 'bg-slate-800 text-white'
                        : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    {st === 'ALL' ? 'Tất cả' : st}
                  </button>
                ))}
              </div>
              <button
                onClick={fetchBookings}
                className="text-slate-500 hover:text-slate-800 p-1"
                title="Làm mới"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${bookingsLoading ? 'animate-spin' : ''}`} />
              </button>
            </div>

            {filteredBookings.length === 0 ? (
              <div className="bg-white p-6 text-center rounded-xl border border-slate-200 text-xs text-slate-500">
                Chưa có dịch vụ nào trong danh sách. Khi AI gợi ý vé bay, khách sạn hoặc tour, booking sẽ hiển thị tại đây để bạn xác nhận!
              </div>
            ) : (
              <div className="space-y-2.5">
                {filteredBookings.map((b) => (
                  <div
                    key={b.id}
                    className="bg-white p-3 rounded-xl border border-slate-200 shadow-sm space-y-2"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="text-[10px] font-mono font-bold text-sky-700 bg-sky-50 px-1.5 py-0.5 rounded border border-sky-200">
                          {b.booking_reference}
                        </span>
                        <h4 className="font-bold text-xs text-slate-900 mt-1">{b.service_name}</h4>
                      </div>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          b.status === 'CONFIRMED'
                            ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                            : b.status === 'CANCELLED'
                            ? 'bg-rose-100 text-rose-800 border border-rose-300'
                            : 'bg-amber-100 text-amber-800 border border-amber-300 animate-pulse'
                        }`}
                      >
                        {b.status}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-xs text-slate-600 pt-1 border-t border-slate-100">
                      <span className="font-semibold text-emerald-600">
                        {b.price?.toLocaleString()} VND
                      </span>
                      <span className="text-[10px] text-slate-400 capitalize">{b.category}</span>
                    </div>

                    {/* Actions: Human-in-the-loop */}
                    <div className="flex items-center space-x-2 pt-1">
                      {b.status === 'PENDING' && (
                        <button
                          onClick={() => handleConfirmBooking(b.id)}
                          className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white py-1 rounded-lg text-xs font-semibold flex items-center justify-center space-x-1"
                        >
                          <CheckCircle className="w-3.5 h-3.5" />
                          <span>Xác Nhận Đặt</span>
                        </button>
                      )}
                      {b.status !== 'CANCELLED' && (
                        <button
                          onClick={() => handleCancelBooking(b.id)}
                          className="flex-1 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 py-1 rounded-lg text-xs font-semibold flex items-center justify-center space-x-1"
                        >
                          <XCircle className="w-3.5 h-3.5" />
                          <span>Hủy</span>
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ================= TAB 4: IN-TRIP & SOS ================= */}
        {activeTab === 'intrip' && (
          <div className="space-y-4">
            <div className="bg-gradient-to-br from-indigo-900 to-slate-900 text-white p-4 rounded-xl shadow border border-indigo-700/50">
              <div className="flex items-center space-x-2 mb-2">
                <LifeBuoy className="w-4 h-4 text-amber-400" />
                <h4 className="font-bold text-xs tracking-wide">Trợ Lý Hành Trình Thời Gian Thực</h4>
              </div>
              <p className="text-[11px] text-indigo-200 leading-relaxed mb-3">
                Đặt câu hỏi về thời tiết, tìm quán ăn gần vị trí hiện tại hoặc xử lý tình huống phát sinh:
              </p>

              <form onSubmit={handleAskInTrip} className="space-y-2">
                <input
                  type="text"
                  value={inTripQuery}
                  onChange={(e) => setInTripQuery(e.target.value)}
                  placeholder="VD: Quán cà phê view đẹp gần đây?..."
                  className="w-full bg-white/10 border border-indigo-400/30 rounded-xl px-3 py-2 text-xs placeholder-indigo-300 text-white focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
                <button
                  type="submit"
                  disabled={inTripLoading}
                  className="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-1.5 rounded-xl font-medium text-xs flex items-center justify-center space-x-1"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Hỏi Trợ Lý AI</span>
                </button>
              </form>

              {inTripAnswer && (
                <div className="mt-3 bg-white/10 border border-indigo-400/20 p-3 rounded-xl text-xs leading-relaxed text-indigo-100">
                  {inTripAnswer}
                </div>
              )}
            </div>

            {/* Emergency SOS Hotlines */}
            <div className="bg-rose-50 border border-rose-200 rounded-xl p-4">
              <div className="flex items-center space-x-2 text-rose-800 font-bold text-xs mb-2">
                <ShieldAlert className="w-4 h-4 text-rose-600" />
                <span>Đường Dây Nóng Khẩn Cấp (Emergency SOS)</span>
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between bg-white p-2 rounded-lg border border-rose-100">
                  <span className="font-medium text-slate-700">Khẩn cấp quốc tế (EU / Châu Âu)</span>
                  <span className="font-bold text-rose-600 font-mono">112</span>
                </div>
                <div className="flex items-center justify-between bg-white p-2 rounded-lg border border-rose-100">
                  <span className="font-medium text-slate-700">Cảnh sát & Cứu hỏa</span>
                  <span className="font-bold text-rose-600 font-mono">110 / 113 / 911</span>
                </div>
                <div className="flex items-center justify-between bg-white p-2 rounded-lg border border-rose-100">
                  <span className="font-medium text-slate-700">Bảo hộ công dân Việt Nam</span>
                  <span className="font-bold text-rose-600 font-mono">+84 981 84 84 84</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
