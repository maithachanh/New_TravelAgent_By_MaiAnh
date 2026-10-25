// Màu sắc chủ đạo của ứng dụng
export const Colors = {
  primary: '#0284C7',
  primaryDark: '#0369A1',
  primaryLight: '#E0F2FE',
  secondary: '#7C3AED',
  accent: '#F59E0B',
  success: '#16A34A',
  successLight: '#DCFCE7',
  danger: '#DC2626',
  dangerLight: '#FEE2E2',
  warning: '#D97706',

  // Nền
  background: '#F8FAFC',
  surface: '#FFFFFF',
  surfaceSecondary: '#F1F5F9',

  // Văn bản
  textPrimary: '#0F172A',
  textSecondary: '#475569',
  textTertiary: '#94A3B8',
  textInverse: '#FFFFFF',

  // Đường viền
  border: '#E2E8F0',
  borderLight: '#F1F5F9',

  // Header
  headerBg: '#0F172A',
  headerAccent: '#38BDF8',

  // Gradient
  gradientStart: '#0F172A',
  gradientEnd: '#1E293B',
} as const;

// Khoảng cách chuẩn
export const Spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  xxl: 24,
  xxxl: 32,
} as const;

// Bo góc chuẩn
export const Radius = {
  sm: 6,
  md: 10,
  lg: 14,
  xl: 20,
  full: 9999,
} as const;

// Cỡ chữ chuẩn
export const FontSize = {
  xs: 11,
  sm: 12,
  md: 14,
  lg: 16,
  xl: 18,
  xxl: 22,
  xxxl: 28,
} as const;

// Map icon cho loại hoạt động
export const ItemTypeIcon: Record<string, string> = {
  FLIGHT: '✈️',
  HOTEL_CHECKIN: '🏨',
  HOTEL_CHECKOUT: '🏨',
  RESTAURANT: '🍽️',
  BREAKFAST: '🥐',
  LUNCH: '🍱',
  DINNER: '🍜',
  ATTRACTION: '🗺️',
  MUSEUM: '🏛️',
  SHOPPING: '🛍️',
  TRANSPORT: '🚌',
  ACTIVITY: '🎭',
};

// Danh sách đồng tiền phổ biến
export const POPULAR_CURRENCIES = [
  { code: 'VND', name: 'Việt Nam Đồng', symbol: '₫' },
  { code: 'USD', name: 'Đô la Mỹ', symbol: '$' },
  { code: 'EUR', name: 'Euro', symbol: '€' },
  { code: 'JPY', name: 'Yên Nhật', symbol: '¥' },
  { code: 'KRW', name: 'Won Hàn Quốc', symbol: '₩' },
  { code: 'GBP', name: 'Bảng Anh', symbol: '£' },
  { code: 'THB', name: 'Baht Thái', symbol: '฿' },
  { code: 'SGD', name: 'Đô la Singapore', symbol: 'S$' },
  { code: 'AUD', name: 'Đô la Úc', symbol: 'A$' },
  { code: 'CHF', name: 'Franc Thụy Sĩ', symbol: 'Fr' },
  { code: 'CNY', name: 'Nhân dân tệ', symbol: '¥' },
];
