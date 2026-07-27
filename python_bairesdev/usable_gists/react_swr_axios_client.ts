// Use Case: Centralized HTTP Client & Cache Fetcher (Axios + SWR)
// Purpose: Implements request/response interception, token injecting, and unified fetching profiles.
// Key features: Axios Interceptors, token retrieval, global error handlers, and SWR fetcher integrations.

import axios, { AxiosError } from 'axios';

// 1. Configure central Axios client
export const httpClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 8000,
});

// 2. Request Interceptor: Inject JWT token on outgoing HTTP calls
httpClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 3. Response Interceptor: Catch 401 unauthorized errors globally to force re-logins
httpClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 4. Generic SWR Fetcher Wrapper
// Why: Maps response body data directly to cache stores, simplifying SWR hooks
export const apiFetcher = (url: string) => 
  httpClient.get(url).then((res) => res.data);
