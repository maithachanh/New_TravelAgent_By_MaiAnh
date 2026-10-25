import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as Clipboard from 'expo-clipboard';
import { NavbarHeader } from '../../src/components/NavbarHeader';
import {
  convertCurrencyMobile,
  getAllRatesMobile,
  translateTextMobile,
  CurrencyConvertResponse,
  TranslationResponse,
} from '../../src/api/index';

const PRIMARY = '#0284C7';
const BG_DARK = '#0F172A';
const CARD_BG = '#1E293B';
const BORDER = '#334155';
const TEXT_PRIMARY = '#F1F5F9';
const TEXT_SECONDARY = '#94A3B8';
const SUCCESS = '#10B981';

// Supported translation languages matching web version
const TRANSLATE_LANGUAGES = [
  { code: 'en', flag: '🇺🇸', name: 'English (Tiếng Anh)' },
  { code: 'ja', flag: '🇯🇵', name: '日本語 (Tiếng Nhật)' },
  { code: 'ko', flag: '🇰🇷', name: '한국어 (Tiếng Hàn)' },
  { code: 'th', flag: '🇹🇭', name: 'ภาษาไทย (Tiếng Thái)' },
  { code: 'fr', flag: '🇫🇷', name: 'Français (Tiếng Pháp)' },
  { code: 'zh-CN', flag: '🇨🇳', name: '中文 (Tiếng Trung)' },
  { code: 'de', flag: '🇩🇪', name: 'Deutsch (Tiếng Đức)' },
  { code: 'es', flag: '🇪🇸', name: 'Español (Tiếng TBN)' },
  { code: 'it', flag: '🇮🇹', name: 'Italiano (Tiếng Ý)' },
  { code: 'ru', flag: '🇷🇺', name: 'Русский (Tiếng Nga)' },
];

// Quick travel phrases matching web version
const QUICK_PHRASES = [
  '🍽️ Cho tôi xem thực đơn, làm ơn.',
  '💰 Cái này giá bao nhiêu tiền?',
  '🚻 Nhà vệ sinh ở đâu vậy?',
  '🧾 Làm ơn tính tiền cho tôi.',
  '🗺️ Tôi bị lạc đường, xin hãy giúp tôi.',
  '🏷️ Có giảm giá cho khách du lịch không?',
  '🚕 Tôi muốn gọi một chiếc taxi.',
  '🙏 Cảm ơn bạn rất nhiều.',
  '🏨 Tôi muốn nhận phòng khách sạn.',
  '🏥 Bệnh viện hoặc hiệu thuốc gần nhất ở đâu?',
  '⚠️ Làm ơn giúp tôi, trường hợp khẩn cấp!',
];

const POPULAR_CURRENCIES = [
  { code: 'VND', flag: '🇻🇳', name: 'Việt Nam Đồng' },
  { code: 'USD', flag: '🇺🇸', name: 'US Dollar' },
  { code: 'EUR', flag: '🇪🇺', name: 'Euro' },
  { code: 'JPY', flag: '🇯🇵', name: 'Japanese Yen' },
  { code: 'KRW', flag: '🇰🇷', name: 'Korean Won' },
  { code: 'THB', flag: '🇹🇭', name: 'Thai Baht' },
  { code: 'SGD', flag: '🇸🇬', name: 'Singapore Dollar' },
  { code: 'GBP', flag: '🇬🇧', name: 'British Pound' },
  { code: 'AUD', flag: '🇦🇺', name: 'Australian Dollar' },
  { code: 'CNY', flag: '🇨🇳', name: 'Chinese Yuan' },
  { code: 'HKD', flag: '🇭🇰', name: 'Hong Kong Dollar' },
  { code: 'TWD', flag: '🇹🇼', name: 'Taiwan Dollar' },
  { code: 'MYR', flag: '🇲🇾', name: 'Malaysian Ringgit' },
  { code: 'IDR', flag: '🇮🇩', name: 'Indonesian Rupiah' },
  { code: 'PHP', flag: '🇵🇭', name: 'Philippine Peso' },
  { code: 'CAD', flag: '🇨🇦', name: 'Canadian Dollar' },
  { code: 'CHF', flag: '🇨🇭', name: 'Swiss Franc' },
];

