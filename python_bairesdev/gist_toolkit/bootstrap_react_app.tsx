// Gist: bootstrap_react_app.tsx
// A production-ready, clean frontend entry point combining core state and layout providers.

import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { SWRConfig } from 'swr';
import { ChakraProvider, extendTheme } from '@chakra-ui/react';
import { store } from './store'; // Assume Redux Toolkit configureStore path
import { apiFetcher } from './apiClient'; // Assume Axios global fetcher path

// 1. Extend theme colors and configs for Chakra UI
const customTheme = extendTheme({
  config: {
    initialColorMode: 'dark',
    useSystemColorMode: false,
  },
  colors: {
    brand: {
      900: '#090d16',
      800: '#111827',
      700: '#1f2937',
    },
  },
});

// 2. Global SWR Cache Configuration
const globalSWRConfig = {
  fetcher: apiFetcher,
  revalidateOnFocus: false, // Disables aggressive re-fetching when toggling browser tabs
  revalidateOnReconnect: true,
  shouldRetryOnError: true,
  errorRetryCount: 3,
  dedupingInterval: 5000, // Dedupes duplicate component API requests within 5 seconds
};

// 3. Root Application Layout Component
const AppLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-950 text-white font-sans antialiased p-6">
      <header className="mb-8 border-b border-gray-800 pb-4 flex justify-between items-center">
        <h1 className="text-xl font-bold tracking-tight">Fullstack Core Board</h1>
        <span className="text-xs bg-green-500/10 text-green-400 border border-green-500/20 px-2 py-1 rounded">
          Sync Connected
        </span>
      </header>
      <main className="max-w-7xl mx-auto">
        <p className="text-gray-400 text-sm">
          React application successfully bootstrapped with Redux, SWR caching, and Chakra UI themes.
        </p>
      </main>
    </div>
  );
};

// 4. Mount Application wrapping all provider states
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <SWRConfig value={globalSWRConfig}>
        <ChakraProvider theme={customTheme}>
          <AppLayout />
        </ChakraProvider>
      </SWRConfig>
    </Provider>
  </React.StrictMode>
);
