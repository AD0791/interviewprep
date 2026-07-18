// Use Case: Custom SWR Data Fetching Hook with Optimistic Updates
// Purpose: Fetches timeseries metrics, applies memoized transformations, and provides instant UI feedback.
// Key features: SWR caching configs, React useMemo mapping, and cache mutation rollbacks.

import useSWR, { useSWRConfig } from 'swr';
import { useMemo } from 'react';
import { httpClient, apiFetcher } from './react_swr_axios_client';

interface RawMetric {
  tenant_id: number;
  tenant_name: string;
  sales_date: string;
  daily_sales: number;
  running_cumulative_sales: number;
}

export const useMetricsData = (startDate?: string) => {
  const { mutate } = useSWRConfig();
  const url = `/analytics/cumulative-sales${startDate ? `?start_date=${startDate}` : ''}`;
  
  const { data, error, isLoading, mutate: localMutate } = useSWR<RawMetric[]>(
    url, 
    apiFetcher, 
    {
      revalidateOnFocus: false, // Prevents aggressive refresh on browser tab refocuses
      dedupingInterval: 5000,    // Cache stays fresh for 5 seconds
    }
  );

  // 1. Memoize dataset transformations
  // Why: Prevents recalculating arrays on unrelated parent re-renders (e.g. sidebar collapse)
  const chartData = useMemo(() => {
    if (!data) return [];
    
    return data.map((item) => ({
      date: new Date(item.sales_date).toLocaleDateString(),
      sales: item.daily_sales,
      cumulative: item.running_cumulative_sales,
      name: item.tenant_name,
    }));
  }, [data]);

  // 2. Optimistic UI updates
  // Why: Instantly changes UI state, updating backend in background, rolling back on failure
  const updateMetricOptimistically = async (tenantId: number, tempSalesUpdate: number) => {
    if (!data) return;

    // A. Map local data copy
    const optimisticData = data.map((item) => 
      item.tenant_id === tenantId 
        ? { ...item, daily_sales: tempSalesUpdate } 
        : item
    );

    // B. Inject optimistic values into cache, disabling immediate background validation
    localMutate(optimisticData, false);

    try {
      // C. Run actual API write call
      await httpClient.post('/analytics/adjust-metric', { tenant_id: tenantId, amount: tempSalesUpdate });
      // D. Force refetch to sync target source of truth
      mutate(url);
    } catch (err) {
      // E. Rollback state to original data on failure
      localMutate(data, true);
      throw err;
    }
  };

  return {
    metrics: data,
    chartData,
    isLoading,
    isError: !!error,
    updateMetricOptimistically,
  };
};
