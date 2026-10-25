import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { useRealtime } from '../services/realtime';
import { AuthModal } from './AuthModal';
import { ServerConfigModal } from './ServerConfigModal';

interface NavbarHeaderProps {
  title: string;
  subtitle?: string;
  showBack?: boolean;
  onBack?: () => void;
}

const PRIMARY = '#0284C7';
const CARD_BG = '#1E293B';
const BORDER = '#334155';
const TEXT_PRIMARY = '#F1F5F9';
const TEXT_SECONDARY = '#94A3B8';
const SUCCESS = '#10B981';
const DANGER = '#EF4444';

export const NavbarHeader: React.FC<NavbarHeaderProps> = ({
  title,
  subtitle,
  showBack,
  onBack,
}) => {
  const { user, isAuthenticated } = useAuth();
  const { status, reconnect } = useRealtime();
  const [authVisible, setAuthVisible] = useState(false);
  const [serverVisible, setServerVisible] = useState(false);

  return (
    <>
      <View style={styles.header}>
        {/* Left: Back or Title */}
        <View style={styles.leftContainer}>
          {showBack && onBack ? (
            <TouchableOpacity onPress={onBack} style={styles.backBtn}>
              <Ionicons name="arrow-back" size={22} color={TEXT_PRIMARY} />
            </TouchableOpacity>
          ) : null}
          <View>
            <Text style={styles.title} numberOfLines={1}>{title}</Text>
            {subtitle ? <Text style={styles.subtitle} numberOfLines={1}>{subtitle}</Text> : null}
          </View>
        </View>

        {/* Right: Real-time pill, Server settings, Auth profile */}
        <View style={styles.rightContainer}>
          {/* Real-time status pill */}
          <TouchableOpacity
            style={[
              styles.statusPill,
              { borderColor: status === 'connected' ? SUCCESS : status === 'connecting' ? '#F59E0B' : DANGER },
            ]}
            onPress={reconnect}
            activeOpacity={0.7}
          >
            <View
              style={[
                styles.dot,
                { backgroundColor: status === 'connected' ? SUCCESS : status === 'connecting' ? '#F59E0B' : DANGER },
              ]}
            />
            <Text style={styles.statusText}>
              {status === 'connected' ? 'Live' : status === 'connecting' ? 'Đang nối' : 'Offline'}
            </Text>
          </TouchableOpacity>

          {/* Server Config Button */}
          <TouchableOpacity
            style={styles.iconBtn}
            onPress={() => setServerVisible(true)}
            activeOpacity={0.7}
          >
            <Ionicons name="server-outline" size={18} color={TEXT_SECONDARY} />
          </TouchableOpacity>

          {/* User Auth Avatar / Button */}
          <TouchableOpacity
            style={[styles.userBtn, isAuthenticated && styles.userBtnActive]}
            onPress={() => setAuthVisible(true)}
            activeOpacity={0.7}
          >
            {isAuthenticated && user?.full_name ? (
              <Text style={styles.avatarLetter}>{user.full_name[0].toUpperCase()}</Text>
            ) : (
              <Ionicons name="person-outline" size={17} color={TEXT_SECONDARY} />
            )}
          </TouchableOpacity>
        </View>
      </View>

      <AuthModal visible={authVisible} onClose={() => setAuthVisible(false)} />
      <ServerConfigModal visible={serverVisible} onClose={() => setServerVisible(false)} />
    </>
  );
};

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: BORDER,
  },
  leftContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  backBtn: { padding: 4 },
  title: { fontSize: 18, fontWeight: '800', color: TEXT_PRIMARY },
  subtitle: { fontSize: 11, color: TEXT_SECONDARY, marginTop: 1 },
  rightContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  statusPill: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 14,
    borderWidth: 1,
    backgroundColor: '#0F172A',
    gap: 5,
  },
  dot: { width: 7, height: 7, borderRadius: 3.5 },
  statusText: { fontSize: 10, fontWeight: '700', color: TEXT_SECONDARY },
  iconBtn: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: CARD_BG,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: BORDER,
  },
  userBtn: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: CARD_BG,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: BORDER,
  },
  userBtnActive: {
    backgroundColor: PRIMARY,
    borderColor: PRIMARY,
  },
  avatarLetter: { color: '#fff', fontSize: 14, fontWeight: '800' },
});
