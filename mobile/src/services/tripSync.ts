import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Linking from 'expo-linking';
import {
  TripData,
  STORAGE_KEYS,
  getTripsMobile,
  getTripDetailMobile,
  deleteTripMobile,
  replanTripMobile,
  getTripPdfUrl,
} from '../api/index';

export const tripSync = {
  /** Fetch latest trips from backend and update local cache */
  async syncTrips(): Promise<TripData[]> {
    const trips = await getTripsMobile();
    await AsyncStorage.setItem(STORAGE_KEYS.CACHED_TRIPS, JSON.stringify(trips));
    return trips;
  },

  /** Get cached trips from local storage without waiting for network */
  async getLocalTrips(): Promise<TripData[]> {
    const cached = await AsyncStorage.getItem(STORAGE_KEYS.CACHED_TRIPS);
    return cached ? JSON.parse(cached) : [];
  },

  /** Get trip details and cache locally */
  async syncTripDetail(tripId: number | string): Promise<TripData> {
    const detail = await getTripDetailMobile(tripId);
    await AsyncStorage.setItem(`@cached_trip_detail_${tripId}`, JSON.stringify(detail));
    return detail;
  },

  /** Replan a trip item and synchronize with backend */
  async replanItem(
    tripId: number,
    modificationPrompt: string,
    modifiedItem?: any
  ) {
    const result = await replanTripMobile(tripId, modificationPrompt, modifiedItem);
    // Refresh trips list after replan
    await this.syncTrips().catch(() => {});
    return result;
  },

  /** Delete trip on backend and remove from local cache */
  async deleteTrip(tripId: number | string): Promise<void> {
    await deleteTripMobile(tripId);
    const local = await this.getLocalTrips();
    const updated = local.filter(t => String(t.id) !== String(tripId));
    await AsyncStorage.setItem(STORAGE_KEYS.CACHED_TRIPS, JSON.stringify(updated));
    await AsyncStorage.removeItem(`@cached_trip_detail_${tripId}`);
  },

  /** Open / Download PDF directly */
  async downloadPdf(tripId: number | string): Promise<boolean> {
    try {
      const pdfUrl = getTripPdfUrl(tripId);
      const supported = await Linking.canOpenURL(pdfUrl);
      if (supported) {
        await Linking.openURL(pdfUrl);
        return true;
      }
      return false;
    } catch {
      return false;
    }
  },
};
