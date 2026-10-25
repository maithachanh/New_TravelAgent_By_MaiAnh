import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { askInTripSupportMobile } from '../../src/api/index';
import { NavbarHeader } from '../../src/components/NavbarHeader';

const PRIMARY = '#0284C7';
const BG_DARK = '#0F172A';
const CARD_BG = '#1E293B';
const BORDER = '#334155';
const TEXT_PRIMARY = '#F1F5F9';
const TEXT_SECONDARY = '#94A3B8';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  timestamp: Date;
}

const QUICK_PROMPTS = [
  '🍜 Quán ăn ngon xung quanh đây?',
  '🚇 Cách di chuyển bằng tàu điện ngầm?',
  '💰 Tỷ giá hôm nay?',
  '🏥 Bệnh viện gần nhất ở đâu?',
  '🛍️ Khu mua sắm nổi tiếng nhất?',
  '🗺️ Điểm tham quan nên đến?',
];

export default function AssistantScreen() {
  const [location, setLocation] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      text: '👋 Xin chào! Tôi là trợ lý du lịch AI. Hãy cho tôi biết bạn đang ở đâu và tôi có thể giúp bạn tìm nhà hàng, điểm tham quan, hướng dẫn di chuyển, và nhiều hơn nữa!',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = React.useRef<ScrollView>(null);

  const sendMessage = async (text?: string) => {
    const msgText = (text || input).trim();
    if (!msgText) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      text: msgText,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const resp = await askInTripSupportMobile(msgText, location || undefined);
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        text: resp.response || resp.answer || 'Tôi không tìm được thông tin. Vui lòng thử lại!',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch {
      const errMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        text: '❌ Xin lỗi, có lỗi kết nối. Vui lòng kiểm tra mạng và thử lại.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setLoading(false);
      setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 200);
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <LinearGradient colors={[BG_DARK, '#0C1825']} style={styles.gradient}>
        <NavbarHeader title="🤖 Trợ Lý Live AI" subtitle="Tư vấn điểm ăn uống, di chuyển & hỗ trợ 24/7" />

        {/* Location input */}
        <View style={styles.locationBar}>
          <Ionicons name="location" size={16} color={PRIMARY} />
          <TextInput
            style={styles.locationInput}
            value={location}
            onChangeText={setLocation}
            placeholder="Nhập vị trí hiện tại của bạn (vd: Tokyo, Seoul...)"
            placeholderTextColor="#64748B"
          />
          {location ? (
            <TouchableOpacity onPress={() => setLocation('')}>
              <Ionicons name="close-circle" size={16} color="#64748B" />
            </TouchableOpacity>
          ) : null}
        </View>

        {/* Quick prompts */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.quickPromptsContainer}
        >
          {QUICK_PROMPTS.map((qp, i) => (
            <TouchableOpacity
              key={i}
              style={styles.quickPromptBtn}
              onPress={() => sendMessage(qp)}
              activeOpacity={0.7}
            >
              <Text style={styles.quickPromptText}>{qp}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Messages */}
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}
          style={{ flex: 1 }}
          keyboardVerticalOffset={120}
        >
          <ScrollView
            ref={scrollRef}
            style={styles.messagesList}
            contentContainerStyle={styles.messagesContent}
            showsVerticalScrollIndicator={false}
            onContentSizeChange={() => scrollRef.current?.scrollToEnd({ animated: true })}
          >
            {messages.map(msg => (
              <View
                key={msg.id}
                style={[
                  styles.messageBubble,
                  msg.role === 'user' ? styles.userBubble : styles.aiBubble,
                ]}
              >
                {msg.role === 'assistant' && (
                  <View style={styles.aiAvatar}>
                    <Text style={styles.aiAvatarText}>🤖</Text>
                  </View>
                )}
                <View
                  style={[
                    styles.bubbleContent,
                    msg.role === 'user' ? styles.userBubbleContent : styles.aiBubbleContent,
                  ]}
                >
                  <Text style={msg.role === 'user' ? styles.userText : styles.aiText}>
                    {msg.text}
                  </Text>
                  <Text style={styles.timestamp}>
                    {msg.timestamp.toLocaleTimeString('vi-VN', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </Text>
                </View>
              </View>
            ))}
            {loading && (
              <View style={[styles.messageBubble, styles.aiBubble]}>
                <View style={styles.aiAvatar}>
                  <Text style={styles.aiAvatarText}>🤖</Text>
                </View>
                <View style={styles.typingIndicator}>
                  <ActivityIndicator size="small" color={PRIMARY} />
                  <Text style={styles.typingText}>Đang tìm kiếm...</Text>
                </View>
              </View>
            )}
          </ScrollView>

          {/* Input area */}
          <View style={styles.inputBar}>
            <TextInput
              style={styles.messageInput}
              value={input}
              onChangeText={setInput}
              placeholder="Hỏi về địa điểm, nhà hàng, giao thông..."
              placeholderTextColor="#64748B"
              multiline
              maxLength={500}
              onSubmitEditing={() => sendMessage()}
            />
            <TouchableOpacity
              style={[styles.sendBtn, (!input.trim() || loading) && styles.sendBtnDisabled]}
              onPress={() => sendMessage()}
              disabled={!input.trim() || loading}
              activeOpacity={0.8}
            >
              <LinearGradient
                colors={input.trim() && !loading ? [PRIMARY, '#0369A1'] : ['#475569', '#475569']}
                style={styles.sendBtnGradient}
              >
                <Ionicons name="send" size={18} color="#fff" />
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: BG_DARK },
  gradient: { flex: 1 },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: BORDER,
  },
  headerTitle: { fontSize: 20, fontWeight: '800', color: TEXT_PRIMARY },
  headerSubtitle: { fontSize: 12, color: TEXT_SECONDARY, marginTop: 2 },
  statusDot: { width: 10, height: 10, borderRadius: 5 },
  locationBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: CARD_BG,
    marginHorizontal: 16,
    marginTop: 12,
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 10,
    gap: 8,
    borderWidth: 1,
    borderColor: BORDER,
  },
  locationInput: { flex: 1, color: TEXT_PRIMARY, fontSize: 14 },
  quickPromptsContainer: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    gap: 8,
  },
  quickPromptBtn: {
    backgroundColor: '#1D4ED8',
    borderRadius: 20,
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderWidth: 1,
    borderColor: '#2563EB',
  },
  quickPromptText: { color: '#BFDBFE', fontSize: 12, fontWeight: '600' },
  messagesList: { flex: 1 },
  messagesContent: { padding: 16, paddingBottom: 8 },
  messageBubble: {
    flexDirection: 'row',
    marginBottom: 12,
    alignItems: 'flex-end',
  },
  userBubble: { justifyContent: 'flex-end' },
  aiBubble: { justifyContent: 'flex-start' },
  aiAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: CARD_BG,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
    borderWidth: 1,
    borderColor: BORDER,
  },
  aiAvatarText: { fontSize: 16 },
  bubbleContent: {
    maxWidth: '78%',
    borderRadius: 16,
    padding: 12,
  },
  userBubbleContent: {
    backgroundColor: PRIMARY,
    borderBottomRightRadius: 4,
  },
  aiBubbleContent: {
    backgroundColor: CARD_BG,
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: BORDER,
  },
  userText: { color: '#fff', fontSize: 14, lineHeight: 20 },
  aiText: { color: TEXT_PRIMARY, fontSize: 14, lineHeight: 20 },
  timestamp: { color: 'rgba(255,255,255,0.5)', fontSize: 10, marginTop: 4, textAlign: 'right' },
  typingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: CARD_BG,
    borderRadius: 16,
    padding: 12,
    gap: 8,
    borderWidth: 1,
    borderColor: BORDER,
  },
  typingText: { color: TEXT_SECONDARY, fontSize: 13 },
  inputBar: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 10,
    borderTopWidth: 1,
    borderTopColor: BORDER,
    backgroundColor: BG_DARK,
  },
  messageInput: {
    flex: 1,
    backgroundColor: CARD_BG,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    color: TEXT_PRIMARY,
    fontSize: 14,
    maxHeight: 100,
    borderWidth: 1,
    borderColor: BORDER,
  },
  sendBtn: { borderRadius: 22 },
  sendBtnDisabled: { opacity: 0.5 },
  sendBtnGradient: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
