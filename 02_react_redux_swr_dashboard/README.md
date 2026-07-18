# Frontend: React, Redux Toolkit, SWR/Axios, and Dashboard UI

This directory is dedicated to frontend preparation, focused on building highly responsive dashboards, state management, and data-fetching.

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
