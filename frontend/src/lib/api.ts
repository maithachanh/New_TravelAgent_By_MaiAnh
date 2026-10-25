import axios, { AxiosError } from 'axios';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// ---------------------------------------------------------------------------
// Axios instance
// ---------------------------------------------------------------------------
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// Older API records were written with a Windows code-page mismatch.  Repair
// only strings that exhibit the signature, keeping normal Unicode untouched.
const MOJIBAKE_PATTERN = /(?:Ã.|Â.|Ä.|Æ.|áº.|ðŸ)/;
const textDecoder = typeof TextDecoder !== 'undefined' ? new TextDecoder('utf-8', { fatal: true }) : null;

export const repairMojibake = (value: string): string => {
  if (!MOJIBAKE_PATTERN.test(value) || !textDecoder) return value;
  try {
    const bytes = Uint8Array.from(Array.from(value, (char) => char.charCodeAt(0)));
    return textDecoder.decode(bytes);
  } catch {
    return value;
  }
};

const repairApiPayload = (value: any): any => {
  if (typeof value === 'string') return repairMojibake(value);
  if (Array.isArray(value)) return value.map(repairApiPayload);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, repairApiPayload(item)]));
  }
  return value;
};

// Auth request interceptor
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Global error interceptor with retry logic
api.interceptors.response.use(
  (res) => {
    res.data = repairApiPayload(res.data);
    return res;
  },
  async (err: AxiosError) => {
    const originalRequest = err.config as any;
    const retryCount = originalRequest._retryCount || 0;
    const maxRetries = 3;

    // Retry on network errors or 5xx errors
    if (!err.response && retryCount < maxRetries) {
      originalRequest._retryCount = retryCount + 1;
      await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1)));
      return api(originalRequest);
    }

    if (err.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('travel_user');
      window.dispatchEvent(new Event('unauthorized'));
    }

    // Provide more descriptive error messages
    if (err.response?.status === 404) {
      err.message = 'API endpoint not found. Please check the backend service.';
    } else if (err.response?.status === 500) {
      err.message = 'Server error occurred. Please try again later.';
    } else if (err.code === 'ECONNABORTED') {
      err.message = 'Request timeout. Please check your connection and try again.';
    }

    return Promise.reject(err);
  },
);

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    email: string;
    full_name: string;
    avatar_url?: string;
  };
}

export interface PlanTripRequest {
  prompt: string;
  language?: string;
  currency?: string;
}

export interface ItineraryItem {
  id: string;
  type: 'flight' | 'hotel' | 'restaurant' | 'attraction' | 'transport' | 'activity';
  time: string;
  title: string;
  location: string;
  description?: string;
  cost: number;
  currency: string;
  duration?: string;
  booking_url?: string;
  image_url?: string;
  coordinates?: { lat: number; lng: number };
}

export interface ItineraryDay {
  day: number;
  date: string;
  city: string;
  items: ItineraryItem[];
  day_total: number;
}

export interface PlanTripResponse {
  trip_id: number;
  agent_response: string;
  extracted_requirements: {
    destination: string;
    origin?: string;
    start_date?: string;
    end_date?: string;
    duration_days?: number;
    budget?: number;
    currency?: string;
    travelers?: number;
    preferences?: string[];
  };
  itinerary: ItineraryDay[];
  total_cost: number;
  currency: string;
  needs_confirmation: boolean;
  version: number;
}

export interface AgentChatRequest {
  message: string;
  conversation_id?: number;
  trip_id?: number;
  language?: string;
  currency?: string;
}

export interface AgentChatResponse {
  response: string;
  conversation_id: number;
  tool_calls?: ToolCall[];
  updated_itinerary?: ItineraryDay[];
  suggestions?: string[];
}

export interface ToolCall {
  tool: string;
  status: 'running' | 'success' | 'error';
  result?: any;
  message?: string;
}

export interface CurrencyConvertRequest {
  amount: number;
  from_currency: string;
  to_currency: string;
}

export interface CurrencyConvertResponse {
  amount: number;
  from_currency: string;
  to_currency: string;
  converted_amount: number;
  rate: number;
  last_updated: string;
  source: string;
}

export interface FlightSearchRequest {
  origin: string;
  destination: string;
  departure_date: string;
  return_date?: string;
  adults?: number;
  cabin_class?: 'economy' | 'premium_economy' | 'business' | 'first';
  currency?: string;
}

