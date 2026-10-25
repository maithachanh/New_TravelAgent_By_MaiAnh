import { Platform } from 'react-native';
import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Constants from 'expo-constants';

// Storage keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: '@travel_agent_auth_token',
  REFRESH_TOKEN: '@travel_agent_refresh_token',
  USER_PROFILE: '@travel_agent_user_profile',
  CUSTOM_SERVER_URL: '@travel_agent_custom_server_url',
  CACHED_TRIPS: '@travel_agent_cached_trips',
  OFFLINE_QUEUE: '@travel_agent_offline_queue',
};

/**
 * Intelligent Base URL Detection:
 * 1. Custom URL set by user in settings (AsyncStorage)
 * 2. Host URI from Expo Go (extracts the PC's actual LAN IP when running on physical phone)
 * 3. Android Emulator fallback (10.0.2.2)
 * 4. Web / iOS Simulator fallback (localhost)
 */
export const resolveDefaultHost = (): string => {
  // If running via Expo Go on a real phone or emulator, hostUri contains "192.168.x.x:8081"
  const hostUri = Constants.expoConfig?.hostUri;
  if (hostUri) {
    const ip = hostUri.split(':')[0];
    if (ip && ip !== 'localhost' && ip !== '127.0.0.1') {
      return `http://${ip}:8000/api/v1`;
    }
  }

  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:8000/api/v1';
  }
  return 'http://localhost:8000/api/v1';
};

let currentBaseUrl: string = resolveDefaultHost();

// Initialize custom URL from AsyncStorage if available
AsyncStorage.getItem(STORAGE_KEYS.CUSTOM_SERVER_URL).then(url => {
  if (url && url.trim()) {
    currentBaseUrl = url.trim();
    mobileApi.defaults.baseURL = currentBaseUrl;
  }
}).catch(() => {});

export const getApiBaseUrl = (): string => currentBaseUrl;

export const setApiBaseUrl = async (newUrl: string): Promise<void> => {
  let cleanUrl = newUrl.trim();
  if (!cleanUrl.startsWith('http://') && !cleanUrl.startsWith('https://')) {
    cleanUrl = `http://${cleanUrl}`;
  }
  if (!cleanUrl.endsWith('/api/v1')) {
    cleanUrl = cleanUrl.replace(/\/+$/, '') + '/api/v1';
  }
  currentBaseUrl = cleanUrl;
  mobileApi.defaults.baseURL = currentBaseUrl;
  await AsyncStorage.setItem(STORAGE_KEYS.CUSTOM_SERVER_URL, cleanUrl);
};

export const resetApiBaseUrl = async (): Promise<string> => {
  await AsyncStorage.removeItem(STORAGE_KEYS.CUSTOM_SERVER_URL);
  currentBaseUrl = resolveDefaultHost();
  mobileApi.defaults.baseURL = currentBaseUrl;
  return currentBaseUrl;
};

