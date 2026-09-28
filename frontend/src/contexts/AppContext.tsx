'use client';
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
export interface UserPreferences {
  travelStyle: string[];
  dietaryRestrictions: string[];
  accommodationPreference: string;
  budgetRange: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  avatar_url?: string;
  preferences?: UserPreferences;
}

export interface AppContextType {
  // Language
  language: string;
  setLanguage: (lang: string) => void;
  // Currency
  currency: string;
  setCurrency: (cur: string) => void;
  // Theme
  darkMode: boolean;
  toggleDarkMode: () => void;
  // Auth
  user: User | null;
  setUser: (user: User | null) => void;
  isAuthenticated: boolean;
  logout: () => void;
  // Loading
  isLoading: boolean;
  setIsLoading: (v: boolean) => void;
}

// ---------------------------------------------------------------------------
// Translations (mini i18n)
// ---------------------------------------------------------------------------
export const translations: Record<string, Record<string, string>> = {
  vi: {
    planTrip: 'Lập Lịch Trình',
    findFlight: 'Tìm Chuyến Bay',
    findHotel: 'Tìm Khách Sạn',
    convertCurrency: 'Đổi Tiền',
    translate: 'Dịch Thuật',
    sendMessage: 'Gửi',
    typeMessage: 'Nhập tin nhắn...',
    myTrips: 'Chuyến đi của tôi',
    destinations: 'Điểm đến',
    aiAssistant: 'Trợ lý AI',
    profile: 'Hồ sơ',
    logout: 'Đăng xuất',
    settings: 'Cài đặt',
    exportPDF: 'Xuất PDF',
    totalCost: 'Tổng chi phí',
    loading: 'Đang tải...',
    noTrips: 'Chưa có chuyến đi nào',
    startPlanning: 'Bắt đầu lập kế hoạch',
    exchangeRates: 'Tỷ giá hối đoái',
    flightOptions: 'Tùy chọn chuyến bay',
    hotelOptions: 'Tùy chọn khách sạn',
    suggestions: 'Gợi ý',
    tripVersions: 'Phiên bản lịch trình',
    itinerary: 'Lịch trình',
    budget: 'Ngân sách',
    days: 'ngày',
    edit: 'Sửa',
    delete: 'Xóa',
    save: 'Lưu',
    cancel: 'Hủy',
    confirm: 'Xác nhận',
    share: 'Chia sẻ',
    welcome: 'Xin chào! Tôi là trợ lý du lịch AI của bạn.',
    welcomeSub: 'Hãy cho tôi biết bạn muốn đi đâu và tôi sẽ lập kế hoạch hoàn hảo cho bạn!',
  },
  en: {
    planTrip: 'Plan a Trip',
    findFlight: 'Find Flights',
    findHotel: 'Find Hotels',
    convertCurrency: 'Convert Currency',
    translate: 'Translate',
    sendMessage: 'Send',
    typeMessage: 'Type a message...',
    myTrips: 'My Trips',
    destinations: 'Destinations',
    aiAssistant: 'AI Assistant',
    profile: 'Profile',
    logout: 'Logout',
    settings: 'Settings',
    exportPDF: 'Export PDF',
    totalCost: 'Total Cost',
    loading: 'Loading...',
    noTrips: 'No trips yet',
    startPlanning: 'Start Planning',
    exchangeRates: 'Exchange Rates',
    flightOptions: 'Flight Options',
    hotelOptions: 'Hotel Options',
    suggestions: 'Suggestions',
    tripVersions: 'Trip Versions',
    itinerary: 'Itinerary',
    budget: 'Budget',
    days: 'days',
    edit: 'Edit',
    delete: 'Delete',
    save: 'Save',
    cancel: 'Cancel',
    confirm: 'Confirm',
    share: 'Share',
    welcome: 'Hello! I am your AI travel assistant.',
    welcomeSub: "Tell me where you'd like to go and I'll craft the perfect plan for you!",
  },
  ko: {
    planTrip: '여행 계획',
    findFlight: '항공편 찾기',
    findHotel: '호텔 찾기',
    convertCurrency: '환전',
    translate: '번역',
    sendMessage: '보내기',
    typeMessage: '메시지를 입력하세요...',
    myTrips: '내 여행',
    destinations: '목적지',
    aiAssistant: 'AI 어시스턴트',
    profile: '프로필',
    logout: '로그아웃',
    settings: '설정',
    exportPDF: 'PDF 내보내기',
    totalCost: '총 비용',
    loading: '로딩 중...',
    noTrips: '여행이 없습니다',
    startPlanning: '계획 시작',
    exchangeRates: '환율',
    flightOptions: '항공편 옵션',
    hotelOptions: '호텔 옵션',
    suggestions: '제안',
    tripVersions: '여행 버전',
    itinerary: '일정',
    budget: '예산',
    days: '일',
    edit: '편집',
    delete: '삭제',
    save: '저장',
    cancel: '취소',
    confirm: '확인',
    share: '공유',
    welcome: '안녕하세요! 저는 AI 여행 도우미입니다.',
    welcomeSub: '어디로 가고 싶은지 알려주시면 완벽한 계획을 세워드리겠습니다!',
  },
  ja: {
    planTrip: '旅行計画',
    findFlight: 'フライト検索',
    findHotel: 'ホテル検索',
    convertCurrency: '通貨換算',
    translate: '翻訳',
    sendMessage: '送信',
    typeMessage: 'メッセージを入力...',
    myTrips: '私の旅行',
    destinations: '目的地',
    aiAssistant: 'AIアシスタント',
    profile: 'プロフィール',
    logout: 'ログアウト',
    settings: '設定',
    exportPDF: 'PDFエクスポート',
    totalCost: '合計費用',
    loading: '読み込み中...',
    noTrips: '旅行がありません',
    startPlanning: '計画を始める',
    exchangeRates: '為替レート',
    flightOptions: 'フライトオプション',
    hotelOptions: 'ホテルオプション',
    suggestions: '提案',
    tripVersions: '旅行バージョン',
    itinerary: '旅程',
    budget: '予算',
    days: '日',
    edit: '編集',
    delete: '削除',
    save: '保存',
    cancel: 'キャンセル',
    confirm: '確認',
    share: '共有',
    welcome: 'こんにちは！AIトラベルアシスタントです。',
    welcomeSub: 'どこへ行きたいか教えていただければ、完璧なプランを作成します！',
  },
};