function getCurrencyInfo(code: string) {
  return POPULAR_CURRENCIES.find(c => c.code === code) || { code, flag: '🌐', name: code };
}

export default function UtilitiesScreen() {
  const [hubTab, setHubTab] = useState<'translate' | 'currency'>('translate');

  // --- Translation State ---
  const [sourceText, setSourceText] = useState('');
  const [targetLang, setTargetLang] = useState('en');
  const [translationResult, setTranslationResult] = useState<TranslationResponse | null>(null);
  const [translateLoading, setTranslateLoading] = useState(false);
  const [showLangPicker, setShowLangPicker] = useState(false);

  // --- Currency State ---
  const [amount, setAmount] = useState('1');
  const [fromCurrency, setFromCurrency] = useState('USD');
  const [toCurrency, setToCurrency] = useState('VND');
  const [currencyResult, setCurrencyResult] = useState<CurrencyConvertResponse | null>(null);
  const [currencyLoading, setCurrencyLoading] = useState(false);
  const [allRates, setAllRates] = useState<Record<string, number>>({});
  const [showRates, setShowRates] = useState(false);
  const [ratesLoading, setRatesLoading] = useState(false);
  const [selectingCurrency, setSelectingCurrency] = useState<'from' | 'to' | null>(null);

  useEffect(() => {
    handleConvert();
  }, []);

  // --- Translation Handlers ---
  const handleTranslate = async (overrideText?: string) => {
    const textToTranslate = (overrideText ?? sourceText).trim();
    if (!textToTranslate) {
      Alert.alert('Thông báo', 'Vui lòng nhập nội dung cần dịch.');
      return;
    }
    setSourceText(textToTranslate);
    setTranslateLoading(true);
    try {
      const res = await translateTextMobile(textToTranslate, targetLang, 'vi');
      setTranslationResult(res);
    } catch (err: any) {
      Alert.alert('Lỗi', err.message || 'Không thể dịch lúc này. Vui lòng thử lại.');
    } finally {
      setTranslateLoading(false);
    }
  };

  const copyTranslation = async () => {
    if (translationResult?.translated_text) {
      await Clipboard.setStringAsync(translationResult.translated_text);
      Alert.alert('Đã sao chép!', 'Bản dịch đã được sao chép vào bộ nhớ tạm.');
    }
  };

  // --- Currency Handlers ---
  const handleConvert = async () => {
    const num = parseFloat(amount);
    if (!amount || isNaN(num) || num <= 0) return;
    setCurrencyLoading(true);
    try {
      const res = await convertCurrencyMobile(num, fromCurrency, toCurrency);
      setCurrencyResult(res);
    } catch (err: any) {
      // Ignore initial auto-convert error if server still booting
    } finally {
      setCurrencyLoading(false);
    }
  };

  const swapCurrencies = () => {
    setFromCurrency(toCurrency);
    setToCurrency(fromCurrency);
    setCurrencyResult(null);
  };

  const copyCurrencyResult = async () => {
    if (currencyResult?.converted_amount) {
      await Clipboard.setStringAsync(String(currencyResult.converted_amount));
      Alert.alert('Đã sao chép!', 'Số tiền đã được sao chép.');
    }
  };

  const loadAllRates = async () => {
    setShowRates(true);
    setRatesLoading(true);
    try {
      const data = await getAllRatesMobile('USD');
      setAllRates(data.rates || data || {});
    } catch {
      Alert.alert('Lỗi', 'Không thể tải bảng tỷ giá.');
      setShowRates(false);
    } finally {
      setRatesLoading(false);
    }
  };

  const currentLangObj = TRANSLATE_LANGUAGES.find(l => l.code === targetLang) || TRANSLATE_LANGUAGES[0];
  const fromInfo = getCurrencyInfo(fromCurrency);
  const toInfo = getCurrencyInfo(toCurrency);

  // Currency Selector Modal View
  if (selectingCurrency) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <LinearGradient colors={[BG_DARK, '#0C1825']} style={styles.gradient}>
          <View style={styles.pickerHeader}>
            <TouchableOpacity onPress={() => setSelectingCurrency(null)}>
              <Ionicons name="arrow-back" size={24} color={TEXT_PRIMARY} />
            </TouchableOpacity>
            <Text style={styles.pickerTitle}>
              {selectingCurrency === 'from' ? 'Chọn Tiền Gốc' : 'Chọn Tiền Đích'}
            </Text>
            <View style={{ width: 24 }} />
          </View>
          <FlatList
            data={POPULAR_CURRENCIES}
            keyExtractor={item => item.code}
            contentContainerStyle={{ padding: 16 }}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={[
                  styles.currencyListItem,
                  (selectingCurrency === 'from' ? fromCurrency : toCurrency) === item.code &&
                    styles.currencyListItemActive,
                ]}
                onPress={() => {
                  if (selectingCurrency === 'from') setFromCurrency(item.code);
                  else setToCurrency(item.code);
                  setSelectingCurrency(null);
                  setCurrencyResult(null);
                }}
              >
                <Text style={styles.currencyFlag}>{item.flag}</Text>
                <View style={{ flex: 1 }}>
                  <Text style={styles.currencyCode}>{item.code}</Text>
                  <Text style={styles.currencyName}>{item.name}</Text>
                </View>
                {(selectingCurrency === 'from' ? fromCurrency : toCurrency) === item.code && (
                  <Ionicons name="checkmark-circle" size={22} color={PRIMARY} />
                )}
              </TouchableOpacity>
            )}
          />
        </LinearGradient>
      </SafeAreaView>
    );
  }

  // Language Picker Modal View
  if (showLangPicker) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <LinearGradient colors={[BG_DARK, '#0C1825']} style={styles.gradient}>
          <View style={styles.pickerHeader}>
            <TouchableOpacity onPress={() => setShowLangPicker(false)}>
              <Ionicons name="arrow-back" size={24} color={TEXT_PRIMARY} />
            </TouchableOpacity>
            <Text style={styles.pickerTitle}>Chọn Ngôn Ngữ Đích</Text>
            <View style={{ width: 24 }} />
          </View>
          <FlatList
            data={TRANSLATE_LANGUAGES}
            keyExtractor={item => item.code}
            contentContainerStyle={{ padding: 16 }}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={[
                  styles.currencyListItem,
                  targetLang === item.code && styles.currencyListItemActive,
                ]}
                onPress={() => {
                  setTargetLang(item.code);
                  setShowLangPicker(false);
                  if (sourceText.trim()) {
                    handleTranslate();
                  }
                }}
              >
                <Text style={styles.currencyFlag}>{item.flag}</Text>
                <Text style={[styles.currencyName, { fontSize: 15, fontWeight: '700' }]}>{item.name}</Text>
                {targetLang === item.code && (
                  <Ionicons name="checkmark-circle" size={22} color={PRIMARY} />
                )}
              </TouchableOpacity>
            )}
          />
        </LinearGradient>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <LinearGradient colors={[BG_DARK, '#0C1825']} style={styles.gradient}>
        <NavbarHeader
          title="🌐 Tiện Ích & Phiên Dịch"
          subtitle="Dịch thuật đa ngôn ngữ & Đổi tiền tệ trực tiếp"
        />

        {/* Top Hub Tabs: Translation vs Currency */}
        <View style={styles.hubTabBar}>
          <TouchableOpacity
            style={[styles.hubTabItem, hubTab === 'translate' && styles.hubTabItemActive]}
            onPress={() => setHubTab('translate')}
          >
            <Ionicons
              name="language-outline"
              size={17}
              color={hubTab === 'translate' ? '#fff' : TEXT_SECONDARY}
            />
            <Text style={[styles.hubTabText, hubTab === 'translate' && styles.hubTabTextActive]}>
              Dịch Thuật
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.hubTabItem, hubTab === 'currency' && styles.hubTabItemActive]}
            onPress={() => setHubTab('currency')}
          >
            <Ionicons
              name="swap-horizontal-outline"
              size={17}
              color={hubTab === 'currency' ? '#fff' : TEXT_SECONDARY}
            />
            <Text style={[styles.hubTabText, hubTab === 'currency' && styles.hubTabTextActive]}>
              Đổi Tiền Tệ
            </Text>
          </TouchableOpacity>
        </View>

        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}
          style={{ flex: 1 }}
        >
          <ScrollView
            style={styles.scroll}
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}
            keyboardShouldPersistTaps="handled"
          >
            {/* ================= SECTION 1: TRANSLATION ================= */}
            {hubTab === 'translate' && (
              <View>
                {/* Translation Box */}
                <View style={styles.card}>
                  <Text style={styles.sectionHeader}>Dịch Sang Ngôn Ngữ:</Text>
                  <TouchableOpacity
                    style={styles.langSelectorBtn}
                    onPress={() => setShowLangPicker(true)}
                  >
                    <Text style={styles.langSelectorFlag}>{currentLangObj.flag}</Text>
                    <Text style={styles.langSelectorText}>{currentLangObj.name}</Text>
                    <Ionicons name="chevron-down" size={18} color={TEXT_SECONDARY} />
                  </TouchableOpacity>

                  <Text style={[styles.sectionHeader, { marginTop: 14 }]}>Nội dung cần dịch:</Text>
                  <View style={styles.textAreaWrapper}>
                    <TextInput
                      style={styles.textArea}
                      value={sourceText}
                      onChangeText={setSourceText}
                      placeholder="Nhập câu tiếng Việt... Ví dụ: Cho tôi xem thực đơn, làm ơn."
                      placeholderTextColor="#64748B"
                      multiline
                      numberOfLines={3}
                      textAlignVertical="top"
                    />
                    {sourceText ? (
                      <TouchableOpacity
                        style={styles.clearBtn}
                        onPress={() => setSourceText('')}
                      >
                        <Ionicons name="close-circle" size={18} color="#64748B" />
                      </TouchableOpacity>
                    ) : null}
                  </View>

                  <TouchableOpacity
                    style={[styles.actionBtn, (!sourceText.trim() || translateLoading) && { opacity: 0.6 }]}
                    onPress={() => handleTranslate()}
                    disabled={!sourceText.trim() || translateLoading}
                  >
                    <LinearGradient
                      colors={[PRIMARY, '#0369A1']}
                      style={styles.actionGradient}
                      start={{ x: 0, y: 0 }}
                      end={{ x: 1, y: 0 }}
                    >
                      {translateLoading ? (
                        <ActivityIndicator color="#fff" size="small" />
                      ) : (
                        <Ionicons name="language" size={18} color="#fff" />
                      )}
                      <Text style={styles.actionBtnText}>
                        {translateLoading ? 'Đang dịch...' : 'Dịch Ngay'}
                      </Text>
                    </LinearGradient>
                  </TouchableOpacity>

                  {/* Translation Result Card */}
                  {translationResult && (
                    <View style={styles.resultBox}>
                      <View style={styles.resultHeaderRow}>
                        <View style={styles.resultBadge}>
                          <Text style={styles.resultBadgeText}>BẢN DỊCH BẢN ĐỊA</Text>
                        </View>
                        <TouchableOpacity
                          style={styles.copyBtn}
                          onPress={copyTranslation}
                        >
                          <Ionicons name="copy-outline" size={16} color={PRIMARY} />
                          <Text style={styles.copyBtnText}>Sao Chép</Text>
                        </TouchableOpacity>
                      </View>
                      <Text style={styles.translatedText}>
                        {translationResult.translated_text}
                      </Text>
                      {translationResult.provider ? (
                        <Text style={styles.providerText}>
                          Nguồn: {translationResult.provider}
                        </Text>
                      ) : null}
                    </View>
                  )}
                </View>

                {/* Quick Phrases */}
                <View style={[styles.card, { marginTop: 14 }]}>
                  <Text style={styles.sectionHeader}>💬 Mẫu Câu Du Lịch Thông Dụng</Text>
                  <Text style={styles.subHint}>Bấm vào mẫu câu để dịch tức thì sang tiếng bản địa:</Text>
                  <View style={styles.quickPhrasesWrap}>
                    {QUICK_PHRASES.map((phrase, i) => (
                      <TouchableOpacity
                        key={i}
                        style={styles.phraseChip}
                        onPress={() => handleTranslate(phrase.replace(/^.*?\s/, ''))}
                        activeOpacity={0.7}
                      >
                        <Text style={styles.phraseText}>{phrase}</Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>
              </View>
            )}

            {/* ================= SECTION 2: CURRENCY CONVERTER ================= */}
            {hubTab === 'currency' && (
              <View>
                <View style={styles.card}>
                  <View style={styles.currencyCardTop}>
                    <Text style={styles.sectionHeader}>Số tiền cần đổi</Text>
                    <TouchableOpacity
                      style={styles.allRatesBtn}
                      onPress={loadAllRates}
                    >
                      <Ionicons name="globe-outline" size={14} color={PRIMARY} />
                      <Text style={styles.allRatesText}>Bảng tỷ giá</Text>
                    </TouchableOpacity>
                  </View>

                  <TextInput
                    style={styles.amountInput}
                    value={amount}
                    onChangeText={t => { setAmount(t); setCurrencyResult(null); }}
                    keyboardType="numeric"
                    placeholder="1"
                    placeholderTextColor="#64748B"
                  />

                  {/* Currency Selectors */}
                  <View style={styles.currencyRow}>
                    <TouchableOpacity
                      style={styles.currencySelectBtn}
                      onPress={() => setSelectingCurrency('from')}
                    >
                      <Text style={styles.flagLarge}>{fromInfo.flag}</Text>
                      <View>
                        <Text style={styles.curCode}>{fromCurrency}</Text>
                        <Text style={styles.curName} numberOfLines={1}>{fromInfo.name}</Text>
                      </View>
                      <Ionicons name="chevron-down" size={16} color={TEXT_SECONDARY} />
                    </TouchableOpacity>

                    <TouchableOpacity style={styles.swapBtn} onPress={swapCurrencies}>
                      <LinearGradient colors={[PRIMARY, '#0369A1']} style={styles.swapGradient}>
                        <Ionicons name="swap-horizontal" size={20} color="#fff" />
                      </LinearGradient>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={styles.currencySelectBtn}
                      onPress={() => setSelectingCurrency('to')}
                    >
                      <Text style={styles.flagLarge}>{toInfo.flag}</Text>
                      <View>
                        <Text style={styles.curCode}>{toCurrency}</Text>
                        <Text style={styles.curName} numberOfLines={1}>{toInfo.name}</Text>
                      </View>
                      <Ionicons name="chevron-down" size={16} color={TEXT_SECONDARY} />
                    </TouchableOpacity>
                  </View>

                  <TouchableOpacity
                    style={styles.actionBtn}
                    onPress={handleConvert}
                    disabled={currencyLoading}
                  >
                    <LinearGradient
                      colors={[PRIMARY, '#0369A1']}
                      style={styles.actionGradient}
                      start={{ x: 0, y: 0 }}
                      end={{ x: 1, y: 0 }}
                    >
                      {currencyLoading ? (
                        <ActivityIndicator color="#fff" size="small" />
                      ) : (
                        <Ionicons name="calculator" size={18} color="#fff" />
                      )}
                      <Text style={styles.actionBtnText}>
                        {currencyLoading ? 'Đang tính toán...' : 'Quy Đổi Tỷ Giá'}
                      </Text>
                    </LinearGradient>
                  </TouchableOpacity>

                  {/* Result Box */}
                  {currencyResult && (
                    <View style={styles.resultBox}>
                      <View style={styles.currencyResultRow}>
                        <Text style={styles.curFromText}>
                          {fromInfo.flag} {parseFloat(amount).toLocaleString()} {fromCurrency} =
                        </Text>
                        <TouchableOpacity onPress={copyCurrencyResult}>
                          <Ionicons name="copy-outline" size={16} color={TEXT_SECONDARY} />
                        </TouchableOpacity>
                      </View>
                      <Text style={styles.curToText}>
                        {toInfo.flag} {Number(currencyResult.converted_amount).toLocaleString(undefined, { maximumFractionDigits: 2 })} {toCurrency}
                      </Text>
                      <View style={styles.rateDetailRow}>
                        <Text style={styles.rateDetailText}>
                          📊 1 {fromCurrency} = {Number(currencyResult.exchange_rate || currencyResult.rate || 0).toLocaleString(undefined, { maximumFractionDigits: 4 })} {toCurrency}
                        </Text>
                      </View>
                    </View>
                  )}
                </View>

                {/* Quick Convert Buttons to VND */}
                <View style={[styles.card, { marginTop: 14 }]}>
                  <Text style={styles.sectionHeader}>⚡ Quy Đổi Nhanh 1 Đơn Vị Sang VND</Text>
                  <View style={styles.quickCurWrap}>
                    {['USD', 'EUR', 'JPY', 'KRW', 'THB', 'SGD'].map(code => {
                      const c = getCurrencyInfo(code);
                      return (
                        <TouchableOpacity
                          key={code}
                          style={styles.quickCurBtn}
                          onPress={() => {
                            setFromCurrency(code);
                            setToCurrency('VND');
                            setAmount('1');
                            handleConvert();
                          }}
                        >
                          <Text style={styles.quickCurFlag}>{c.flag}</Text>
                          <Text style={styles.quickCurCode}>{code}</Text>
                        </TouchableOpacity>
                      );
                    })}
                  </View>
                </View>

                {/* All rates table */}
                {showRates && (
                  <View style={[styles.card, { marginTop: 14 }]}>
                    <View style={styles.currencyCardTop}>
                      <Text style={styles.sectionHeader}>🌍 Bảng Tỷ Giá (1 USD)</Text>
                      <TouchableOpacity onPress={() => setShowRates(false)}>
                        <Ionicons name="close" size={18} color={TEXT_SECONDARY} />
                      </TouchableOpacity>
                    </View>
                    {ratesLoading ? (
                      <ActivityIndicator color={PRIMARY} style={{ marginVertical: 20 }} />
                    ) : (
                      Object.entries(allRates)
                        .filter(([code]) => POPULAR_CURRENCIES.some(c => c.code === code))
                        .map(([code, r]) => {
                          const info = getCurrencyInfo(code);
                          return (
                            <View key={code} style={styles.rateItemRow}>
                              <Text style={{ fontSize: 18 }}>{info.flag}</Text>
                              <Text style={styles.rateItemCode}>{code}</Text>
                              <Text style={styles.rateItemName}>{info.name}</Text>
                              <Text style={styles.rateItemValue}>
                                {Number(r).toLocaleString(undefined, { maximumFractionDigits: 3 })}
                              </Text>
                            </View>
                          );
                        })
                    )}
                  </View>
                )}
              </View>
            )}
          </ScrollView>
        </KeyboardAvoidingView>
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: BG_DARK },
  gradient: { flex: 1 },
  hubTabBar: {
    flexDirection: 'row',
    backgroundColor: CARD_BG,
    marginHorizontal: 16,
    marginTop: 10,
    borderRadius: 12,
    padding: 4,
    borderWidth: 1,
    borderColor: BORDER,
  },
  hubTabItem: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    gap: 6,
    borderRadius: 8,
  },
  hubTabItemActive: { backgroundColor: PRIMARY },
  hubTabText: { color: TEXT_SECONDARY, fontWeight: '700', fontSize: 13 },
  hubTabTextActive: { color: '#fff' },
  scroll: { flex: 1 },
  scrollContent: { padding: 16, paddingBottom: 40 },
  card: {
    backgroundColor: CARD_BG,
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: BORDER,
  },
  sectionHeader: { color: TEXT_PRIMARY, fontWeight: '800', fontSize: 14, marginBottom: 8 },
  subHint: { color: TEXT_SECONDARY, fontSize: 12, marginBottom: 12 },
  langSelectorBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: BG_DARK,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 12,
    gap: 10,
    borderWidth: 1,
    borderColor: BORDER,
  },
  langSelectorFlag: { fontSize: 22 },
  langSelectorText: { color: TEXT_PRIMARY, fontWeight: '700', fontSize: 14, flex: 1 },
  textAreaWrapper: { position: 'relative' },
  textArea: {
    backgroundColor: BG_DARK,
    borderRadius: 12,
    padding: 14,
    paddingRight: 36,
    color: TEXT_PRIMARY,
    fontSize: 14,
    minHeight: 85,
    borderWidth: 1,
    borderColor: BORDER,
  },
  clearBtn: { position: 'absolute', top: 12, right: 12 },
  actionBtn: { borderRadius: 12, overflow: 'hidden', marginTop: 14 },
  actionGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 13,
    gap: 8,
  },
  actionBtnText: { color: '#fff', fontWeight: '800', fontSize: 15 },
  resultBox: {
    backgroundColor: '#0F2744',
    borderRadius: 14,
    padding: 14,
    marginTop: 14,
    borderWidth: 1,
    borderColor: '#1D4ED8',
  },
  resultHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  resultBadge: {
    backgroundColor: 'rgba(56, 189, 248, 0.2)',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  resultBadgeText: { color: '#38BDF8', fontSize: 10, fontWeight: '800' },
  copyBtn: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  copyBtnText: { color: PRIMARY, fontSize: 12, fontWeight: '700' },
  translatedText: { color: '#fff', fontSize: 16, fontWeight: '800', lineHeight: 24 },
  providerText: { color: '#64748B', fontSize: 11, marginTop: 8 },
  quickPhrasesWrap: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  phraseChip: {
    backgroundColor: BG_DARK,
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderWidth: 1,
    borderColor: BORDER,
  },
  phraseText: { color: TEXT_SECONDARY, fontSize: 12, fontWeight: '600' },
  currencyCardTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  allRatesBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: BG_DARK,
    borderRadius: 14,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderWidth: 1,
    borderColor: BORDER,
  },
  allRatesText: { color: PRIMARY, fontSize: 12, fontWeight: '700' },
  amountInput: {
    backgroundColor: BG_DARK,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 12,
    color: TEXT_PRIMARY,
    fontSize: 22,
    fontWeight: '800',
    borderWidth: 1,
    borderColor: BORDER,
    textAlign: 'center',
    marginBottom: 14,
  },
  currencyRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  currencySelectBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: BG_DARK,
    borderRadius: 12,
    padding: 10,
    gap: 6,
    borderWidth: 1,
    borderColor: BORDER,
  },
  flagLarge: { fontSize: 22 },
  curCode: { color: TEXT_PRIMARY, fontWeight: '800', fontSize: 15 },
  curName: { color: TEXT_SECONDARY, fontSize: 10, width: 60 },
  swapBtn: { borderRadius: 20 },
  swapGradient: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  currencyResultRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  curFromText: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: '600' },
  curToText: { color: SUCCESS, fontSize: 22, fontWeight: '800', marginVertical: 4 },
  rateDetailRow: { marginTop: 4 },
  rateDetailText: { color: '#BAE6FD', fontSize: 12 },
  quickCurWrap: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  quickCurBtn: {
    flex: 1,
    minWidth: '28%',
    backgroundColor: BG_DARK,
    borderRadius: 12,
    padding: 10,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: BORDER,
  },
  quickCurFlag: { fontSize: 22, marginBottom: 4 },
  quickCurCode: { color: TEXT_PRIMARY, fontWeight: '700', fontSize: 12 },
  rateItemRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
    gap: 10,
  },
  rateItemCode: { color: TEXT_PRIMARY, fontWeight: '700', fontSize: 13, width: 40 },
  rateItemName: { color: TEXT_SECONDARY, fontSize: 11, flex: 1 },
  rateItemValue: { color: SUCCESS, fontWeight: '700', fontSize: 13 },
  pickerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: BORDER,
  },
  pickerTitle: { color: TEXT_PRIMARY, fontSize: 17, fontWeight: '800' },
  currencyListItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: CARD_BG,
    borderRadius: 14,
    padding: 14,
    marginBottom: 8,
    gap: 14,
    borderWidth: 1,
    borderColor: BORDER,
  },
  currencyListItemActive: { borderColor: PRIMARY, backgroundColor: '#1E3A5F' },
  currencyFlag: { fontSize: 26 },
  currencyCode: { color: TEXT_PRIMARY, fontWeight: '800', fontSize: 15 },
  currencyName: { color: TEXT_SECONDARY, fontSize: 12 },
});
