// Use Case: Unit Testing React Widgets with Mock SWR Cache States
// Purpose: Seed SWR Config cache and assert visual loading/data display boundaries.
// Key features: SWRConfig mapping, screen query matches, and async finding assertions.

import React from 'react';
import { render, screen } from '@testing-library/react';
import { SWRConfig } from 'swr';
import { SalesWidget } from './SalesWidget'; // Assume component path

const mockData = [
  {
    tenant_id: 1,
    tenant_name: 'Acme Corp',
    sales_date: '2026-07-18',
    daily_sales: 150.0,
    running_cumulative_sales: 150.0,
  },
];

describe('SalesWidget Component SWR Caching Unit Tests', () => {
  it('renders loading skeleton initial state when cache is empty', () => {
    render(
      <SWRConfig value={{ provider: () => new Map() }}>
        <SalesWidget />
      </SWRConfig>
    );

    expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument();
  });

  it('renders sales metrics correctly when cache is seeded', async () => {
    const cacheMap = new Map();
    // Seed SWR cache for the specific API endpoint
    cacheMap.set('/analytics/cumulative-sales', mockData);

    render(
      <SWRConfig value={{ provider: () => cacheMap, dedupingInterval: 0 }}>
        <SalesWidget />
      </SWRConfig>
    );

    // Assert that metric text is rendered correctly
    expect(await screen.findByText('Acme Corp')).toBeInTheDocument();
    expect(screen.getByText('$150.00')).toBeInTheDocument();
  });
});