export const t = (lang: string, key: string): string => {
  return translations[lang]?.[key] ?? translations['en']?.[key] ?? key;
};

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------
export const AppContext = createContext<AppContextType>(null!);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState('vi');
  const [currency, setCurrencyState] = useState('VND');
  const [darkMode, setDarkMode] = useState(false);
  const [user, setUserState] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Hydrate from localStorage on mount
  useEffect(() => {
    try {
      const savedLang = localStorage.getItem('travel_language') || 'vi';
      const savedCur = localStorage.getItem('travel_currency') || 'VND';
      const savedDark = localStorage.getItem('travel_dark_mode') === 'true';
      const savedUser = localStorage.getItem('travel_user');

      setLanguageState(savedLang);
      setCurrencyState(savedCur);
      setDarkMode(savedDark);
      if (savedUser) {
        try { setUserState(JSON.parse(savedUser)); } catch {}
      }
    } catch {
      // localStorage not available (SSR guard)
    }
  }, []);

  // Sync dark mode class on <html>
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const setLanguage = useCallback((lang: string) => {
    setLanguageState(lang);
    try { localStorage.setItem('travel_language', lang); } catch {}
  }, []);

  const setCurrency = useCallback((cur: string) => {
    setCurrencyState(cur);
    try { localStorage.setItem('travel_currency', cur); } catch {}
  }, []);

  const toggleDarkMode = useCallback(() => {
    setDarkMode((prev) => {
      const next = !prev;
      try { localStorage.setItem('travel_dark_mode', String(next)); } catch {}
      return next;
    });
  }, []);

  const setUser = useCallback((u: User | null) => {
    setUserState(u);
    try {
      if (u) localStorage.setItem('travel_user', JSON.stringify(u));
      else localStorage.removeItem('travel_user');
    } catch {}
  }, []);

  const logout = useCallback(() => {
    setUserState(null);
    try {
      localStorage.removeItem('travel_user');
      localStorage.removeItem('access_token');
    } catch {}
  }, []);

  return (
    <AppContext.Provider
      value={{
        language,
        setLanguage,
        currency,
        setCurrency,
        darkMode,
        toggleDarkMode,
        user,
        setUser,
        isAuthenticated: !!user,
        logout,
        isLoading,
        setIsLoading,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export const useApp = () => useContext(AppContext);
export const useTranslation = () => {
  const { language } = useApp();
  return (key: string) => t(language, key);
};
