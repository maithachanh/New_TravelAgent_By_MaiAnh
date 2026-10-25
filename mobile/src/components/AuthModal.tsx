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
import { useAuth } from '../context/AuthContext';

interface AuthModalProps {
  visible: boolean;
  onClose: () => void;
}

const PRIMARY = '#0284C7';
const BG_DARK = '#0F172A';
const CARD_BG = '#1E293B';
const BORDER = '#334155';
const TEXT_PRIMARY = '#F1F5F9';
const TEXT_SECONDARY = '#94A3B8';

export const AuthModal: React.FC<AuthModalProps> = ({ visible, onClose }) => {
  const { user, isAuthenticated, login, register, logout, quickDemoLogin } = useAuth();
  const [tab, setTab] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!email.trim() || !password.trim()) {
      Alert.alert('Lỗi', 'Vui lòng nhập đầy đủ Email và Mật khẩu.');
      return;
    }
    setLoading(true);
    try {
      if (tab === 'login') {
        await login(email.trim(), password.trim());
        Alert.alert('Thành công', 'Đăng nhập thành công!');
      } else {
        if (!fullName.trim()) {
          Alert.alert('Lỗi', 'Vui lòng nhập Họ và Tên.');
          setLoading(false);
          return;
        }
        await register(email.trim(), password.trim(), fullName.trim());
        Alert.alert('Thành công', 'Đăng ký và đăng nhập thành công!');
      }
      onClose();
    } catch (err: any) {
      Alert.alert('Thất bại', err.message || 'Xác thực thất bại. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemo = async () => {
    setLoading(true);
    try {
      await quickDemoLogin();
      Alert.alert('Thành công', 'Đã đăng nhập bằng tài khoản Quản trị Demo!');
      onClose();
    } catch (err: any) {
      Alert.alert('Lỗi', err.message || 'Không thể đăng nhập tài khoản demo.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    Alert.alert('Đã đăng xuất', 'Bạn đã đăng xuất thành công.');
    onClose();
  };

  return (
    <Modal visible={visible} animationType="slide" transparent onRequestClose={onClose}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.modalOverlay}
      >
        <View style={styles.modalContent}>
          {/* Header */}
          <View style={styles.header}>
            <View>
              <Text style={styles.headerTitle}>
                {isAuthenticated ? 'Tài Khoản Du Lịch' : tab === 'login' ? 'Đăng Nhập' : 'Tạo Tài Khoản'}
              </Text>
              <Text style={styles.headerSub}>
                {isAuthenticated ? 'Thông tin cá nhân & cài đặt' : 'Đồng bộ hóa lịch trình trên mọi thiết bị'}
              </Text>
            </View>
            <TouchableOpacity onPress={onClose} style={styles.closeBtn}>
              <Ionicons name="close" size={22} color={TEXT_SECONDARY} />
            </TouchableOpacity>
          </View>

          {isAuthenticated ? (
            /* User profile view */
            <View style={styles.profileBox}>
              <View style={styles.avatarRow}>
                <View style={styles.avatar}>
                  <Text style={styles.avatarText}>
                    {user?.full_name ? user.full_name[0].toUpperCase() : 'U'}
                  </Text>
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={styles.userName}>{user?.full_name || 'Khách Du Lịch'}</Text>
                  <Text style={styles.userEmail}>{user?.email}</Text>
                  <View style={styles.badge}>
                    <Text style={styles.badgeText}>Thành viên AI Agent 2.0</Text>
                  </View>
                </View>
              </View>

              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Ngôn ngữ:</Text>
                <Text style={styles.infoValue}>{user?.language === 'vi' ? '🇻🇳 Tiếng Việt' : user?.language}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Tiền tệ mặc định:</Text>
                <Text style={styles.infoValue}>{user?.currency || 'VND'}</Text>
              </View>

              <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
                <Ionicons name="log-out-outline" size={18} color="#EF4444" />
                <Text style={styles.logoutText}>Đăng Xuất</Text>
              </TouchableOpacity>
            </View>
          ) : (
            /* Login / Register form */
            <View>
              {/* Tab switch */}
              <View style={styles.tabBar}>
                <TouchableOpacity
                  style={[styles.tabItem, tab === 'login' && styles.tabActive]}
                  onPress={() => setTab('login')}
                >
                  <Text style={[styles.tabText, tab === 'login' && styles.tabTextActive]}>
                    Đăng Nhập
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.tabItem, tab === 'register' && styles.tabActive]}
                  onPress={() => setTab('register')}
                >
                  <Text style={[styles.tabText, tab === 'register' && styles.tabTextActive]}>
                    Đăng Ký
                  </Text>
                </TouchableOpacity>
              </View>

              {tab === 'register' && (
                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>Họ và Tên</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="Nguyễn Văn A"
                    placeholderTextColor="#64748B"
                    value={fullName}
                    onChangeText={setFullName}
                  />
                </View>
              )}

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Địa chỉ Email</Text>
                <TextInput
                  style={styles.input}
                  placeholder="traveler@example.com"
                  placeholderTextColor="#64748B"
                  value={email}
                  onChangeText={setEmail}
                  autoCapitalize="none"
                  keyboardType="email-address"
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Mật khẩu</Text>
                <TextInput
                  style={styles.input}
                  placeholder="••••••••"
                  placeholderTextColor="#64748B"
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                />
              </View>

              <TouchableOpacity
                style={styles.submitBtn}
                onPress={handleSubmit}
                disabled={loading}
              >
                <LinearGradient
                  colors={[PRIMARY, '#0369A1']}
                  style={styles.submitGradient}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                >
                  {loading ? (
                    <ActivityIndicator color="#fff" size="small" />
                  ) : (
                    <Text style={styles.submitText}>
                      {tab === 'login' ? 'Đăng Nhập' : 'Tạo Tài Khoản Mới'}
                    </Text>
                  )}
                </LinearGradient>
              </TouchableOpacity>

              {/* Demo 1-click login */}
              <TouchableOpacity
                style={styles.demoBtn}
                onPress={handleDemo}
                disabled={loading}
              >
                <Ionicons name="flash" size={16} color="#F59E0B" />
                <Text style={styles.demoText}>Dùng Thử Nhanh (Demo Account)</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
};

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'flex-end',
  },
  modalContent: {
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
    marginBottom: 20,
  },
  headerTitle: { fontSize: 20, fontWeight: '800', color: TEXT_PRIMARY },
  headerSub: { fontSize: 13, color: TEXT_SECONDARY, marginTop: 4 },
  closeBtn: { padding: 4 },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: BG_DARK,
    borderRadius: 12,
    padding: 4,
    marginBottom: 20,
  },
  tabItem: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    borderRadius: 10,
  },
  tabActive: { backgroundColor: PRIMARY },
  tabText: { color: TEXT_SECONDARY, fontWeight: '600', fontSize: 14 },
  tabTextActive: { color: '#fff' },
  inputGroup: { marginBottom: 16 },
  inputLabel: { color: TEXT_PRIMARY, fontSize: 13, fontWeight: '600', marginBottom: 6 },
  input: {
    backgroundColor: BG_DARK,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 12,
    color: TEXT_PRIMARY,
    fontSize: 15,
    borderWidth: 1,
    borderColor: BORDER,
  },
  submitBtn: { borderRadius: 12, overflow: 'hidden', marginTop: 8 },
  submitGradient: { paddingVertical: 14, alignItems: 'center' },
  submitText: { color: '#fff', fontWeight: '700', fontSize: 16 },
  demoBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    marginTop: 12,
    borderRadius: 12,
    backgroundColor: '#0F172A',
    borderWidth: 1,
    borderColor: '#334155',
    gap: 8,
  },
  demoText: { color: '#FCD34D', fontWeight: '600', fontSize: 13 },
  profileBox: { paddingVertical: 8 },
  avatarRow: { flexDirection: 'row', alignItems: 'center', gap: 14, marginBottom: 20 },
  avatar: {
    width: 54,
    height: 54,
    borderRadius: 27,
    backgroundColor: PRIMARY,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: { color: '#fff', fontSize: 22, fontWeight: '800' },
  userName: { color: TEXT_PRIMARY, fontSize: 18, fontWeight: '800' },
  userEmail: { color: TEXT_SECONDARY, fontSize: 13, marginTop: 2 },
  badge: {
    backgroundColor: '#065F46',
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingVertical: 2,
    alignSelf: 'flex-start',
    marginTop: 6,
  },
  badgeText: { color: '#6EE7B7', fontSize: 11, fontWeight: '700' },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
  },
  infoLabel: { color: TEXT_SECONDARY, fontSize: 14 },
  infoValue: { color: TEXT_PRIMARY, fontWeight: '600', fontSize: 14 },
  logoutBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 12,
    backgroundColor: '#450A0A',
    marginTop: 24,
    gap: 8,
    borderWidth: 1,
    borderColor: '#991B1B',
  },
  logoutText: { color: '#F87171', fontWeight: '700', fontSize: 15 },
});