export interface FlightOption {
  id: string;
  airline: string;
  airline_logo?: string;
  flight_number: string;
  departure_time: string;
  arrival_time: string;
  duration: string;
  stops: number;
  price: number;
  currency: string;
  cabin_class: string;
  available_seats?: number;
  booking_url?: string;
}

export interface HotelSearchRequest {
  city: string;
  country?: string;
  check_in: string;
  check_out: string;
  adults?: number;
  rooms?: number;
  max_price?: number;
  currency?: string;
  rating?: number;
}

export interface HotelOption {
  id: string;
  name: string;
  stars: number;
  rating: number;
  review_count: number;
  address: string;
  image_url?: string;
  price_per_night: number;
  total_price: number;
  currency: string;
  amenities: string[];
  booking_url?: string;
  coordinates?: { lat: number; lng: number };
}

export interface TripSummary {
  id: number;
  title: string;
  destination: string;
  start_date?: string;
  end_date?: string;
  status: 'draft' | 'confirmed' | 'completed' | 'cancelled';
  total_cost: number;
  currency: string;
  cover_image_url?: string;
  created_at: string;
  updated_at: string;
}

export interface TripDetail extends TripSummary {
  itinerary: ItineraryDay[];
  extracted_requirements: PlanTripResponse['extracted_requirements'];
  version: number;
  versions?: { version: number; created_at: string }[];
}

// ---------------------------------------------------------------------------
// Auth API
// ---------------------------------------------------------------------------
export const authAPI = {
  register: (data: RegisterRequest): Promise<LoginResponse> =>
    api.post('/auth/register', data).then((r) => r.data),

  login: (email: string, password: string): Promise<LoginResponse> =>
    api.post('/auth/login', { email, password }).then((r) => r.data),

  getMe: (): Promise<LoginResponse['user']> =>
    api.get('/auth/me').then((r) => r.data),

  updatePreferences: (data: Partial<{ preferences: Record<string, any> }>): Promise<any> =>
    api.put('/auth/me/preferences', data).then((r) => r.data),

  updateProfile: (data: Partial<{ full_name: string; avatar_url: string }>): Promise<any> =>
    api.put('/auth/me', data).then((r) => r.data),

  changePassword: (currentPassword: string, newPassword: string): Promise<any> =>
    api.post('/auth/change-password', { current_password: currentPassword, new_password: newPassword }).then((r) => r.data),
};

// ---------------------------------------------------------------------------
// AI Agent API
// ---------------------------------------------------------------------------
export const agentAPI = {
  chat: (req: AgentChatRequest): Promise<AgentChatResponse> =>
    api.post('/agent/plan-trip', { prompt: req.message, trip_id: req.trip_id }).then((r) => r.data),

  planTrip: (req: PlanTripRequest): Promise<PlanTripResponse> =>
    api.post('/agent/plan-trip', req).then((r) => r.data),

  modifyTrip: (tripId: number, modification: string, language?: string): Promise<PlanTripResponse> =>
    api.post('/agent/replan', { trip_id: tripId, modification, language }).then((r) => r.data),

  recommend: (query: string, city: string, country: string): Promise<{ recommendations: any[] }> =>
    api.post('/ai/recommend', { query, city, country }).then((r) => r.data),

  confirmBooking: (bookingId: number): Promise<{ success: boolean; message: string }> =>
    api.post(`/bookings/${bookingId}/confirm`).then((r) => r.data),
};

// ---------------------------------------------------------------------------

export interface TripMemberItem {
  id: number;
  user_id?: number;
  email: string;
  full_name?: string;
  role: 'OWNER' | 'EDITOR' | 'VIEWER' | string;
  status: string;
  is_owner: boolean;
  created_at?: string;
}

export interface TripExpenseItem {
  id: number;
  payer_name: string;
  title: string;
  category: string;
  amount: number;
  currency: string;
  split_members: string[];
  created_at?: string;
}

export interface DebtSettlementItem {
  from: string;
  to: string;
  amount: number;
  currency: string;
}

export interface TripExpensesResponse {
  trip_id: number;
  expenses: TripExpenseItem[];
  total_spent: number;
  balances: Record<string, number>;
  debt_settlements: DebtSettlementItem[];
}

export interface CheckoutResult {
  success: boolean;
  message: string;
  transaction_id: string;
  payment_method: string;
  total_amount: number;
  currency: string;
  paid_at: string;
  voucher_code: string;
  qr_code_url: string;
  confirmed_items_count: number;
  status: string;
}

