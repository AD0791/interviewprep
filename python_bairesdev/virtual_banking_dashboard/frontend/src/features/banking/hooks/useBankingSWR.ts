import useSWR, { useSWRConfig } from 'swr';
import { useMemo } from 'react';
import { apiFetcher, httpClient } from '@/config/httpClient';

export interface Account {
  id: number;
  account_number: string;
  holder_name: string;
  balance: number;
  created_at: string;
}

export interface VolumeMetric {
  sales_date: string;
  daily_volume: number;
  running_cumulative_volume: number;
}

export const useBankingSWR = () => {
  const { mutate } = useSWRConfig();

  // Fetch accounts lists
  const { data: accounts, error: accountsErr, mutate: mutateAccounts } = useSWR<Account[]>(
    '/v1/accounts',
    apiFetcher
  );

  // Fetch timeseries analytics volumes
  const { data: metrics, error: metricsErr } = useSWR<VolumeMetric[]>(
    '/v1/analytics/cumulative-volume',
    apiFetcher
  );

  // Memoize total bank deposits pool calculation
  const totalBalance = useMemo(() => {
    if (!accounts) return 0;
    return accounts.reduce((acc, current) => acc + current.balance, 0);
  }, [accounts]);

  const addAccount = async (accountNumber: string, holderName: string, initialBalance: number) => {
    await httpClient.post('/v1/accounts', {
      account_number: accountNumber,
      holder_name: holderName,
      initial_balance: initialBalance
    });
    // Trigger optimistic UI revalidation update
    mutateAccounts();
    mutate('/v1/analytics/cumulative-volume');
  };

  const addTransaction = async (accountId: number, amount: number, type: 'deposit' | 'withdrawal') => {
    await httpClient.post('/v1/transactions', {
      account_id: accountId,
      amount,
      transaction_type: type
    });
    mutateAccounts();
    mutate('/v1/analytics/cumulative-volume');
  };

  return {
    accounts,
    metrics,
    totalBalance,
    isLoading: (!accounts && !accountsErr) || (!metrics && !metricsErr),
    isError: !!accountsErr || !!metricsErr,
    addAccount,
    addTransaction
  };
};
