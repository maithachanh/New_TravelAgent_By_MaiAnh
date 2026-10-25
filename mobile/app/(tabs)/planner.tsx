import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { NavbarHeader } from '../../src/components/NavbarHeader';
import { ReplanModal } from '../../src/components/ReplanModal';
import { planTripMobile, PlanTripResponse, ItineraryDayData, ItineraryItemData } from '../../src/api/index';
import { tripSync } from '../../src/services/tripSync';

const PRIMARY = '#0284C7';
const BG_DARK = '#0F172A';
const CARD_BG = '#1E293B';
const BORDER = '#334155';
const TEXT_PRIMARY = '#F1F5F9';
const TEXT_SECONDARY = '#94A3B8';
const SUCCESS = '#10B981';
const WARNING = '#F59E0B';

export default function PlannerScreen() {
  const router = useRouter();
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState('');
  const [result, setResult] = useState<PlanTripResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [replanItem, setReplanItem] = useState<any>(null);
  const scrollRef = useRef<ScrollView>(null);

  const examplePrompts = [
    '🇯🇵 Tôi muốn đi Nhật Bản 7 ngày 6 đêm, ngân sách 50 triệu VND cho 2 người từ Hà Nội.',
    '🇹🇭 Lên tour Thái Lan 5 ngày 4 đêm, ngân sách 30 triệu VND cho 1 người từ TP.HCM.',
    '🇫🇷 Tour Paris 10 ngày 9 đêm, ngân sách 5000 USD cho cặp đôi từ Đà Nẵng.',
    '🇰🇷 Khám phá Seoul 5 ngày, ngân sách 40 triệu VND, 3 người từ TP.HCM.',
  ];

  // Simulated live step progress during AI planning
  useEffect(() => {
    let timer: any;
    if (loading) {
      setLoadingStep('🤖 AI đang phân tích yêu cầu điểm đến...');
      timer = setTimeout(() => {
        setLoadingStep('✈️ Đang so sánh chuyến bay & khách sạn tốt nhất...');
        timer = setTimeout(() => {
          setLoadingStep('📊 Tối ưu hóa ma trận chi phí & khoảng cách di chuyển...');
          timer = setTimeout(() => {
            setLoadingStep('📝 Đang đồng bộ hóa dữ liệu vào hệ thống...');
          }, 3500);
        }, 3500);
      }, 3000);
    }
    return () => clearTimeout(timer);
  }, [loading]);

  const handlePlan = async () => {
    if (!prompt.trim()) {
      Alert.alert('Thông báo', 'Vui lòng nhập nhu cầu du lịch của bạn.');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await planTripMobile(prompt.trim());
      setResult(data);
      // Trigger sync so itinerary tab has the new trip immediately
      await tripSync.syncTrips().catch(() => {});
      setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 400);
    } catch (e: any) {
      setError(e?.message || 'Có lỗi xảy ra khi tạo lịch trình. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  const daysList: ItineraryDayData[] = result?.itinerary || [];

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <LinearGradient colors={[BG_DARK, '#0C1825']} style={styles.gradient}>
        <NavbarHeader title="✈️ AI Travel Planner" subtitle="Lên kế hoạch thông minh cho mọi quốc gia" />

        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}
          style={{ flex: 1 }}
        >
          <ScrollView
            ref={scrollRef}
            style={styles.scroll}
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}
            keyboardShouldPersistTaps="handled"
          >
            {/* Input Card */}
            <View style={styles.inputCard}>
              <Text style={styles.inputLabel}>🌟 Nhập yêu cầu du lịch của bạn</Text>
              <TextInput
                style={styles.textInput}
                value={prompt}
                onChangeText={setPrompt}
                placeholder="Ví dụ: Tôi muốn đi Nhật Bản 7 ngày 6 đêm, ngân sách 50 triệu..."
                placeholderTextColor={TEXT_SECONDARY}
                multiline
                numberOfLines={4}
                textAlignVertical="top"
              />
              <TouchableOpacity
                style={[styles.planBtn, loading && styles.planBtnDisabled]}
                onPress={handlePlan}
                disabled={loading}
                activeOpacity={0.8}
              >
                <LinearGradient
                  colors={loading ? ['#475569', '#475569'] : [PRIMARY, '#0369A1']}
                  style={styles.planBtnGradient}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                >
                  {loading ? (
                    <ActivityIndicator color="#fff" size="small" />
                  ) : (
                    <Ionicons name="sparkles" size={18} color="#fff" />
                  )}
                  <Text style={styles.planBtnText}>
                    {loading ? 'AI Đang Lập Kế Hoạch...' : 'Khởi Tạo Tour Bằng AI'}
                  </Text>
                </LinearGradient>
              </TouchableOpacity>

              {loading && (
                <View style={styles.progressBox}>
                  <ActivityIndicator color={PRIMARY} size="small" />
                  <Text style={styles.progressText}>{loadingStep}</Text>
                </View>
              )}
            </View>

            {/* Example prompts */}
            {!result && !loading && (
              <View style={styles.examplesCard}>
                <Text style={styles.examplesTitle}>💡 Gợi ý câu lệnh mẫu</Text>
                {examplePrompts.map((ex, i) => (
                  <TouchableOpacity
                    key={i}
                    style={styles.exampleBtn}
                    onPress={() => setPrompt(ex.slice(3))}
                    activeOpacity={0.7}
                  >
                    <Text style={styles.exampleText}>{ex}</Text>
                    <Ionicons name="chevron-forward" size={16} color={TEXT_SECONDARY} />
                  </TouchableOpacity>
                ))}
              </View>
            )}

            {/* Error Card */}
            {error && (
              <View style={styles.errorCard}>
                <Ionicons name="alert-circle" size={22} color="#EF4444" />
                <Text style={styles.errorText}>{error}</Text>
              </View>
            )}

            {/* Results */}
            {result && (
              <View>
                {/* Trip Summary Card */}
                <View style={styles.summaryCard}>
                  <LinearGradient colors={['#064E3B', '#065F46']} style={styles.summaryHeader}>
                    <Ionicons name="checkmark-circle" size={24} color={SUCCESS} />
                    <View style={{ flex: 1 }}>
                      <Text style={styles.summaryTitle}>Tour {result.destination}</Text>
                      <Text style={styles.summarySub}>Mã tour #{result.trip_id} • Phiên bản v{result.version}</Text>
                    </View>
                  </LinearGradient>

                  <View style={styles.summaryGrid}>
                    <View style={styles.summaryItem}>
                      <Text style={styles.summaryLabel}>🛫 Khởi hành từ</Text>
                      <Text style={styles.summaryValue}>{result.origin || 'Việt Nam'}</Text>
                    </View>
                    <View style={styles.summaryItem}>
                      <Text style={styles.summaryLabel}>🛬 Điểm đến</Text>
                      <Text style={styles.summaryValue}>{result.destination}</Text>
                    </View>
                    <View style={styles.summaryItem}>
                      <Text style={styles.summaryLabel}>💰 Chi phí ước tính</Text>
                      <Text style={[styles.summaryValue, { color: SUCCESS }]}>
                        {Number(result.total_cost || 0).toLocaleString()} VND
                      </Text>
                    </View>
                    <View style={styles.summaryItem}>
                      <Text style={styles.summaryLabel}>📅 Số ngày</Text>
                      <Text style={styles.summaryValue}>{daysList.length} ngày</Text>
                    </View>
                  </View>

                  {/* Actions: View in Itinerary or PDF */}
                  <View style={styles.actionRow}>
                    <TouchableOpacity
                      style={styles.viewItineraryBtn}
                      onPress={() => router.push('/(tabs)/itinerary')}
                    >
                      <Ionicons name="calendar-outline" size={16} color="#fff" />
                      <Text style={styles.btnText}>Xem Trong Lịch Trình</Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={styles.pdfBtn}
                      onPress={() => tripSync.downloadPdf(result.trip_id)}
                    >
                      <Ionicons name="document-text-outline" size={16} color="#38BDF8" />
                      <Text style={[styles.btnText, { color: '#38BDF8' }]}>Xuất PDF</Text>
                    </TouchableOpacity>
                  </View>
                </View>

                {/* Day-by-Day Itinerary Items */}
                {daysList.map((day: ItineraryDayData, idx: number) => (
                  <View key={idx} style={styles.dayCard}>
                    <LinearGradient
                      colors={['#1E3A5F', '#1D4ED8']}
                      style={styles.dayHeader}
                      start={{ x: 0, y: 0 }}
                      end={{ x: 1, y: 0 }}
                    >
                      <Text style={styles.dayTitle}>📅 Ngày {day.day_number} — {day.date}</Text>
                      {day.city ? <Text style={styles.dayCity}>📍 {day.city}</Text> : null}
                    </LinearGradient>

                    {day.items?.map((item: ItineraryItemData, iIdx: number) => (
                      <View key={iIdx} style={styles.itemRow}>
                        <View style={styles.itemContent}>
                          <Text style={styles.itemTime}>🕐 {item.start_time} – {item.end_time}</Text>
                          <Text style={styles.itemTitle}>{item.title}</Text>
                          {item.location ? (
                            <Text style={styles.itemLocation}>📍 {item.location}</Text>
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

                        {/* Replan Button */}
                        <TouchableOpacity
                          style={styles.editBtn}
                          onPress={() => setReplanItem(item)}
                        >
                          <Ionicons name="pencil" size={14} color={PRIMARY} />
                          <Text style={styles.editBtnText}>Sửa</Text>
                        </TouchableOpacity>
                      </View>
                    ))}
                  </View>
                ))}
              </View>
            )}
          </ScrollView>
        </KeyboardAvoidingView>

        {/* Replan Modal */}
        {replanItem && result && (
          <ReplanModal
            visible={!!replanItem}
            tripId={result.trip_id}
            item={replanItem}
            onClose={() => setReplanItem(null)}
            onSuccess={(updated) => {
              setResult((prev: any) => ({ ...prev, itinerary: updated, version: (prev?.version || 1) + 1 }));
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
  inputCard: {
    backgroundColor: CARD_BG,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: BORDER,
  },
  inputLabel: { color: TEXT_PRIMARY, fontWeight: '700', fontSize: 15, marginBottom: 10 },
  textInput: {
    backgroundColor: '#0F172A',
    borderRadius: 12,
    padding: 14,
    color: TEXT_PRIMARY,
    fontSize: 15,
    minHeight: 110,
    borderWidth: 1,
    borderColor: BORDER,
    marginBottom: 14,
  },
  planBtn: { borderRadius: 12, overflow: 'hidden' },
  planBtnDisabled: { opacity: 0.6 },
  planBtnGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    gap: 8,
  },
  planBtnText: { color: '#fff', fontWeight: '800', fontSize: 16 },
  progressBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0F172A',
    borderRadius: 10,
    padding: 12,
    marginTop: 12,
    gap: 10,
    borderWidth: 1,
    borderColor: '#1E3A5F',
  },
  progressText: { color: '#BAE6FD', fontSize: 13, flex: 1 },
  examplesCard: {
    backgroundColor: CARD_BG,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: BORDER,
  },
  examplesTitle: { color: TEXT_PRIMARY, fontWeight: '700', fontSize: 15, marginBottom: 12 },
  exampleBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#0F172A',
    borderRadius: 10,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#1E3A5F',
  },
  exampleText: { color: TEXT_SECONDARY, fontSize: 13, flex: 1 },
  errorCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#450A0A',
    borderRadius: 12,
    padding: 14,
    gap: 10,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#EF4444',
  },
  errorText: { color: '#FCA5A5', flex: 1, fontSize: 14 },
  summaryCard: {
    backgroundColor: CARD_BG,
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#065F46',
  },
  summaryHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
    gap: 10,
  },
  summaryTitle: { color: '#fff', fontWeight: '800', fontSize: 17 },
  summarySub: { color: '#A7F3D0', fontSize: 11, marginTop: 2 },
  summaryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 14,
    gap: 10,
  },
  summaryItem: {
    width: '47%',
    backgroundColor: '#0F172A',
    borderRadius: 10,
    padding: 10,
  },
  summaryLabel: { color: TEXT_SECONDARY, fontSize: 12, marginBottom: 4 },
  summaryValue: { color: TEXT_PRIMARY, fontWeight: '700', fontSize: 13 },
  actionRow: {
    flexDirection: 'row',
    padding: 12,
    paddingTop: 0,
    gap: 10,
  },
  viewItineraryBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: PRIMARY,
    borderRadius: 10,
    paddingVertical: 10,
    gap: 6,
  },
  pdfBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#0F172A',
    borderRadius: 10,
    paddingVertical: 10,
    gap: 6,
    borderWidth: 1,
    borderColor: '#0284C7',
  },
  btnText: { color: '#fff', fontWeight: '700', fontSize: 13 },
  dayCard: {
    backgroundColor: CARD_BG,
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 12,
    borderWidth: 1,
    borderColor: BORDER,
  },
  dayHeader: { padding: 12 },
  dayTitle: { color: '#fff', fontWeight: '800', fontSize: 15 },
  dayCity: { color: '#BAE6FD', fontSize: 12, marginTop: 2 },
  itemRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#1E293B',
  },
  itemContent: { flex: 1 },
  itemTime: { color: PRIMARY, fontSize: 12, fontWeight: '700', marginBottom: 2 },
  itemTitle: { color: TEXT_PRIMARY, fontWeight: '700', fontSize: 14, marginBottom: 2 },
  itemLocation: { color: TEXT_SECONDARY, fontSize: 12, marginBottom: 2 },
  itemCost: { color: SUCCESS, fontSize: 12, fontWeight: '700' },
  itemNotes: { color: WARNING, fontSize: 12, fontStyle: 'italic', marginTop: 4 },
  editBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0F172A',
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingVertical: 5,
    gap: 4,
    borderWidth: 1,
    borderColor: PRIMARY,
    marginLeft: 8,
  },
  editBtnText: { color: PRIMARY, fontSize: 11, fontWeight: '700' },
});