// Axios Instance
export const mobileApi: AxiosInstance = axios.create({
  baseURL: currentBaseUrl,
  timeout: 60000, // 60s for LLM/AI processing
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Request Interceptor: Attach JWT Token & Current BaseURL
mobileApi.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    config.baseURL = currentBaseUrl;
    try {
      const token = await AsyncStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch {
      // Ignore token read error
    }
    return config;
  },
  error => Promise.reject(error)
);

// Response Interceptor: Format error messages
mobileApi.interceptors.response.use(
  response => response,
  error => {
    let msg = 'Không thể kết nối máy chủ.';
    if (error.response) {
      const data = error.response.data;
      msg = data?.detail || data?.message || `Lỗi máy chủ (${error.response.status})`;
    } else if (error.code === 'ECONNABORTED') {
      msg = 'Quá thời gian phản hồi (Timeout). Vui lòng thử lại!';
    } else if (error.message) {
      msg = error.message.includes('Network Error')
        ? 'Lỗi mạng: Không kết nối được Backend. Kiểm tra IP máy chủ!'
        : error.message;
    }
    return Promise.reject(new Error(msg));
  }
);

// ─────────────── TypeScript Interfaces ───────────────
export interface UserProfile {
  id: number;
  email: string;
  full_name: string;
  language?: string;
  currency?: string;
  timezone?: string;
  travel_styles?: string[];
  is_active?: boolean;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface ItineraryItemData {
  id?: number;
  title: string;
  item_type?: string;
  type?: string;
  start_time: string;
  end_time: string;
  location?: string;
  latitude?: number;
  longitude?: number;
  estimated_cost?: number;
  cost?: number;
  notes?: string;
  duration_minutes?: number;
}

export interface ItineraryDayData {
  id?: number;
  day_number: number;
  date: string;
  city?: string;
  location?: string;
  items: ItineraryItemData[];
}

export interface TripData {
  id: number;
  user_id?: number;
  title: string;
  destination: string;
  origin?: string;
  start_date: string;
  end_date: string;
  travelers: number;
  duration_days?: number;
  duration_nights?: number;
  budget: number;
  currency: string;
  status: string;
  preferences?: string[];
  days?: ItineraryDayData[];
  created_at?: string;
  updated_at?: string;
}

export interface PlanTripResponse {
  agent_response?: string;
  destination: string;
  origin: string;
  trip_id: number;
  version: number;
  total_cost: number;
  extracted_requirements?: any;
  destination_analysis?: any;
  itinerary: ItineraryDayData[];
}

export interface ReplanTripResponse {
  message?: string;
  trip_id: number;
  version: number;
  itinerary: ItineraryDayData[];
  total_cost?: number;
  adjustments?: string[];
}

export interface CurrencyConvertResponse {
  amount: number;
  from_currency: string;
  to_currency: string;
  converted_amount: number;
  exchange_rate?: number;
  rate?: number;
  source?: string;
  last_updated?: string;
}

export interface BookingData {
  id: number;
  trip_id: number;
  service_name: string;
  category: string;
  booking_reference: string;
  price: number;
  status: string;
  details?: any;
}

// ─────────────── API Functions ───────────────

// 1. Connection & Diagnostic
export const testServerConnection = async (): Promise<{ ok: boolean; message: string; host: string }> => {
  try {
    const rootUrl = currentBaseUrl.replace('/api/v1', '');
    const res = await axios.get(`${rootUrl}/`, { timeout: 6000 });
    return { ok: true, message: res.data?.status || 'Online', host: currentBaseUrl };
  } catch (err: any) {
    return { ok: false, message: err.message, host: currentBaseUrl };
  }
};

// 2. Authentication Flow
export const loginMobile = async (email: string, password: string): Promise<AuthTokens> => {
  const res = await mobileApi.post('/auth/login', { email, password });
  const data: AuthTokens = res.data;
  if (data.access_token) {
    await AsyncStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, data.access_token);
    if (data.refresh_token) {
      await AsyncStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, data.refresh_token);
    }
  }
  return data;
};

export const registerMobile = async (
  email: string,
  password: string,
  fullName: string,
  language = 'vi',
  currency = 'VND'
): Promise<UserProfile> => {
  const res = await mobileApi.post('/auth/register', {
    email,
    password,
    full_name: fullName,
    language,
    currency,
  });
  return res.data;
};

export const getMeMobile = async (): Promise<UserProfile> => {
  const res = await mobileApi.get('/auth/me');
  const user: UserProfile = res.data;
  await AsyncStorage.setItem(STORAGE_KEYS.USER_PROFILE, JSON.stringify(user));
  return user;
};

export const logoutMobile = async (): Promise<void> => {
  await AsyncStorage.multiRemove([
    STORAGE_KEYS.AUTH_TOKEN,
    STORAGE_KEYS.REFRESH_TOKEN,
    STORAGE_KEYS.USER_PROFILE,
  ]);
};

// 3. AI Agent Planning & Support
export const planTripMobile = async (prompt: string, tripId?: number): Promise<PlanTripResponse> => {
  const res = await mobileApi.post('/agent/plan-trip', {
    prompt,
    trip_id: tripId || null,
  });
  return res.data;
};

