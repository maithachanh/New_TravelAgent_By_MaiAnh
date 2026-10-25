import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Alert,
  Linking,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useFocusEffect } from 'expo-router';
import { NavbarHeader } from '../../src/components/NavbarHeader';
import { ReplanModal } from '../../src/components/ReplanModal';
import { TripData } from '../../src/api/index';
import { tripSync } from '../../src/services/tripSync';

const PRIMARY = '#0284C7';
const BG_DARK = '#0F172A';
const CARD_BG = '#1E293B';
const BORDER = '#334155';
const TEXT_PRIMARY = '#F1F5F9';
const TEXT_SECONDARY = '#94A3B8';
const SUCCESS = '#10B981';
const DANGER = '#EF4444';

const ITEM_TYPE_ICON: Record<string, string> = {
  flight: '✈️',
  FLIGHT: '✈️',
  hotel: '🏨',
  HOTEL: '🏨',
  restaurant: '🍽️',
  RESTAURANT: '🍽️',
  MEAL: '🍽️',
  activity: '🎯',
  ACTIVITY: '🎯',
  ATTRACTION: '🎯',
  transport: '🚌',
  TRANSPORT: '🚌',
  shopping: '🛍️',
  SHOPPING: '🛍️',
  default: '📍',
};

export default function ItineraryScreen() {
  const [trips, setTrips] = useState<TripData[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedTrip, setSelectedTrip] = useState<TripData | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [expandedDays, setExpandedDays] = useState<Set<number>>(new Set([0]));
  const [replanItem, setReplanItem] = useState<any>(null);

  const loadTrips = async () => {
    try {
      // 1. Immediately read cached trips for instant display
      const local = await tripSync.getLocalTrips();
      if (local && local.length > 0) {
        setTrips(local);
        setLoading(false);
      }
      // 2. Fetch fresh trips from backend
      const fresh = await tripSync.syncTrips();
      setTrips(fresh || []);
    } catch {
      // If network fails, keep cached trips
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      loadTrips();
    }, [])
  );

  const onRefresh = () => {
    setRefreshing(true);
    loadTrips();
  };

  const loadTripDetail = async (tripId: number) => {
    setDetailLoading(true);
    try {
      const detail = await tripSync.syncTripDetail(tripId);
      setSelectedTrip(detail);
      setExpandedDays(new Set([0]));
    } catch {
      Alert.alert('Lỗi', 'Không thể tải chi tiết chuyến đi.');
    } finally {
      setDetailLoading(false);
    }
  };

  const handleDeleteTrip = (tripId: number, name: string) => {
    Alert.alert(
      'Xóa chuyến đi',
      `Bạn có chắc chắn muốn xóa "${name}"?`,
      [
        { text: 'Hủy', style: 'cancel' },
        {
          text: 'Xóa Vĩnh Viễn',
          style: 'destructive',
          onPress: async () => {
            try {
              await tripSync.deleteTrip(tripId);
              if (selectedTrip?.id === tripId) {
                setSelectedTrip(null);
              }
              await loadTrips();
              Alert.alert('Thành công', 'Đã xóa chuyến đi thành công.');
            } catch {
              Alert.alert('Lỗi', 'Không thể xóa chuyến đi.');
            }
          },
        },
      ]
    );
  };

  const toggleDay = (dayIndex: number) => {
    setExpandedDays(prev => {
      const next = new Set(prev);
      if (next.has(dayIndex)) next.delete(dayIndex);
      else next.add(dayIndex);
      return next;
    });
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <LinearGradient colors={[BG_DARK, '#0C1825']} style={styles.gradient}>
        <NavbarHeader
          title={selectedTrip ? selectedTrip.title || selectedTrip.destination : '📋 Lịch Trình Đã Lưu'}
          subtitle={selectedTrip ? `Tour #${selectedTrip.id}` : `${trips.length} chuyến đi đã đồng bộ`}
          showBack={!!selectedTrip}
          onBack={() => setSelectedTrip(null)}
        />

        {!selectedTrip ? (
          // Trip List View
          <ScrollView
            style={styles.scroll}
            contentContainerStyle={[styles.scrollContent, trips.length === 0 && styles.centered]}
            refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={PRIMARY} />}
            showsVerticalScrollIndicator={false}
          >
            {loading ? (
              <ActivityIndicator size="large" color={PRIMARY} style={{ marginTop: 40 }} />
            ) : trips.length === 0 ? (
              <View style={styles.emptyBox}>
                <Text style={styles.emptyIcon}>🗺️</Text>
                <Text style={styles.emptyTitle}>Chưa có lịch trình nào</Text>
                <Text style={styles.emptySub}>
                  Hãy dùng tab AI Planner để tạo tour tự động cho điểm đến bạn yêu thích!
                </Text>
              </View>
            ) : (
              trips.map(trip => (
                <TouchableOpacity
                  key={trip.id}
                  style={styles.tripCard}
                  onPress={() => loadTripDetail(trip.id)}
                  activeOpacity={0.8}
                >
                  <LinearGradient
                    colors={['#1E3A5F', '#0F2744']}
                    style={styles.tripCardGradient}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 1 }}
                  >
                    <View style={styles.tripTop}>
                      <View style={{ flex: 1 }}>
                        <Text style={styles.tripTitle}>{trip.title || `Tour ${trip.destination}`}</Text>
                        <Text style={styles.tripDest}>📍 {trip.destination}</Text>
                      </View>
                      <TouchableOpacity
                        onPress={() => handleDeleteTrip(trip.id, trip.title || trip.destination)}
                        hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                      >
                        <Ionicons name="trash-outline" size={18} color="#F87171" />
                      </TouchableOpacity>
                    </View>

                    <View style={styles.tripMetaRow}>
                      <View style={styles.tripMetaItem}>
                        <Ionicons name="calendar-outline" size={13} color="#BAE6FD" />
                        <Text style={styles.tripMetaText}>
                          {trip.start_date} → {trip.end_date}
                        </Text>
                      </View>
                      <View style={styles.tripMetaItem}>
                        <Ionicons name="people-outline" size={13} color="#BAE6FD" />
                        <Text style={styles.tripMetaText}>{trip.travelers} người</Text>
                      </View>
                    </View>

                    <View style={styles.tripBottom}>
                      <Text style={styles.tripBudget}>
                        💰 {Number(trip.budget || 0).toLocaleString()} VND
                      </Text>
                      <View style={styles.cardActions}>
                        <TouchableOpacity
                          style={styles.smallPdfBtn}
                          onPress={() => tripSync.downloadPdf(trip.id)}
                        >
                          <Ionicons name="document-text-outline" size={13} color="#38BDF8" />
                          <Text style={styles.smallPdfText}>PDF</Text>
                        </TouchableOpacity>
                        <Ionicons name="chevron-forward" size={16} color={TEXT_SECONDARY} />
                      </View>
                    </View>
                  </LinearGradient>
                </TouchableOpacity>
              ))
            )}
          </ScrollView>
        ) : (
          // Trip Detail View
          <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}>
            {detailLoading ? (
              <ActivityIndicator size="large" color={PRIMARY} style={{ marginTop: 40 }} />
            ) : (
              <>
                {/* Trip Summary Card */}
                <View style={styles.detailCard}>
                  <View style={styles.detailRow}>
                    <View style={styles.detailItem}>
                      <Text style={styles.detailLabel}>Khởi hành từ</Text>
                      <Text style={styles.detailValue}>{selectedTrip.origin || 'Việt Nam'}</Text>
                    </View>
                    <View style={styles.detailItem}>
                      <Text style={styles.detailLabel}>Số khách</Text>
                      <Text style={styles.detailValue}>{selectedTrip.travelers} người</Text>
                    </View>
                    <View style={styles.detailItem}>
                      <Text style={styles.detailLabel}>Ngân sách</Text>
                      <Text style={[styles.detailValue, { color: SUCCESS }]}>
                        {Number(selectedTrip.budget || 0).toLocaleString()} VND
                      </Text>
                    </View>
                  </View>

                  <View style={styles.pdfDownloadRow}>
                    <TouchableOpacity
                      style={styles.downloadPdfBtn}
                      onPress={() => tripSync.downloadPdf(selectedTrip.id)}
                    >
                      <Ionicons name="cloud-download-outline" size={16} color="#fff" />
                      <Text style={styles.downloadPdfText}>Xuất PDF</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={styles.openMapBtn}
                      onPress={() => {
                        const url = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(selectedTrip.destination)}`;
                        Linking.openURL(url);
                      }}
                    >
                      <Ionicons name="map-outline" size={16} color="#fff" />
                      <Text style={styles.downloadPdfText}>Bản Đồ Google Maps</Text>
                    </TouchableOpacity>
                  </View>
                </View>

                {/* Days Accordion */}
                {selectedTrip.days?.map((day, dIdx) => (
                  <View key={dIdx} style={styles.daySection}>
                    <TouchableOpacity
                      style={styles.dayHeaderBtn}
                      onPress={() => toggleDay(dIdx)}
                      activeOpacity={0.8}
                    >
                      <LinearGradient
                        colors={['#1E3A5F', '#1D4ED8']}
                        style={styles.dayHeaderGradient}
                        start={{ x: 0, y: 0 }}
                        end={{ x: 1, y: 0 }}
                      >
                        <View>
                          <Text style={styles.dayNum}>Ngày {day.day_number}</Text>
                          <Text style={styles.dayDate}>{day.date}</Text>
                        </View>
                        <Ionicons
                          name={expandedDays.has(dIdx) ? 'chevron-up' : 'chevron-down'}
                          size={18}
                          color="#BAE6FD"
                        />
                      </LinearGradient>
                    </TouchableOpacity>

                    {expandedDays.has(dIdx) && (
                      <View style={styles.dayBody}>
                        {day.items?.map((item, iIdx) => (
                          <View key={iIdx} style={styles.timelineRow}>
                            <View style={styles.iconBox}>
                              <Text style={styles.itemEmoji}>
                                {ITEM_TYPE_ICON[item.item_type || 'default'] || '📍'}
                              </Text>
                              {iIdx < (day.items?.length || 0) - 1 && <View style={styles.line} />}
                            </View>

                            <View style={styles.timelineContent}>
                              <View style={styles.itemHeaderRow}>
                                <Text style={styles.itemTime}>
                                  {item.start_time} – {item.end_time}
                                </Text>
                                <TouchableOpacity
                                  style={styles.replanBtn}
                                  onPress={() => setReplanItem(item)}
                                >
                                  <Ionicons name="create-outline" size={13} color={PRIMARY} />
                                  <Text style={styles.replanBtnText}>Sửa</Text>
                                </TouchableOpacity>
                              </View>
                              <Text style={styles.itemTitle}>{item.title}</Text>
                              {item.location ? (
                                <View style={styles.locationContainer}>
                                  <Text style={styles.itemLocation}>📍 {item.location}</Text>
                                  <TouchableOpacity
                                    style={styles.directNavBtn}
                                    onPress={() => {
                                      const dest = item.latitude && item.longitude
                                        ? `${item.latitude},${item.longitude}`
                                        : encodeURIComponent(item.location || item.title);
                                      Linking.openURL(`https://www.google.com/maps/dir/?api=1&destination=${dest}`);
                                    }}
                                  >
                                    <Ionicons name="navigate-outline" size={11} color="#0284C7" />
                                    <Text style={styles.directNavText}>Chỉ đường</Text>
                                  </TouchableOpacity>
                                </View>
                              ) : null}
                              {Number(item.estimated_cost || 0) > 0 ? (
                                <Text style={styles.itemCost}>
                                  💰 {Number(item.estimated_cost).toLocaleString()} VND
                                </Text>
                              ) : null}
                              {item.notes ? (
                                <Text style={styles.itemNotes}>💡 {item.notes}</Text>
                              ) : null}
                            </View>
                          </View>
                        ))}
                      </View>
                    )}
                  </View>
                ))}
              </>
            )}
          </ScrollView>
        )}

        {/* Replan Modal */}
        {replanItem && selectedTrip && (
          <ReplanModal
            visible={!!replanItem}
            tripId={selectedTrip.id}
            item={replanItem}
            onClose={() => setReplanItem(null)}
            onSuccess={() => {
              loadTripDetail(selectedTrip.id);
            }}
          />
        )}
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: BG_DARK },
  gradient: { flex: 1 },
  scroll: { flex: 1 },
  scrollContent: { padding: 16, paddingBottom: 40 },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center', minHeight: 350 },
  emptyBox: { alignItems: 'center', paddingVertical: 40 },
  emptyIcon: { fontSize: 54, marginBottom: 14 },
  emptyTitle: { color: TEXT_PRIMARY, fontSize: 18, fontWeight: '800', marginBottom: 8 },
  emptySub: { color: TEXT_SECONDARY, fontSize: 13, textAlign: 'center', lineHeight: 20 },
  tripCard: {
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 12,
    borderWidth: 1,
    borderColor: BORDER,
  },
  tripCardGradient: { padding: 16 },
  tripTop: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: 10 },
  tripTitle: { color: '#fff', fontWeight: '800', fontSize: 16, marginBottom: 3 },
  tripDest: { color: '#BAE6FD', fontSize: 12 },
  tripMetaRow: { flexDirection: 'row', gap: 14, marginBottom: 12 },
  tripMetaItem: { flexDirection: 'row', alignItems: 'center', gap: 5 },
  tripMetaText: { color: '#BAE6FD', fontSize: 11 },
  tripBottom: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.1)',
  },
  tripBudget: { color: '#fff', fontWeight: '800', fontSize: 14 },
  cardActions: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  smallPdfBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(56, 189, 248, 0.15)',
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 3,
    gap: 4,
  },
  smallPdfText: { color: '#38BDF8', fontSize: 11, fontWeight: '700' },
  detailCard: {
    backgroundColor: CARD_BG,
    borderRadius: 16,
    padding: 16,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: BORDER,
  },
  detailRow: { flexDirection: 'row', justifyContent: 'space-around', marginBottom: 12 },
  detailItem: { alignItems: 'center' },
  detailLabel: { color: TEXT_SECONDARY, fontSize: 11, marginBottom: 4 },
  detailValue: { color: TEXT_PRIMARY, fontWeight: '800', fontSize: 14 },
  pdfDownloadRow: { borderTopWidth: 1, borderTopColor: '#334155', paddingTop: 12, flexDirection: 'row', gap: 8 },
  downloadPdfBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: PRIMARY,
    borderRadius: 10,
    paddingVertical: 10,
    gap: 6,
  },
  downloadPdfText: { color: '#fff', fontWeight: '700', fontSize: 13 },
  daySection: { marginBottom: 12 },
  dayHeaderBtn: { borderRadius: 12, overflow: 'hidden' },
  dayHeaderGradient: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
  },
  dayNum: { color: '#fff', fontWeight: '800', fontSize: 15 },
  dayDate: { color: '#BAE6FD', fontSize: 11, marginTop: 2 },
  dayBody: {
    backgroundColor: CARD_BG,
    borderRadius: 12,
    padding: 12,
    marginTop: 4,
    borderWidth: 1,
    borderColor: BORDER,
  },
  timelineRow: { flexDirection: 'row', marginBottom: 16 },
  iconBox: { width: 34, alignItems: 'center' },
  itemEmoji: { fontSize: 20 },
  line: { flex: 1, width: 2, backgroundColor: BORDER, marginTop: 4, marginBottom: -6 },
  timelineContent: { flex: 1, paddingLeft: 8 },
  itemHeaderRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  itemTime: { color: PRIMARY, fontSize: 11, fontWeight: '700' },
  replanBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0F172A',
    borderRadius: 6,
    paddingHorizontal: 6,
    paddingVertical: 2,
    gap: 3,
    borderWidth: 1,
    borderColor: PRIMARY,
  },
  replanBtnText: { color: PRIMARY, fontSize: 10, fontWeight: '700' },
  itemTitle: { color: TEXT_PRIMARY, fontWeight: '700', fontSize: 14, marginVertical: 2 },
  itemLocation: { color: TEXT_SECONDARY, fontSize: 12 },
  itemCost: { color: SUCCESS, fontSize: 12, fontWeight: '600', marginTop: 2 },
  itemNotes: { color: '#FCD34D', fontSize: 11, fontStyle: 'italic', marginTop: 2 },
  openMapBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    backgroundColor: '#059669',
    borderRadius: 10,
    paddingVertical: 10,
  },
  locationContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 6,
    marginTop: 3,
  },
  directNavBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 3,
    backgroundColor: 'rgba(2, 132, 199, 0.15)',
    paddingHorizontal: 7,
    paddingVertical: 3,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: 'rgba(2, 132, 199, 0.3)',
  },
  directNavText: {
    color: '#38BDF8',
    fontSize: 10,
    fontWeight: '700',
  },
});
