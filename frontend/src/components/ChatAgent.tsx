'use client';

import React, { useEffect, useRef, useState } from 'react';
import {
  Calendar, Compass, FileDown, Globe2, LoaderCircle, MapPin,
  Plane, Send, Sparkles, WalletCards,
} from 'lucide-react';
import { exportTripPDF, planTripWithAI, askInTripSupport } from '@/lib/api';

interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  data?: any;
}

const suggestions = [
  { label: 'Hallstatt', text: 'Lên lịch Hallstatt, Áo 3 ngày 2 đêm cho 2 người, ngân sách 1.500 EUR, thích hồ và ẩm thực địa phương.' },
  { label: 'Seoul', text: 'Đi Seoul 4 ngày 3 đêm cho 2 người từ Hà Nội, ngân sách 35 triệu VND, thích ẩm thực và mua sắm.' },
  { label: 'Đà Nẵng', text: 'Lập kế hoạch Đà Nẵng 3 ngày 2 đêm cho gia đình 4 người, ngân sách 18 triệu, thích biển và đồ ăn.' },
];

interface ChatAgentProps {
  onItineraryGenerated?: (data: any) => void;
  externalPrompt?: string;
  onPromptConsumed?: () => void;
}

export default function ChatAgent({
  onItineraryGenerated,
  externalPrompt,
  onPromptConsumed
}: ChatAgentProps) {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState('Đang phân tích yêu cầu của bạn…');
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'ai',
      text: 'Chào bạn! Mình sẽ giúp bạn tạo lịch trình rõ ràng, phù hợp ngân sách và sở thích. Hãy cho mình biết điểm đến, số ngày, số người và ngân sách.',
    },
  ]);
  const [currentTripData, setCurrentTripData] = useState<any>(null);
  const requestIdRef = useRef(0);
  const abortRef = useRef<AbortController | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, loading]);

  useEffect(() => () => abortRef.current?.abort(), []);

  useEffect(() => {
    if (externalPrompt && externalPrompt.trim()) {
      setPrompt(externalPrompt);
      void handleSend(externalPrompt);
      onPromptConsumed?.();
    }
  }, [externalPrompt]);

  const appendMessage = (message: Message) => setMessages((previous) => [...previous, message]);

  const handleSend = async (textOverride?: string) => {
    const text = (textOverride ?? prompt).trim();
    if (!text || loading) return;

    const requestId = ++requestIdRef.current;
    const controller = new AbortController();
    abortRef.current?.abort();
    abortRef.current = controller;

    appendMessage({ id: `user-${requestId}`, sender: 'user', text });
    setPrompt('');
    setLoading(true);
    setCurrentStep('Đang phân tích điểm đến, thời gian và ngân sách…');

    const progressTimer = window.setTimeout(() => {
      if (requestIdRef.current === requestId) {
        setCurrentStep('Đang tối ưu lịch trình và kiểm tra chi phí…');
      }
    }, 1200);

    try {
      // Check if this is a support inquiry (not a request to plan a completely new tour)
      const hasNewTripIntent = /(lập tour|lên tour|lên lịch|tạo tour|kế hoạch mới|đi du lịch mới|chuyến đi mới|tour mới|hành trình mới|lên kế hoạch)/i.test(text);
      const isSupportInquiry = /(thời tiết|trời mưa|nhiệt độ|ăn gì|quán ăn|nhà hàng|đặc sản|đi lại|xe buýt|bus|tàu|taxi|sân bay|tiền|tỷ giá|đổi tiền|dịch|tiếng|an toàn|khẩn cấp|bệnh viện|thuốc|cho mình hỏi|bạn ơi|ở đâu|chỉ đường|review|gợi ý thêm|mấy giờ)/i.test(text);

      const isSupportQuestion = currentTripData?.trip_id && isSupportInquiry && !hasNewTripIntent;

      if (isSupportQuestion) {
        // For support questions, answer directly without destroying active itinerary
        const supportResponse = await askInTripSupport(currentTripData.trip_id, text);
        appendMessage({
          id: `ai-${requestId}`,
          sender: 'ai',
          text: supportResponse.agent_response || 'Câu trả lời của trợ lý hành trình.',
        });
      } else {
        // For new trip requests, run trip planner
        const result = await planTripWithAI(text, 'vi', 'VND', controller.signal);
        if (requestIdRef.current !== requestId) return;

        appendMessage({
          id: `ai-${requestId}`,
          sender: 'ai',
          text: result.agent_response || 'Mình đã hoàn tất đề xuất cho chuyến đi của bạn.',
          data: result,
        });

        // Only update active itinerary if itinerary is valid and non-empty
        if (result?.itinerary && Array.isArray(result.itinerary) && result.itinerary.length > 0) {
          setCurrentTripData(result);
          onItineraryGenerated?.(result);
        }
      }
    } catch (error: any) {
      if (error?.code === 'ERR_CANCELED' || requestIdRef.current !== requestId) return;
      const errorMsg = error?.response?.data?.detail || error?.message || 'Không thể kết nối tới Travel Agent lúc này. Hãy kiểm tra backend đang chạy tại cổng 8000 rồi thử lại.';
      setError(errorMsg);
      appendMessage({
        id: `error-${requestId}`,
        sender: 'ai',
        text: errorMsg,
      });
    } finally {
      window.clearTimeout(progressTimer);
      if (requestIdRef.current === requestId) {
        setLoading(false);
        setCurrentStep('');
      }
    }
  };

  return (
    <section className="panel-surface flex h-[720px] flex-col overflow-hidden">
      <div className="relative overflow-hidden bg-gradient-to-br from-sky-700 via-indigo-700 to-violet-800 px-5 py-4 text-white">
        <div className="absolute -right-7 -top-9 h-32 w-32 rounded-full bg-white/10 blur-2xl animate-pulse" />
        <div className="relative flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl border border-white/20 bg-white/15 p-2.5 shadow-lg backdrop-blur animate-pulse">
              <Sparkles className="h-5 w-5 text-amber-200" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-bold">Trợ lý lập kế hoạch</h2>
                <span className="rounded-full border border-emerald-200/30 bg-emerald-400/15 px-2 py-0.5 text-[10px] font-semibold text-emerald-100 animate-pulse">Sẵn sàng</span>
              </div>
              <p className="mt-0.5 flex items-center gap-1 text-xs text-sky-100"><Globe2 className="h-3.5 w-3.5" /> Lịch trình được kiểm tra theo yêu cầu của bạn</p>
            </div>
          </div>
          {currentTripData?.trip_id && (
            <button onClick={() => exportTripPDF(currentTripData.trip_id)} className="inline-flex items-center gap-1.5 rounded-xl border border-white/25 bg-white/10 px-3 py-2 text-xs font-semibold transition-all duration-200 hover:bg-white/20 hover:scale-105 active:scale-95">
              <FileDown className="h-3.5 w-3.5" /> PDF
            </button>
          )}
        </div>
      </div>

      <div className="flex gap-2 overflow-x-auto border-b border-slate-100 bg-slate-50/80 px-4 py-2.5 no-scrollbar">
        <span className="flex shrink-0 items-center gap-1 pt-1 text-xs font-semibold text-slate-500"><Compass className="h-3.5 w-3.5 text-sky-600" /> Gợi ý</span>
        {suggestions.map((suggestion) => (
          <button key={suggestion.label} disabled={loading} onClick={() => void handleSend(suggestion.text)} className="shrink-0 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 shadow-sm transition-all duration-200 hover:border-sky-300 hover:bg-sky-50 hover:text-sky-700 hover:scale-105 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:scale-100">
            {suggestion.label}
          </button>
        ))}
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto px-4 py-5" aria-live="polite">
        {messages.map((message, index) => (
          <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`} style={{ animationDelay: `${index * 50}ms` }}>
            <article className={`max-w-[92%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm transition-all duration-200 hover:shadow-md ${message.sender === 'user' ? 'rounded-br-md bg-gradient-to-br from-sky-600 to-indigo-600 text-white' : 'rounded-bl-md border border-slate-200 bg-white text-slate-700'}`}>
              <p className="whitespace-pre-line">{message.text}</p>
              {message.data?.destination_analysis && (
                <div className="mt-3 grid gap-2 border-t border-slate-200 pt-3 text-xs text-slate-600 sm:grid-cols-2">
                  <span className="flex items-center gap-1.5"><MapPin className="h-3.5 w-3.5 text-rose-500" /> {message.data.destination}</span>
                  <span className="flex items-center gap-1.5"><WalletCards className="h-3.5 w-3.5 text-emerald-600" /> {Number(message.data.total_cost || 0).toLocaleString('vi-VN')} VND</span>
                  <span className="flex items-center gap-1.5"><Plane className="h-3.5 w-3.5 text-sky-600" /> {message.data.destination_analysis?.nearest_airport?.iata || 'N/A'}</span>
                  <span className="flex items-center gap-1.5"><Calendar className="h-3.5 w-3.5 text-violet-600" /> {message.data.itinerary?.length || 0} ngày</span>
                </div>
              )}
            </article>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start animate-in fade-in duration-300">
            <div className="flex max-w-[88%] items-center gap-2 rounded-2xl rounded-bl-md border border-sky-100 bg-sky-50 px-4 py-3 text-xs font-medium text-sky-800">
              <LoaderCircle className="h-4 w-4 animate-spin" /> {currentStep}
            </div>
          </div>
        )}
        {error && (
          <div className="flex justify-start animate-in fade-in duration-300">
            <div className="flex max-w-[88%] items-center gap-2 rounded-2xl rounded-bl-md border border-rose-200 bg-rose-50 px-4 py-3 text-xs font-medium text-rose-800">
              {error}
              <button onClick={() => setError(null)} className="ml-2 text-rose-600 hover:text-rose-800 font-semibold">✕</button>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={(event) => { event.preventDefault(); void handleSend(); }} className="border-t border-slate-100 bg-white p-4">
        <label htmlFor="travel-prompt" className="mb-2 block text-xs font-semibold text-slate-600">Bạn muốn đi đâu?</label>
        <div className="flex items-end gap-2 rounded-2xl border border-slate-200 bg-slate-50 p-2 transition-all duration-200 focus-within:border-sky-400 focus-within:ring-4 focus-within:ring-sky-100 focus-within:shadow-md">
          <textarea
            id="travel-prompt"
            rows={4}
            maxLength={1000}
            value={prompt}
            disabled={loading}
            onChange={(event) => setPrompt(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                void handleSend();
              }
            }}
            placeholder="Ví dụ: Đi Kyoto 4 ngày cho 2 người, ngân sách 30 triệu, thích ẩm thực và văn hóa…"
            className="min-h-[96px] max-h-[150px] flex-1 resize-y bg-transparent px-2 py-1 text-sm leading-6 text-slate-800 outline-none placeholder:text-slate-400 disabled:cursor-not-allowed"
          />
          <button type="submit" disabled={loading || !prompt.trim()} aria-label="Gửi yêu cầu lập kế hoạch" className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-sky-600 to-indigo-600 text-white shadow-md transition-all duration-200 hover:brightness-110 hover:scale-105 active:scale-95 disabled:cursor-not-allowed disabled:opacity-45 disabled:hover:scale-100">
            <Send className="h-4 w-4" />
          </button>
        </div>
        <p className="mt-2 text-[11px] text-slate-400">Enter để gửi · Shift + Enter để xuống dòng</p>
      </form>
    </section>
  );
}
