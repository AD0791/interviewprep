// Use Case: Global UI State & Preference Management (Redux Toolkit)
// Purpose: Configures slices, immer-driven mutators, and memoized selectors.
// Key features: RTK slices, Immer integration, custom selectors.

import { configureStore, createSlice, createSelector, PayloadAction } from '@reduxjs/toolkit';

interface DashboardState {
  theme: 'light' | 'dark';
  timeRange: '7d' | '30d' | '90d';
  visibleWidgets: string[];
  sidebarCollapsed: boolean;
}

const initialState: DashboardState = {
  theme: 'dark',
  timeRange: '30d',
  visibleWidgets: ['sales-chart', 'logs-table'],
  sidebarCollapsed: false,
};

// 1. Create Slice
// Why Immer: Reducer functions use Immer.js. We can write mutating statements (e.g. array.push) safely
const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    toggleTheme: (state) => {
      state.theme = state.theme === 'light' ? 'dark' : 'light';
    },
    setTimeRange: (state, action: PayloadAction<DashboardState['timeRange']>) => {
      state.timeRange = action.payload;
    },
    toggleWidgetVisibility: (state, action: PayloadAction<string>) => {
      const widget = action.payload;
      if (state.visibleWidgets.includes(widget)) {
        state.visibleWidgets = state.visibleWidgets.filter((w) => w !== widget);
      } else {
        state.visibleWidgets.push(widget);
      }
    },
    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.sidebarCollapsed = action.payload;
    },
  },
});

// Export slice actions
export const {
  toggleTheme,
  setTimeRange,
  toggleWidgetVisibility,
  setSidebarCollapsed,
} = dashboardSlice.actions;

// 2. Configure Global Store
export const store = configureStore({
  reducer: {
    dashboard: dashboardSlice.reducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// ---------------------------------------------------------
// 3. MEMOIZED SELECTORS
// ---------------------------------------------------------
const selectDashboardState = (state: RootState) => state.dashboard;

// Select visible widgets array
export const selectVisibleWidgets = createSelector(
  [selectDashboardState],
  (dashboard) => dashboard.visibleWidgets
);

// Select theme properties (Memoized)
// Why: Selector prevents rendering triggers in components if other state attributes (like sidebar) toggle
export const selectActiveTheme = createSelector(
  [selectDashboardState],
  (dashboard) => dashboard.theme
);
