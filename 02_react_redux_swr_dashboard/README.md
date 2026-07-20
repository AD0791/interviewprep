# Frontend: React, Redux Toolkit, SWR/Axios, and Dashboard UI

This directory is dedicated to frontend preparation, focused on building highly responsive dashboards, state management, and data-fetching.

## Documents in This Folder

1. [01_react_dashboard_rendering_state.md](01_react_dashboard_rendering_state.md) — Server-cache vs client-state boundary, memoization rules, list virtualization.
2. [02_browser_apis_and_storage.md](02_browser_apis_and_storage.md) — Client storage comparison, HttpOnly cookies vs localStorage, token security.
3. [03_error_boundaries_suspense_profiling.md](03_error_boundaries_suspense_profiling.md) — Per-widget error boundaries with SWR reset, Suspense for data, React Profiler workflow.

## Key Study Topics

### 1. Data Fetching & Caching
* **SWR (Stale-While-Revalidate) / React Query**:
  * Automatic caching, revalidation on focus, polling, and pagination support.
  * Optimistic updates (immediately update local state before API resolves, revert on error).
* **Axios**:
  * Configured client instances, request/response interceptors (handling auth tokens, global error tracking).

### 2. State Management (Redux Toolkit)
* **When to use RTK vs SWR**:
  * SWR/React Query for server-cache state.
  * Redux Toolkit for complex global client state (UI state, user preferences, multi-step wizards, cross-component sync).
* **RTK Slices**:
  ```typescript
  import { createSlice, PayloadAction } from '@reduxjs/toolkit';
  ```

### 3. Dashboard Performance Optimization
* **Rendering Optimizations**:
  * `React.memo` for static widgets.
  * `useMemo` for heavy data transformation or filtering before passing to charts.
  * `useCallback` for event handlers passed to child components.
* **Large Datasets**:
  * Virtualized lists (e.g., `react-window` or `react-virtualized`) for long aggregation logs.
  * Debouncing inputs for filter fields.

### 4. Form Validation: Formik & Zod
* Formik handles form submission, values, errors, and touch states.
* Zod defines the schema and acts as the validator using `zod-formik-adapter` or direct validation.
