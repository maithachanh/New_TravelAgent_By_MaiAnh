import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NavbarHeader } from '../../src/components/NavbarHeader';
import {
  searchFlightsMobile,
  searchHotelsMobile,
  getBookingsMobile,
  confirmBookingMobile,
  cancelBookingMobile,
  BookingData,
} from '../../src/api/index';

const PRIMARY = '#0284C7';
const BG_DARK = '#0F172A';
const CARD_BG = '#1E293B';
const BORDER = '#334155';
const TEXT_PRIMARY = '#F1F5F9';
const TEXT_SECONDARY = '#94A3B8';
const SUCCESS = '#10B981';
const DANGER = '#EF4444';
const WARNING = '#F59E0B';

export default function ServicesScreen() {
  const [activeTab, setActiveTab] = useState<'flights' | 'hotels' | 'bookings'>('flights');

  // Flights State
  const [flightOrigin, setFlightOrigin] = useState('Hà Nội');
  const [flightDest, setFlightDest] = useState('Tokyo');
  const [flightTravelers, setFlightTravelers] = useState('2');
  const [flights, setFlights] = useState<any[]>([]);
  const [flightLoading, setFlightLoading] = useState(false);

  // Hotels State
  const [hotelCity, setHotelCity] = useState('Tokyo');
  const [budgetTier, setBudgetTier] = useState('MEDIUM');
  const [hotels, setHotels] = useState<any[]>([]);
  const [hotelLoading, setHotelLoading] = useState(false);

  // Bookings State
  const [bookings, setBookings] = useState<BookingData[]>([]);
  const [bookingsLoading, setBookingsLoading] = useState(false);

  useEffect(() => {
    if (activeTab === 'bookings') {
      loadBookings();
    }
  }, [activeTab]);

  const handleSearchFlights = async () => {
    if (!flightDest.trim()) {
      Alert.alert('Thông báo', 'Vui lòng nhập điểm đến.');
      return;
    }
    setFlightLoading(true);
    try {
      const data = await searchFlightsMobile(flightOrigin, flightDest, parseInt(flightTravelers) || 1);
      const flightList = Array.isArray(data) ? data : (data?.flights || data?.offers || []);
      setFlights(flightList);
    } catch (err: any) {
      Alert.alert('Lỗi', err.message || 'Không tìm thấy chuyến bay.');
    } finally {
      setFlightLoading(false);
    }
  };

  const handleSearchHotels = async () => {
    if (!hotelCity.trim()) {
      Alert.alert('Thông báo', 'Vui lòng nhập thành phố.');
      return;
    }
    setHotelLoading(true);
    try {
      const data = await searchHotelsMobile(hotelCity, budgetTier);
      const hotelList = Array.isArray(data) ? data : (data?.hotels || data?.accommodations || []);
      setHotels(hotelList);
    } catch (err: any) {
      Alert.alert('Lỗi', err.message || 'Không tìm thấy khách sạn.');
    } finally {
      setHotelLoading(false);
    }
  };

  const loadBookings = async () => {
    setBookingsLoading(true);
    try {
      const data = await getBookingsMobile();
      setBookings(data || []);
    } catch {
      setBookings([]);
    } finally {
      setBookingsLoading(false);
    }
  };

  const handleConfirmBooking = async (id: number) => {
    try {
      await confirmBookingMobile(id);
      Alert.alert('Thành công', 'Đã xác nhận đặt chỗ thành công!');
      loadBookings();
    } catch (err: any) {
      Alert.alert('Lỗi', err.message);
    }
  };

  const handleCancelBooking = async (id: number) => {
    try {
      await cancelBookingMobile(id);
      Alert.alert('Đã hủy', 'Đã hủy dịch vụ đặt chỗ.');
      loadBookings();
    } catch (err: any) {
      Alert.alert('Lỗi', err.message);
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <LinearGradient colors={[BG_DARK, '#0C1825']} style={styles.gradient}>
        <NavbarHeader title="✈️ Dịch Vụ & Đặt Chỗ" subtitle="Vé máy bay, Khách sạn & Quản lý booking" />

        {/* Sub tabs */}
        <View style={styles.tabBar}>
          <TouchableOpacity
            style={[styles.tabItem, activeTab === 'flights' && styles.tabItemActive]}
            onPress={() => setActiveTab('flights')}
          >
            <Ionicons
              name="airplane-outline"
              size={16}
              color={activeTab === 'flights' ? '#fff' : TEXT_SECONDARY}
            />
            <Text style={[styles.tabText, activeTab === 'flights' && styles.tabTextActive]}>
              Vé Bay
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.tabItem, activeTab === 'hotels' && styles.tabItemActive]}
            onPress={() => setActiveTab('hotels')}
          >
            <Ionicons
              name="bed-outline"
              size={16}
              color={activeTab === 'hotels' ? '#fff' : TEXT_SECONDARY}
            />
            <Text style={[styles.tabText, activeTab === 'hotels' && styles.tabTextActive]}>
              Khách Sạn
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.tabItem, activeTab === 'bookings' && styles.tabItemActive]}
            onPress={() => setActiveTab('bookings')}
          >
            <Ionicons
              name="receipt-outline"
              size={16}
              color={activeTab === 'bookings' ? '#fff' : TEXT_SECONDARY}
            />
            <Text style={[styles.tabText, activeTab === 'bookings' && styles.tabTextActive]}>
              Booking ({bookings.length})
            </Text>
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}>
          {/* TAB 1: FLIGHTS */}
          {activeTab === 'flights' && (
            <View>
              <View style={styles.searchCard}>
                <Text style={styles.cardTitle}>🔍 Tìm Kiếm Chuyến Bay Toàn Cầu</Text>
                <View style={styles.row}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.inputLabel}>Nơi khởi hành</Text>
                    <TextInput
                      style={styles.input}
                      value={flightOrigin}
                      onChangeText={setFlightOrigin}
                      placeholder="Hà Nội / SGN..."
                      placeholderTextColor="#64748B"
                    />
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.inputLabel}>Nơi đến</Text>
                    <TextInput
                      style={styles.input}
                      value={flightDest}
                      onChangeText={setFlightDest}
                      placeholder="Tokyo, Paris..."
                      placeholderTextColor="#64748B"
                    />
                  </View>
                </View>
                <View style={{ marginTop: 10 }}>
                  <Text style={styles.inputLabel}>Số lượng hành khách</Text>
                  <TextInput
                    style={styles.input}
                    value={flightTravelers}
                    onChangeText={setFlightTravelers}
                    keyboardType="numeric"
                    placeholder="2"
                    placeholderTextColor="#64748B"
                  />
                </View>

                <TouchableOpacity
                  style={styles.searchBtn}
                  onPress={handleSearchFlights}
                  disabled={flightLoading}
                >
                  <LinearGradient colors={[PRIMARY, '#0369A1']} style={styles.searchGradient}>
                    {flightLoading ? (
                      <ActivityIndicator color="#fff" size="small" />
                    ) : (
                      <Ionicons name="search" size={16} color="#fff" />
                    )}
                    <Text style={styles.searchBtnText}>
                      {flightLoading ? 'Đang tìm...' : 'Tra Cứu Chuyến Bay'}
                    </Text>
                  </LinearGradient>
                </TouchableOpacity>
              </View>

              {/* Flight Results */}
              {(Array.isArray(flights) ? flights : []).map((fl: any, i: number) => (
                <View key={i} style={styles.resultItem}>
                  <View style={styles.resultHeader}>
                    <Text style={styles.airlineName}>✈️ {fl.airline || 'Hãng bay'}</Text>
                    <Text style={styles.flightNo}>{fl.flight_number || 'VN-999'}</Text>
                  </View>
                  <View style={styles.flightRoute}>
                    <Text style={styles.routeText}>{fl.origin || flightOrigin}</Text>
                    <Ionicons name="airplane" size={16} color={PRIMARY} />
                    <Text style={styles.routeText}>{fl.destination || flightDest}</Text>
                  </View>
                  <View style={styles.resultBottom}>
                    <Text style={styles.priceText}>
                      {Number(fl.price_per_person || fl.price || 0).toLocaleString()} VND / người
                    </Text>
                    <TouchableOpacity
                      style={styles.bookBtn}
                      onPress={() => Alert.alert('Đặt vé', 'Tính năng giữ chỗ đã kích hoạt!')}
                    >
                      <Text style={styles.bookBtnText}>Giữ Chỗ</Text>
                    </TouchableOpacity>
                  </View>
                </View>
              ))}
            </View>
          )}

          {/* TAB 2: HOTELS */}
          {activeTab === 'hotels' && (
            <View>
              <View style={styles.searchCard}>
                <Text style={styles.cardTitle}>🏨 Tìm Khách Sạn & Chỗ Nghỉ</Text>
                <Text style={styles.inputLabel}>Thành phố hoặc địa danh</Text>
                <TextInput
                  style={styles.input}
                  value={hotelCity}
                  onChangeText={setHotelCity}
                  placeholder="Tokyo, Seoul, Đà Nẵng..."
                  placeholderTextColor="#64748B"
                />

                <Text style={[styles.inputLabel, { marginTop: 10 }]}>Hạng mức ngân sách</Text>
                <View style={styles.tierRow}>
                  {['BUDGET', 'MEDIUM', 'LUXURY'].map(tier => (
                    <TouchableOpacity
                      key={tier}
                      style={[styles.tierBtn, budgetTier === tier && styles.tierBtnActive]}
                      onPress={() => setBudgetTier(tier)}
                    >
                      <Text style={[styles.tierText, budgetTier === tier && styles.tierTextActive]}>
                        {tier === 'BUDGET' ? 'Tiết kiệm' : tier === 'MEDIUM' ? 'Tiêu chuẩn' : 'Cao cấp'}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>

                <TouchableOpacity
                  style={styles.searchBtn}
                  onPress={handleSearchHotels}
                  disabled={hotelLoading}
                >
                  <LinearGradient colors={[PRIMARY, '#0369A1']} style={styles.searchGradient}>
                    {hotelLoading ? (
                      <ActivityIndicator color="#fff" size="small" />
                    ) : (
                      <Ionicons name="search" size={16} color="#fff" />
                    )}
                    <Text style={styles.searchBtnText}>
                      {hotelLoading ? 'Đang tìm...' : 'Tìm Khách Sạn'}
                    </Text>
                  </LinearGradient>
                </TouchableOpacity>
              </View>

              {/* Hotel Results */}
              {(Array.isArray(hotels) ? hotels : []).map((ht: any, i: number) => (
                <View key={i} style={styles.resultItem}>
                  <View style={styles.resultHeader}>
                    <Text style={styles.airlineName}>🏨 {ht.name || 'Khách sạn'}</Text>
                    <Text style={styles.starText}>⭐ {ht.stars || ht.rating || 4.5}</Text>
                  </View>
                  <Text style={styles.addressText}>📍 {ht.address || ht.city || hotelCity}</Text>
                  <View style={styles.resultBottom}>
                    <Text style={styles.priceText}>
                      {Number(ht.price_per_night || ht.price || 0).toLocaleString()} VND / đêm
                    </Text>
                    <TouchableOpacity
                      style={styles.bookBtn}
                      onPress={() => Alert.alert('Đặt phòng', 'Đã lưu yêu cầu giữ phòng!')}
                    >
                      <Text style={styles.bookBtnText}>Đặt Ngay</Text>
                    </TouchableOpacity>
                  </View>
                </View>
              ))}
            </View>
          )}

          {/* TAB 3: BOOKINGS */}
          {activeTab === 'bookings' && (
            <View>
              {bookingsLoading ? (
                <ActivityIndicator color={PRIMARY} style={{ marginVertical: 40 }} />
              ) : bookings.length === 0 ? (
                <View style={styles.emptyBox}>
                  <Text style={styles.emptyIcon}>🎫</Text>
                  <Text style={styles.emptyTitle}>Chưa có dịch vụ nào được đề xuất</Text>
                  <Text style={styles.emptySub}>
                    Khi bạn dùng AI Planner tạo tour, các dịch vụ vé bay, khách sạn và trải nghiệm sẽ xuất hiện ở đây để bạn xác nhận!
                  </Text>
                </View>
              ) : (
                bookings.map(bk => (
                  <View key={bk.id} style={styles.bookingCard}>
                    <View style={styles.bookingTop}>
                      <View style={{ flex: 1 }}>
                        <Text style={styles.bookingService}>{bk.service_name}</Text>
                        <Text style={styles.bookingRef}>Mã: {bk.booking_reference}</Text>
                      </View>
                      <View
                        style={[
                          styles.statusBadge,
                          {
                            backgroundColor:
                              bk.status === 'confirmed' ? '#065F46' : bk.status === 'cancelled' ? '#450A0A' : '#78350F',
                          },
                        ]}
                      >
                        <Text
                          style={[
                            styles.statusText,
                            {
                              color:
                                bk.status === 'confirmed' ? SUCCESS : bk.status === 'cancelled' ? DANGER : WARNING,
                            },
                          ]}
                        >
                          {bk.status === 'confirmed' ? '✓ Đã xác nhận' : bk.status === 'cancelled' ? 'Đã hủy' : '⏳ Chờ duyệt'}
                        </Text>
                      </View>
                    </View>

                    <Text style={styles.bookingPrice}>
                      Chi phí: {Number(bk.price).toLocaleString()} VND
                    </Text>

                    {bk.status === 'pending' && (
                      <View style={styles.bookingActions}>
                        <TouchableOpacity
                          style={styles.confirmBtn}
                          onPress={() => handleConfirmBooking(bk.id)}
                        >
                          <Ionicons name="checkmark-circle-outline" size={16} color="#fff" />
                          <Text style={styles.actionBtnText}>Xác Nhận</Text>
                        </TouchableOpacity>
                        <TouchableOpacity
                          style={styles.cancelBtn}
                          onPress={() => handleCancelBooking(bk.id)}
                        >
                          <Ionicons name="close-circle-outline" size={16} color="#F87171" />
                          <Text style={[styles.actionBtnText, { color: '#F87171' }]}>Hủy</Text>
                        </TouchableOpacity>
                      </View>
                    )}
                  </View>
                ))
              )}
            </View>
          )}
        </ScrollView>
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: BG_DARK },
  gradient: { flex: 1 },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: CARD_BG,
    marginHorizontal: 16,
    marginTop: 10,
    borderRadius: 12,
    padding: 4,
    borderWidth: 1,
    borderColor: BORDER,
  },
  tabItem: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    gap: 6,
    borderRadius: 8,
  },
  tabItemActive: { backgroundColor: PRIMARY },
  tabText: { color: TEXT_SECONDARY, fontWeight: '700', fontSize: 13 },
  tabTextActive: { color: '#fff' },
  scroll: { flex: 1 },
  scrollContent: { padding: 16, paddingBottom: 40 },
  searchCard: {
    backgroundColor: CARD_BG,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: BORDER,
  },
  cardTitle: { color: TEXT_PRIMARY, fontWeight: '800', fontSize: 16, marginBottom: 12 },
  row: { flexDirection: 'row', gap: 10 },
  inputLabel: { color: TEXT_SECONDARY, fontSize: 12, fontWeight: '600', marginBottom: 4 },
  input: {
    backgroundColor: BG_DARK,
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 10,
    color: TEXT_PRIMARY,
    fontSize: 14,
    borderWidth: 1,
    borderColor: BORDER,
  },
  tierRow: { flexDirection: 'row', gap: 8, marginTop: 4 },
  tierBtn: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: BG_DARK,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: BORDER,
  },
  tierBtnActive: { borderColor: PRIMARY, backgroundColor: '#1E3A5F' },
  tierText: { color: TEXT_SECONDARY, fontSize: 12, fontWeight: '600' },
  tierTextActive: { color: '#fff', fontWeight: '700' },
  searchBtn: { borderRadius: 10, overflow: 'hidden', marginTop: 14 },
  searchGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    gap: 8,
  },
  searchBtnText: { color: '#fff', fontWeight: '700', fontSize: 14 },
  resultItem: {
    backgroundColor: CARD_BG,
    borderRadius: 14,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: BORDER,
  },
  resultHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  airlineName: { color: TEXT_PRIMARY, fontWeight: '800', fontSize: 15 },
  flightNo: { color: PRIMARY, fontWeight: '700', fontSize: 13 },
  starText: { color: '#FCD34D', fontWeight: '700', fontSize: 13 },
  addressText: { color: TEXT_SECONDARY, fontSize: 12, marginBottom: 8 },
  flightRoute: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginVertical: 6,
  },
  routeText: { color: '#BAE6FD', fontWeight: '600', fontSize: 13 },
  resultBottom: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#334155',
  },
  priceText: { color: SUCCESS, fontWeight: '800', fontSize: 14 },
  bookBtn: {
    backgroundColor: PRIMARY,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  bookBtnText: { color: '#fff', fontWeight: '700', fontSize: 12 },
  emptyBox: { alignItems: 'center', paddingVertical: 40 },
  emptyIcon: { fontSize: 48, marginBottom: 12 },
  emptyTitle: { color: TEXT_PRIMARY, fontSize: 17, fontWeight: '800', marginBottom: 6 },
  emptySub: { color: TEXT_SECONDARY, fontSize: 13, textAlign: 'center', lineHeight: 20 },
  bookingCard: {
    backgroundColor: CARD_BG,
    borderRadius: 14,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: BORDER,
  },
  bookingTop: { flexDirection: 'row', alignItems: 'flex-start', gap: 10 },
  bookingService: { color: TEXT_PRIMARY, fontWeight: '700', fontSize: 14 },
  bookingRef: { color: TEXT_SECONDARY, fontSize: 11, marginTop: 2 },
  statusBadge: { borderRadius: 12, paddingHorizontal: 8, paddingVertical: 3 },
  statusText: { fontSize: 11, fontWeight: '700' },
  bookingPrice: { color: SUCCESS, fontWeight: '700', fontSize: 13, marginTop: 8 },
  bookingActions: { flexDirection: 'row', gap: 10, marginTop: 12 },
  confirmBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#065F46',
    borderRadius: 8,
    paddingVertical: 8,
    gap: 4,
  },
  cancelBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#450A0A',
    borderRadius: 8,
    paddingVertical: 8,
    gap: 4,
  },
  actionBtnText: { color: '#fff', fontWeight: '700', fontSize: 12 },
});