// Trips API
// ---------------------------------------------------------------------------
export const tripsAPI = {
  list: (): Promise<TripSummary[]> =>
    api.get('/trips/').then((r) => r.data),

  get: (id: number): Promise<TripDetail> =>
    api.get(`/trips/${id}`).then((r) => r.data),

  create: (data: Partial<TripSummary>): Promise<TripDetail> =>
    api.post('/trips/', data).then((r) => r.data),

  update: (id: number, data: Partial<TripDetail>): Promise<TripDetail> =>
    api.put(`/trips/${id}`, data).then((r) => r.data),

  delete: (id: number): Promise<{ success: boolean }> =>
    api.delete(`/trips/${id}`).then((r) => r.data),

  exportPDF: (id: number): void => {
    if (typeof window !== 'undefined') {
      window.open(`${API_BASE_URL}/trips/${id}/pdf`, '_blank');
    }
  },

  getVersion: (id: number, version: number): Promise<TripDetail> =>
    api.get(`/trips/${id}/versions/${version}`).then((r) => r.data),

  reorderItem: (tripId: number, day: number, itemId: string, newIndex: number): Promise<TripDetail> =>
    api.patch(`/trips/${tripId}/reorder`, { day, item_id: itemId, new_index: newIndex }).then((r) => r.data),

  getMembers: (tripId: number): Promise<{ trip_id: number; members: TripMemberItem[] }> =>
    api.get(`/trips/${tripId}/members`).then((r) => r.data),

  inviteMember: (tripId: number, data: { email: string; full_name?: string; role?: string }): Promise<{ success: boolean; message: string; member: TripMemberItem }> =>
    api.post(`/trips/${tripId}/members`, data).then((r) => r.data),

  removeMember: (tripId: number, memberId: number): Promise<{ success: boolean; message: string }> =>
    api.delete(`/trips/${tripId}/members/${memberId}`).then((r) => r.data),

  getExpenses: (tripId: number): Promise<TripExpensesResponse> =>
    api.get(`/trips/${tripId}/expenses`).then((r) => r.data),

  createExpense: (tripId: number, data: { payer_name: string; title: string; category?: string; amount: number; currency?: string; split_members?: string[] }): Promise<{ success: boolean; message: string; expense: TripExpenseItem }> =>
    api.post(`/trips/${tripId}/expenses`, data).then((r) => r.data),

  deleteExpense: (tripId: number, expenseId: number): Promise<{ success: boolean; message: string }> =>
    api.delete(`/trips/${tripId}/expenses/${expenseId}`).then((r) => r.data),
};

// ---------------------------------------------------------------------------
// Search APIs
// ---------------------------------------------------------------------------
export const searchAPI = {
  flights: (req: FlightSearchRequest): Promise<{ offers: FlightOption[]; flights: FlightOption[]; count: number }> =>
    api.post('/flights/search', req).then((r) => {
      const data = r.data || {};
      const list = data.flights || data.offers || [];
      return { ...data, offers: list, flights: list, count: data.count || list.length };
    }),

  hotels: (req: HotelSearchRequest): Promise<{ accommodations: HotelOption[]; hotels: HotelOption[]; count: number }> =>
    api.post('/hotels/search', req).then((r) => {
      const data = r.data || {};
      const list = data.hotels || data.accommodations || [];
      return { ...data, accommodations: list, hotels: list, count: data.count || list.length };
    }),

  places: (req: { query: string; city: string; country?: string; type?: string }): Promise<{ places: any[] }> =>
    api.post('/places/search', req).then((r) => r.data),
};

// ---------------------------------------------------------------------------
// Currency API
// ---------------------------------------------------------------------------
export const currencyAPI = {
  convert: (req: CurrencyConvertRequest): Promise<CurrencyConvertResponse> =>
    api.post('/currency/convert', req).then((r) => r.data),

  rates: (base: string = 'VND'): Promise<{ base: string; rates: Record<string, number>; last_updated: string }> =>
    api.get('/currency/rates', { params: { base, base_currency: base } }).then((r) => r.data),
};

// ---------------------------------------------------------------------------
// Translation API
// ---------------------------------------------------------------------------
export const translationAPI = {
  translate: (text: string, targetLanguage: string, sourceLanguage?: string): Promise<{ translated_text: string; source_lang: string; target_lang: string; provider: string; success: boolean; error?: string }> =>
    api.post('/translation/translate', { text, target_lang: targetLanguage, source_lang: sourceLanguage }).then((r) => r.data),
};

