import React, { useState, useEffect } from 'react';
import {
  Modal,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import {
  getApiBaseUrl,
  setApiBaseUrl,
  resetApiBaseUrl,
  testServerConnection,
} from '../api/index';
import { realtimeClient } from '../services/realtime';

interface ServerConfigModalProps {
  visible: boolean;
  onClose: () => void;
  onServerChanged?: () => void;
}

const PRIMARY = '#0284C7';
const BG_DARK = '#0F172A';
const CARD_BG = '#1E293B';
const BORDER = '#334155';
const TEXT_PRIMARY = '#F1F5F9';
const TEXT_SECONDARY = '#94A3B8';
const SUCCESS = '#10B981';
const DANGER = '#EF4444';

export const ServerConfigModal: React.FC<ServerConfigModalProps> = ({
  visible,
  onClose,
  onServerChanged,
}) => {
  const [url, setUrl] = useState('');
  const [testing, setTesting] = useState(false);
  const [statusResult, setStatusResult] = useState<{ ok: boolean; message: string } | null>(null);

  useEffect(() => {
    if (visible) {
      setUrl(getApiBaseUrl());
      setStatusResult(null);
    }
  }, [visible]);

  const handleTest = async () => {
    setTesting(true);
    setStatusResult(null);
    try {
      const res = await testServerConnection();
      setStatusResult({ ok: res.ok, message: res.ok ? 'Kết nối thành công (Backend Online)' : res.message });
    } catch (err: any) {
      setStatusResult({ ok: false, message: err.message || 'Không thể kết nối máy chủ' });
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    if (!url.trim()) return;
    try {
      await setApiBaseUrl(url);
      realtimeClient.connect();
      Alert.alert('Thành công', `Đã lưu địa chỉ máy chủ:\n${getApiBaseUrl()}`);
      if (onServerChanged) onServerChanged();
      onClose();
    } catch {
      Alert.alert('Lỗi', 'Không thể lưu địa chỉ máy chủ.');
    }
  };

  const handleReset = async () => {
    const defaultUrl = await resetApiBaseUrl();
    setUrl(defaultUrl);
    realtimeClient.connect();
    Alert.alert('Đã khôi phục', `Đã tự động nhận diện IP máy chủ:\n${defaultUrl}`);
    if (onServerChanged) onServerChanged();
  };

  return (
    <Modal visible={visible} animationType="slide" transparent onRequestClose={onClose}>
      <View style={styles.overlay}>
        <View style={styles.content}>
          {/* Header */}
          <View style={styles.header}>
            <View>
              <Text style={styles.title}>Cấu Hình Máy Chủ Backend</Text>
              <Text style={styles.subtitle}>Kết nối điện thoại thật với máy tính chạy server</Text>
            </View>
            <TouchableOpacity onPress={onClose} style={styles.closeBtn}>
              <Ionicons name="close" size={22} color={TEXT_SECONDARY} />
            </TouchableOpacity>
          </View>

          {/* Description */}
          <View style={styles.infoBox}>
            <Ionicons name="information-circle" size={20} color={PRIMARY} />
            <Text style={styles.infoText}>
              Khi chạy Expo Go trên điện thoại thật, ứng dụng cần IP mạng Wi-Fi (ví dụ: <Text style={{ fontWeight: '700' }}>http://192.168.1.15:8000</Text>) thay vì localhost.
            </Text>
          </View>

          {/* Input */}
          <Text style={styles.inputLabel}>URL Backend FastAPI:</Text>
          <TextInput
            style={styles.input}
            value={url}
            onChangeText={setUrl}
            placeholder="http://192.168.1.15:8000/api/v1"
            placeholderTextColor="#64748B"
            autoCapitalize="none"
            autoCorrect={false}
          />

          {/* Test connection result */}
          {statusResult && (
            <View style={[styles.statusBox, { backgroundColor: statusResult.ok ? '#064E3B' : '#450A0A' }]}>
              <Ionicons
                name={statusResult.ok ? 'checkmark-circle' : 'alert-circle'}
                size={18}
                color={statusResult.ok ? SUCCESS : DANGER}
              />
              <Text style={[styles.statusText, { color: statusResult.ok ? '#A7F3D0' : '#FECACA' }]}>
                {statusResult.message}
              </Text>
            </View>
          )}

          {/* Buttons */}
          <View style={styles.actionRow}>
            <TouchableOpacity
              style={[styles.testBtn, testing && { opacity: 0.7 }]}
              onPress={handleTest}
              disabled={testing}
            >
              {testing ? (
                <ActivityIndicator size="small" color={PRIMARY} />
              ) : (
                <Ionicons name="wifi" size={16} color={PRIMARY} />
              )}
              <Text style={styles.testBtnText}>Kiểm Tra Ping</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.resetBtn} onPress={handleReset}>
              <Ionicons name="refresh" size={16} color={TEXT_SECONDARY} />
              <Text style={styles.resetBtnText}>Tự Nhận Diện</Text>
            </TouchableOpacity>
          </View>

          <TouchableOpacity style={styles.saveBtn} onPress={handleSave}>
            <LinearGradient
              colors={[PRIMARY, '#0369A1']}
              style={styles.saveGradient}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
            >
              <Text style={styles.saveBtnText}>Lưu & Áp Dụng Ngay</Text>
            </LinearGradient>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'center',
    padding: 20,
  },
  content: {
    backgroundColor: CARD_BG,
    borderRadius: 20,
    padding: 20,
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
  subtitle: { fontSize: 12, color: TEXT_SECONDARY, marginTop: 2 },
  closeBtn: { padding: 4 },
  infoBox: {
    flexDirection: 'row',
    backgroundColor: '#0F172A',
    borderRadius: 12,
    padding: 12,
    gap: 10,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: BORDER,
  },
  infoText: { color: TEXT_SECONDARY, fontSize: 12, flex: 1, lineHeight: 18 },
  inputLabel: { color: TEXT_PRIMARY, fontSize: 13, fontWeight: '700', marginBottom: 6 },
  input: {
    backgroundColor: BG_DARK,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 12,
    color: TEXT_PRIMARY,
    fontSize: 14,
    borderWidth: 1,
    borderColor: BORDER,
    marginBottom: 12,
  },
  statusBox: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 10,
    padding: 10,
    gap: 8,
    marginBottom: 14,
  },
  statusText: { fontSize: 12, fontWeight: '600', flex: 1 },
  actionRow: { flexDirection: 'row', gap: 10, marginBottom: 16 },
  testBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#0F172A',
    borderRadius: 10,
    paddingVertical: 12,
    gap: 6,
    borderWidth: 1,
    borderColor: PRIMARY,
  },
  testBtnText: { color: PRIMARY, fontWeight: '700', fontSize: 13 },
  resetBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#0F172A',
    borderRadius: 10,
    paddingVertical: 12,
    gap: 6,
    borderWidth: 1,
    borderColor: BORDER,
  },
  resetBtnText: { color: TEXT_SECONDARY, fontWeight: '600', fontSize: 13 },
  saveBtn: { borderRadius: 12, overflow: 'hidden' },
  saveGradient: { paddingVertical: 14, alignItems: 'center' },
  saveBtnText: { color: '#fff', fontWeight: '800', fontSize: 15 },
});
