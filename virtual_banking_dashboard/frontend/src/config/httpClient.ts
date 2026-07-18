import axios from 'axios';
import { env } from './env';

export const httpClient = axios.create({
  baseURL: env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export const apiFetcher = (url: string) => httpClient.get(url).then((res) => res.data);
