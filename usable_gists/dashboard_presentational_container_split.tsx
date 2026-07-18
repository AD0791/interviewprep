// Use Case: Isolate UI Rendering from Stateful Logic (Smart/Dumb Split)
// Purpose: Split data loading (Container) and card rendering (Presentational Component).
// Key features: React.memo wrapper, custom hook integration, prop-driven interfaces.

import React, { useMemo } from 'react';
import useSWR from 'swr';
import { apiFetcher } from './react_swr_axios_client';

// ---------------------------------------------------------
// 1. PRESENTATIONAL COMPONENT (Dumb - Layout/Styling Only)
// ---------------------------------------------------------
interface StatsDisplayProps {
  title: string;
  value: number;
  isLoading: boolean;
}

// React.memo: Prevents card rendering unless props change (e.g. value changes)
const StatsDisplay: React.FC<StatsDisplayProps> = React.memo(({ title, value, isLoading }) => {
  console.log(`Rendering StatsDisplay Card: ${title}`);
  
  if (isLoading) {
    return <div className="animate-pulse bg-gray-800 h-24 rounded-lg" />;
  }
  
  return (
    <div className="p-6 bg-gray-900 border border-gray-800 rounded-xl text-white">
      <h4 className="text-xs font-bold uppercase text-gray-400">{title}</h4>
      <p className="text-3xl font-black mt-2">${value.toLocaleString()}</p>
    </div>
  );
});
StatsDisplay.displayName = 'StatsDisplay';

// ---------------------------------------------------------
// 2. CONTAINER COMPONENT (Smart - State & Coordination Only)
// ---------------------------------------------------------
export const DashboardMetricsContainer: React.FC = () => {
  // smart container handles SWR network state fetching
  const { data, error } = useSWR<{ value: number }[]>('/analytics/daily-totals', apiFetcher);
  
  const totalSum = useMemo(() => {
    if (!data) return 0;
    return data.reduce((sum, item) => sum + item.value, 0);
  }, [data]);

  const isLoading = !data && !error;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6">
      {/* 
        Pass values into Presentational card components as simple props.
        Container does not contain layout styles beyond wrapper grids.
      */}
      <StatsDisplay title="Total Daily Sales" value={totalSum} isLoading={isLoading} />
      <StatsDisplay title="Calculated Revenue Pool" value={totalSum * 0.95} isLoading={isLoading} />
    </div>
  );
};
