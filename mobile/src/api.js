import axios from 'axios';

// Replace with your local machine's IP address when running on physical device
const API_BASE_URL = 'http://10.0.2.2:8000/api/v1'; 

export const mobileApi = axios.create({
  baseURL: API_BASE_URL,
});

export const getTripsMobile = async () => {
  const res = await mobileApi.get('/trips/');
  return res.data;
};

export const askInTripSupportMobile = async (tripId, userQuery) => {
  const res = await mobileApi.post('/agent/in-trip-support', {
    trip_id: tripId,
    user_query: userQuery,
  });
  return res.data;
};
