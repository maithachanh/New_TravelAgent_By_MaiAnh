'use client';

import React, { useState } from 'react';
import {
  Send,
  Sparkles,
  MapPin,
  DollarSign,
  Calendar,
  RefreshCw,
  FileDown,
  Globe2,
  Navigation,
  Compass,
  CheckCircle2,
  Plane
} from 'lucide-react';
import { planTripWithAI, exportTripPDF } from '@/lib/api';

interface Message {
  sender: 'user' | 'ai';
  text: string;
  data?: any;
}

export default function ChatAgent({ onItineraryGenerated }: { onItineraryGenerated?: (data: any) => void }) {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'ai',
      text: 'Xin chào! Tôi là Travel Agent AI toàn cầu. Bạn có thể yêu cầu đi BẤT KỲ quốc gia, thành phố hay ngôi làng nào trên thế giới (Ví dụ: Làng cổ Hallstatt Áo, Zermatt Thụy Sĩ, Seoul Hàn Quốc, Sa Pa Việt Nam, Tokyo Nhật Bản...). Tôi sẽ tự động geocoding vị trí, tra cứu tỷ giá ngoại tệ, tính khoảng cách và lập lịch trình chuẩn xác nhất cho bạn!',
    },
  ]);
  const [currentTripData, setCurrentTripData] = useState<any>(null);

  const samplePrompts = [
    {
      label: '🇦🇹 Làng Hallstatt (Áo)',
      text: 'Tôi muốn đi thăm làng cổ Hallstatt ở Áo 3 ngày 2 đêm, thích ngắm hồ thiên nhiên và ẩm thực địa phương, ngân sách 1,500 EUR cho 2 người'
    },
    {
      label: '🇨🇭 Núi Zermatt (Thụy Sĩ)',
      text: 'Lập kế hoạch du lịch Zermatt Thụy Sĩ 4 ngày 3 đêm ngắm đỉnh Matterhorn, thích trượt tuyết và đi tàu ngắm cảnh'
    },
    {
      label: '🇰🇷 Seoul (Hàn Quốc)',
      text: 'Tôi muốn đi Seoul Hàn Quốc 4 ngày 3 đêm cho 2 người từ Hà Nội, ngân sách 35 triệu VND, thích ẩm thực Myeongdong và mua sắm Hongdae'
    },
    {
      label: '🇻🇳 Sa Pa (Việt Nam)',
      text: 'Lập lịch trình khám phá bản Cát Cát và đỉnh Fansipan ở Sa Pa 3 ngày 2 đêm cho gia đình 2 người'
    },
    {
      label: '🇯🇵 Tokyo (Nhật Bản)',
      text: 'Gợi ý lịch trình du lịch Tokyo 5 ngày 4 đêm, trải nghiệm công nghệ Akihabara, ngắm tháp Tokyo và ẩm thực Shinjuku'
    },
    {
      label: '🇫🇷 Paris (Pháp)',
      text: 'Du lịch Paris Pháp 4 ngày 3 đêm, tham quan bảo tàng Louvre, tháp Eiffel và du thuyền sông Seine'
    }
  ];

  const handleSend = async (customPrompt?: string) => {
    const textToSend = customPrompt || prompt;
    if (!textToSend.trim() || loading) return;

    const newMessages: Message[] = [...messages, { sender: 'user', text: textToSend }];
    setMessages(newMessages);
    if (!customPrompt) setPrompt('');
    setLoading(true);
    setCurrentStep('Phân tích ngôn ngữ & Geocoding vị trí toàn cầu...');

    const stepTimer1 = setTimeout(() => {
      setCurrentStep('Tra cứu tỷ giá tiền tệ thực tế & sân bay gần nhất...');
    }, 1200);

    const stepTimer2 = setTimeout(() => {
      setCurrentStep('Chạy thuật toán tối ưu đa mục tiêu & lộ trình Haversine TSP...');
    }, 2500);

    try {
      const res = await planTripWithAI(textToSend);
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      setCurrentStep('');

      setMessages([
        ...newMessages,
        {
          sender: 'ai',
          text: res.agent_response || 'Đã tạo lịch trình thành công!',
          data: res,
        },
      ]);
      setCurrentTripData(res);
      if (onItineraryGenerated) onItineraryGenerated(res);
    } catch (err: any) {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      setCurrentStep('');
      setMessages([
        ...newMessages,
        {
          sender: 'ai',
          text: 'Rất tiếc, đã có lỗi kết nối tới AI Agent Server. Bạn vui lòng kiểm tra kết nối và thử lại!',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden flex flex-col h-[750px]">
      {/* Header */}
      <div className="bg-gradient-to-r from-sky-600 via-indigo-600 to-sky-700 text-white p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-white/10 rounded-xl backdrop-blur-sm border border-white/20">
            <Sparkles className="w-5 h-5 text-amber-300" />
          </div>
          <div>
            <h2 className="font-bold text-base sm:text-lg flex items-center space-x-2">
              <span>Universal Travel Agent</span>
              <span className="text-[10px] bg-sky-400/20 text-sky-200 px-2 py-0.5 rounded-full border border-sky-300/30">
                14-Stage DAG
              </span>
            </h2>
            <p className="text-xs text-sky-100 flex items-center space-x-1">
              <Globe2 className="w-3.5 h-3.5" />
              <span>Hỗ trợ mọi ngôi làng, thành phố trên toàn thế giới</span>
            </p>
          </div>
        </div>

        {currentTripData?.trip_id && (
          <button
            onClick={() => exportTripPDF(currentTripData.trip_id)}
            className="flex items-center space-x-1 bg-white/20 hover:bg-white/30 text-xs px-3 py-1.5 rounded-lg transition font-medium border border-white/30"
          >
            <FileDown className="w-4 h-4" />
            <span>Xuất PDF</span>
          </button>
        )}
      </div>

      {/* Suggested Destination Prompts */}
      <div className="p-2.5 bg-slate-50 border-b border-slate-200 flex items-center space-x-2 overflow-x-auto text-xs no-scrollbar">
        <span className="font-bold text-slate-500 shrink-0 flex items-center space-x-1">
          <Compass className="w-3.5 h-3.5 text-sky-600" />
          <span>Gợi ý:</span>
        </span>
        {samplePrompts.map((p, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(p.text)}
            className="shrink-0 bg-white border border-slate-200 hover:border-sky-500 hover:text-sky-600 hover:bg-sky-50/50 text-slate-700 px-3 py-1 rounded-full transition shadow-sm font-medium"
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[90%] rounded-2xl p-4 shadow-sm ${
                msg.sender === 'user'
                  ? 'bg-sky-600 text-white rounded-br-none'
                  : 'bg-slate-100 text-slate-800 rounded-bl-none border border-slate-200'
              }`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-line">{msg.text}</p>

              {/* Render Destination & Route Summary Card */}
              {msg.data?.destination_analysis && (
                <div className="mt-3 pt-3 border-t border-slate-200/80 bg-white text-slate-900 rounded-xl p-3 shadow-inner">
                  <div className="flex items-center justify-between text-xs font-bold text-sky-800 mb-2">
                    <span className="flex items-center space-x-1">
                      <MapPin className="w-3.5 h-3.5 text-rose-500" />
                      <span>{msg.data.destination || msg.data.destination_analysis?.city_or_village}</span>
                    </span>
                    <span className="text-emerald-700 font-extrabold flex items-center space-x-0.5">
                      <DollarSign className="w-3.5 h-3.5 text-emerald-600" />
                      <span>{msg.data.total_cost?.toLocaleString()} VND</span>
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-600 mb-3 bg-slate-50 p-2 rounded-lg border border-slate-200">
                    <div>
                      <span className="font-semibold text-slate-700">Sân bay lân cận:</span>{' '}
                      <span className="font-mono text-sky-700">
                        {msg.data.destination_analysis?.nearest_airport?.iata || 'N/A'} (
                        {msg.data.destination_analysis?.nearest_airport?.distance_km}km)
                      </span>
                    </div>
                    <div>
                      <span className="font-semibold text-slate-700">Tiền tệ:</span>{' '}
                      <span className="font-mono text-emerald-700">
                        {msg.data.destination_analysis?.currency || 'EUR'}
                      </span>
                    </div>
                  </div>

                  {/* Days snapshot */}
                  <div className="space-y-1.5">
                    {msg.data.itinerary?.map((day: any, dIdx: number) => (
                      <div key={dIdx} className="bg-slate-50 p-2 rounded-lg border border-slate-200 text-xs">
                        <div className="font-bold text-slate-800 flex items-center justify-between">
                          <span className="flex items-center space-x-1">
                            <Calendar className="w-3 h-3 text-sky-500" />
                            <span>Ngày {day.day_number} ({day.date})</span>
                          </span>
                          <span className="text-[10px] text-slate-500">{day.items?.length || 0} hoạt động</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading / Pipeline status */}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-sky-200 shadow-md text-slate-700 rounded-2xl rounded-bl-none p-4 max-w-[85%] space-y-2">
              <div className="flex items-center space-x-2 text-sm font-semibold text-sky-700">
                <RefreshCw className="w-4 h-4 animate-spin text-sky-600" />
                <span>LangGraph AI Pipeline đang xử lý...</span>
              </div>
              <p className="text-xs text-slate-500 italic pl-6">{currentStep}</p>
            </div>
          </div>
        )}
      </div>

      {/* Input Form */}
      <div className="p-3 bg-white border-t border-slate-200">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center space-x-2"
        >
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ví dụ: Đi làng Hallstatt 3 ngày, Zermatt tuyết, Seoul ăn vặt..."
            className="flex-1 border border-slate-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500 shadow-sm"
          />
          <button
            type="submit"
            disabled={loading || !prompt.trim()}
            className="bg-sky-600 hover:bg-sky-700 disabled:opacity-50 text-white font-medium px-5 py-2.5 rounded-xl flex items-center space-x-1.5 transition shadow-sm"
          >
            <Send className="w-4 h-4" />
            <span>Lập Tour</span>
          </button>
        </form>
      </div>
    </div>
  );
}