// ---------------------------------------------------------------------------
// Bookings API (Human-in-the-Loop)
// ---------------------------------------------------------------------------
export interface BookingItem {
  id: number;
  trip_id: number;
  user_id: number;
  service_name: string;
  category: 'flight' | 'hotel' | 'activity' | 'restaurant' | string;
  booking_reference: string;
  price: number;
  status: 'PENDING' | 'CONFIRMED' | 'CANCELLED';
  booking_date: string;
  details?: Record<string, any>;
}

export const bookingsAPI = {
  list: (): Promise<BookingItem[]> =>
    api.get('/bookings/').then((r) => r.data),

  get: (id: number): Promise<BookingItem> =>
    api.get(`/bookings/${id}`).then((r) => r.data),

  confirm: (id: number): Promise<{ message: string; booking_reference: string; status: string }> =>
    api.post(`/bookings/${id}/confirm`).then((r) => r.data),

  cancel: (id: number): Promise<{ message: string; booking_reference: string; status: string }> =>
    api.post(`/bookings/${id}/cancel`).then((r) => r.data),

  bookFlight: (data: { trip_id: number; flight_number: string; airline: string; origin: string; destination: string; price: number; passengers?: number; departure_time?: string }): Promise<any> =>
    api.post('/bookings/flight', data).then((r) => r.data),

  bookHotel: (data: { trip_id: number; hotel_name: string; city: string; check_in: string; check_out: string; price: number; guests?: number }): Promise<any> =>
    api.post('/bookings/hotel', data).then((r) => r.data),

  bookActivity: (data: { trip_id: number; activity_name: string; location: string; date: string; price: number }): Promise<any> =>
    api.post('/bookings/activity', data).then((r) => r.data),

  bookRestaurant: (data: { trip_id: number; restaurant_name: string; city: string; date: string; time: string; price: number; guests?: number }): Promise<any> =>
    api.post('/bookings/restaurant', data).then((r) => r.data),

  getRecommendations: (destination: string, origin: string, trip_id?: number): Promise<{
    destination: string;
    origin: string;
    trip_id?: number;
    recommended_hotels: any[];
    recommended_flights: any[];
    recommended_activities: any[];
    recommended_restaurants: any[];
    notice: string;
  }> =>
    api.get('/bookings/recommendations', { params: { destination, origin, trip_id } }).then((r) => r.data),

  checkout: (data: {
    booking_id?: number;
    booking_ids?: number[];
    trip_id?: number;
    payment_method: string;
    card_number?: string;
    card_holder?: string;
    card_expiry?: string;
    phone_number?: string;
  }): Promise<CheckoutResult> =>
    api.post('/bookings/checkout', data).then((r) => r.data),
};

// ---------------------------------------------------------------------------
// Standalone Direct Functions for Convenient Usage
// ---------------------------------------------------------------------------
export const planTripWithAI = async (prompt: string, language?: string, currency?: string, signal?: AbortSignal) => {
  const res = await api.post('/agent/plan-trip', { prompt, language, currency }, { signal });
  return res.data;
};

export const exportTripPDF = (tripId: number) => {
  if (typeof window !== 'undefined') {
    window.open(`${API_BASE_URL}/trips/${tripId}/pdf`, '_blank');
  }
};

export const replanTrip = async (
  tripId: number,
  modifiedItemId?: number,
  notes?: string,
  newStartTime?: string
) => {
  const res = await api.post('/agent/replan', {
    trip_id: tripId,
    modified_item_id: modifiedItemId,
    notes,
    new_start_time: newStartTime,
  });
  return res.data;
};

export const askInTripSupport = async (tripId: number, query: string, lat?: number, lng?: number) => {
  const res = await api.post('/agent/in-trip-support', {
    trip_id: tripId,
    user_query: query,
    current_lat: lat,
    current_lng: lng,
  });
  return res.data;
};

export const getTripVersions = async (tripId: number) => {
  const res = await api.get(`/agent/trips/${tripId}/versions`);
  return res.data;
};

// ---------------------------------------------------------------------------
// Helper: format currency
// ---------------------------------------------------------------------------
export const formatCurrency = (amount: number, currency: string): string => {
  const localeMap: Record<string, string> = {
    VND: 'vi-VN',
    USD: 'en-US',
    EUR: 'de-DE',
    KRW: 'ko-KR',
    JPY: 'ja-JP',
    CNY: 'zh-CN',
    THB: 'th-TH',
    GBP: 'en-GB',
    CHF: 'de-CH',
  };
  const locale = localeMap[currency] || 'en-US';
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    maximumFractionDigits: currency === 'VND' || currency === 'JPY' || currency === 'KRW' ? 0 : 2,
  }).format(amount);
};
