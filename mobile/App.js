import React, { useState } from 'react';
import { StyleSheet, Text, View, SafeAreaView, TouchableOpacity, ScrollView, TextInput } from 'react-native';
import { StatusBar } from 'expo-status-bar';

export default function App() {
  const [activeTab, setActiveTab] = useState('itinerary');
  const [query, setQuery] = useState('');
  const [assistantReply, setAssistantReply] = useState('');

  const sampleItinerary = [
    { time: '08:00', title: 'Bay VN123 từ Hà Nội -> Đà Nẵng', type: 'Chuyến bay' },
    { time: '12:00', title: 'Ăn trưa Bánh Xèo Bà Dưỡng', type: 'Nhà hàng' },
    { time: '14:00', title: 'Check-in Khách sạn Mỹ Khê Resort', type: 'Khách sạn' },
    { time: '15:30', title: 'Tắm biển & dạo chơi Mỹ Khê', type: 'Tham quan' },
    { time: '19:00', title: 'Bữa tối Hải Sản Sông Hàn', type: 'Nhà hàng' },
  ];

  const handleAskAssistant = () => {
    if (!query.trim()) return;
    setAssistantReply(`AI Support: Gần vị trí của bạn có Chợ Đêm Sơn Trà (cách 1.1km). Bạn có thể thử các món ăn vặt và xem Cầu Rồng phun lửa lúc 21:00!`);
    setQuery('');
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />
      
      {/* Mobile Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Travel Agent Mobile</Text>
        <Text style={styles.headerSub}>Hành trình Đà Nẵng (3 Ngày 2 Đêm)</Text>
      </View>

      {/* Tabs */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'itinerary' && styles.tabActive]}
          onPress={() => setActiveTab('itinerary')}
        >
          <Text style={[styles.tabText, activeTab === 'itinerary' && styles.tabTextActive]}>Lịch Trình</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tab, activeTab === 'assistant' && styles.tabActive]}
          onPress={() => setActiveTab('assistant')}
        >
          <Text style={[styles.tabText, activeTab === 'assistant' && styles.tabTextActive]}>AI Assistant</Text>
        </TouchableOpacity>
      </View>

      {/* Content */}
      {activeTab === 'itinerary' ? (
        <ScrollView style={styles.content}>
          <Text style={styles.sectionTitle}>Ngày 1 — Khám Phá Đà Nẵng</Text>
          {sampleItinerary.map((item, index) => (
            <View key={index} style={styles.card}>
              <View style={styles.timeBadge}>
                <Text style={styles.timeText}>{item.time}</Text>
              </View>
              <View style={styles.cardBody}>
                <Text style={styles.cardTitle}>{item.title}</Text>
                <Text style={styles.cardType}>{item.type}</Text>
              </View>
            </View>
          ))}
        </ScrollView>
      ) : (
        <View style={styles.content}>
          <Text style={styles.sectionTitle}>Hỏi AI Agent Trong Chuyến Đi</Text>
          <TextInput
            style={styles.input}
            placeholder="VD: Gần đây có địa điểm ăn vặt nào ngon không?..."
            value={query}
            onChangeText={setQuery}
          />
          <TouchableOpacity style={styles.button} onPress={handleAskAssistant}>
            <Text style={styles.buttonText}>Gửi Câu Hỏi</Text>
          </TouchableOpacity>

          {assistantReply ? (
            <View style={styles.replyBox}>
              <Text style={styles.replyText}>{assistantReply}</Text>
            </View>
          ) : null}
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    backgroundColor: '#0284C7',
    padding: 20,
    paddingTop: 40,
  },
  headerTitle: {
    color: '#FFF',
    fontSize: 22,
    fontWeight: 'bold',
  },
  headerSub: {
    color: '#E0F2FE',
    fontSize: 14,
    marginTop: 4,
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  tab: {
    flex: 1,
    paddingVertical: 14,
    alignItems: 'center',
  },
  tabActive: {
    borderBottomWidth: 3,
    borderBottomColor: '#0284C7',
  },
  tabText: {
    color: '#64748B',
    fontWeight: '600',
  },
  tabTextActive: {
    color: '#0284C7',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#0F172A',
    marginBottom: 12,
  },
  card: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  timeBadge: {
    backgroundColor: '#E0F2FE',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    marginRight: 12,
  },
  timeText: {
    color: '#0369A1',
    fontWeight: 'bold',
    fontSize: 12,
  },
  cardBody: {
    flex: 1,
  },
  cardTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1E293B',
  },
  cardType: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  input: {
    backgroundColor: '#FFF',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: 12,
    padding: 12,
    fontSize: 14,
    marginBottom: 12,
  },
  button: {
    backgroundColor: '#0284C7',
    padding: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  buttonText: {
    color: '#FFF',
    fontWeight: 'bold',
  },
  replyBox: {
    backgroundColor: '#F0F9FF',
    borderColor: '#BAE6FD',
    borderWidth: 1,
    padding: 14,
    borderRadius: 12,
    marginTop: 16,
  },
  replyText: {
    color: '#0369A1',
    fontSize: 14,
    lineHeight: 20,
  },
});
