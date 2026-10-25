import React, { useState } from 'react';
import {
  Modal,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { tripSync } from '../services/tripSync';

interface ReplanModalProps {
  visible: boolean;
  tripId: number;
  item: any;
  onClose: () => void;
  onSuccess: (updatedItinerary: any) => void;
}

const PRIMARY = '#0284C7';
const BG_DARK = '#0F172A';
const CARD_BG = '#1E293B';
const BORDER = '#334155';
const TEXT_PRIMARY = '#F1F5F9';
const TEXT_SECONDARY = '#94A3B8';

export const ReplanModal: React.FC<ReplanModalProps> = ({
  visible,
  tripId,
  item,
  onClose,
  onSuccess,
}) => {
  const [title, setTitle] = useState(item?.title || item?.activity_name || '');
  const [startTime, setStartTime] = useState(item?.start_time || '09:00');
  const [endTime, setEndTime] = useState(item?.end_time || '11:00');
  const [cost, setCost] = useState(String(item?.estimated_cost || item?.cost || '0'));
  const [notes, setNotes] = useState(item?.notes || '');
  const [customPrompt, setCustomPrompt] = useState('');
  const [loading, setLoading] = useState(false);

  const handleReplan = async () => {
    setLoading(true);
    try {
      const prompt = customPrompt.trim() || `Điều chỉnh mục "${title}" vào lúc ${startTime} - ${endTime}`;
      const modifiedPayload = {
        id: item?.id,
        title,
        start_time: startTime,
        end_time: endTime,
        estimated_cost: parseFloat(cost) || 0,
        notes,
      };

      const res = await tripSync.replanItem(tripId, prompt, modifiedPayload);
      Alert.alert('Thành công', 'Lịch trình đã được AI tái cấu trúc và lưu vào hệ thống!');
      onSuccess(res.itinerary);
      onClose();
    } catch (err: any) {
      Alert.alert('Lỗi', err.message || 'Không thể điều chỉnh lịch trình.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal visible={visible} animationType="slide" transparent onRequestClose={onClose}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.overlay}
      >
        <View style={styles.content}>
          <View style={styles.header}>
            <View>
              <Text style={styles.title}>Sửa Mục Lịch Trình (AI Replan)</Text>
              <Text style={styles.sub}>AI sẽ tự động tính toán lại thời gian & ngân sách</Text>
            </View>
            <TouchableOpacity onPress={onClose}>
              <Ionicons name="close" size={22} color={TEXT_SECONDARY} />
            </TouchableOpacity>
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Tên hoạt động / Địa điểm</Text>
            <TextInput
              style={styles.input}
              value={title}
              onChangeText={setTitle}
              placeholder="Tham quan bảo tàng..."
              placeholderTextColor="#64748B"
            />
          </View>

          <View style={styles.row}>
            <View style={[styles.inputGroup, { flex: 1 }]}>
              <Text style={styles.label}>Bắt đầu</Text>
              <TextInput
                style={styles.input}
                value={startTime}
                onChangeText={setStartTime}
                placeholder="09:00"
                placeholderTextColor="#64748B"
              />
            </View>
            <View style={[styles.inputGroup, { flex: 1 }]}>
              <Text style={styles.label}>Kết thúc</Text>
              <TextInput
                style={styles.input}
                value={endTime}
                onChangeText={setEndTime}
                placeholder="11:30"
                placeholderTextColor="#64748B"
              />
            </View>
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Chi phí ước tính (VND)</Text>
            <TextInput
              style={styles.input}
              value={cost}
              onChangeText={setCost}
              keyboardType="numeric"
              placeholder="250000"
              placeholderTextColor="#64748B"
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Yêu cầu tùy chỉnh cho AI (Tùy chọn)</Text>
            <TextInput
              style={styles.input}
              value={customPrompt}
              onChangeText={setCustomPrompt}
              placeholder="VD: Đổi sang buổi chiều để kết hợp ăn trưa..."
              placeholderTextColor="#64748B"
            />
          </View>

          <TouchableOpacity style={styles.submitBtn} onPress={handleReplan} disabled={loading}>
            <LinearGradient
              colors={[PRIMARY, '#0369A1']}
              style={styles.gradient}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
            >
              {loading ? (
                <ActivityIndicator color="#fff" size="small" />
              ) : (
                <Ionicons name="sparkles" size={18} color="#fff" />
              )}
              <Text style={styles.submitText}>
                {loading ? 'AI đang tính toán...' : 'Áp Dụng & Tái Lập Lịch Trình'}
              </Text>
            </LinearGradient>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'flex-end',
  },
  content: {
    backgroundColor: CARD_BG,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    borderWidth: 1,
    borderColor: BORDER,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  title: { fontSize: 18, fontWeight: '800', color: TEXT_PRIMARY },
  sub: { fontSize: 12, color: TEXT_SECONDARY, marginTop: 4 },
  row: { flexDirection: 'row', gap: 12 },
  inputGroup: { marginBottom: 14 },
  label: { color: TEXT_PRIMARY, fontSize: 13, fontWeight: '600', marginBottom: 6 },
  input: {
    backgroundColor: BG_DARK,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 12,
    color: TEXT_PRIMARY,
    fontSize: 14,
    borderWidth: 1,
    borderColor: BORDER,
  },
  submitBtn: { borderRadius: 12, overflow: 'hidden', marginTop: 8 },
  gradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    gap: 8,
  },
  submitText: { color: '#fff', fontWeight: '800', fontSize: 15 },
});