export const replanTripMobile = async (
  tripId: number,
  modificationRequest: string,
  modifiedItem?: any
): Promise<ReplanTripResponse> => {
  const res = await mobileApi.post('/agent/replan', {
    trip_id: tripId,
    modification_request: modificationRequest,
    modified_item: modifiedItem || null,
  });
  return res.data;
};

export const askInTripSupportMobile = async (
  query: string,
  location?: string,
  tripId?: number
): Promise<{ response: string; answer?: string }> => {
  const res = await mobileApi.post('/agent/in-trip-support', {
    user_query: query,
    current_location: location || '',
    trip_id: tripId || 1,
  });
  return res.data;
};

// 4. Trips CRUD & Sync
export const getTripsMobile = async (): Promise<TripData[]> => {
  try {
    const res = await mobileApi.get('/trips/');
    const trips = res.data || [];
    // Cache locally for offline resilience
    await AsyncStorage.setItem(STORAGE_KEYS.CACHED_TRIPS, JSON.stringify(trips));
    return trips;
  } catch (err) {
    // If network fails, return cached trips if available
    const cached = await AsyncStorage.getItem(STORAGE_KEYS.CACHED_TRIPS);
    if (cached) {
      return JSON.parse(cached);
    }
    throw err;
  }
};

export const getTripDetailMobile = async (tripId: number | string): Promise<TripData> => {
  try {
    const res = await mobileApi.get(`/trips/${tripId}`);
    return res.data;
  } catch (err) {
    const cached = await AsyncStorage.getItem(`@cached_trip_detail_${tripId}`);
    if (cached) {
      return JSON.parse(cached);
    }
    throw err;
  }
};

export const deleteTripMobile = async (tripId: number | string): Promise<void> => {
  await mobileApi.delete(`/trips/${tripId}`);
};

export const getTripPdfUrl = (tripId: number | string): string => {
  return `${currentBaseUrl}/trips/${tripId}/pdf`;
};

// 5. Currency Converter
export const convertCurrencyMobile = async (
  amount: number,
  fromCur = 'USD',
  toCur = 'VND'
): Promise<CurrencyConvertResponse> => {
  const res = await mobileApi.get('/currency/convert', {
    params: { amount, from: fromCur, to: toCur },
  });
  return res.data;
};

export const getAllRatesMobile = async (base = 'USD') => {
  const res = await mobileApi.get('/currency/rates', { params: { base } });
  return res.data;
};

// 6. Bookings & Services
export const getBookingsMobile = async (tripId?: number): Promise<BookingData[]> => {
  const params = tripId ? { trip_id: tripId } : {};
  const res = await mobileApi.get('/bookings/', { params });
  return res.data;
};

export const confirmBookingMobile = async (bookingId: number): Promise<BookingData> => {
  const res = await mobileApi.post(`/bookings/${bookingId}/confirm`);
  return res.data;
};

export const cancelBookingMobile = async (bookingId: number): Promise<BookingData> => {
  const res = await mobileApi.post(`/bookings/${bookingId}/cancel`);
  return res.data;
};

// 7. Flights & Hotels Search
export const searchFlightsMobile = async (
  origin: string,
  destination: string,
  travelers = 1
) => {
  const res = await mobileApi.post('/flights/search', { origin, destination, travelers });
  return res.data;
};

export const searchHotelsMobile = async (city: string, budgetTier = 'MEDIUM') => {
  const res = await mobileApi.post('/hotels/search', { city, budget_tier: budgetTier });
  return res.data;
};

export interface TranslationResponse {
  translated_text: string;
  source_lang: string;
  target_lang: string;
  provider: string;
  success: boolean;
  error?: string;
}

// 8. Translation
export const translateTextMobile = async (
  text: string,
  targetLang = 'en',
  sourceLang = 'vi'
): Promise<TranslationResponse> => {
  const res = await mobileApi.post('/translation/translate', {
    text,
    target_lang: targetLang,
    source_lang: sourceLang,
  });
  return res.data;
};
