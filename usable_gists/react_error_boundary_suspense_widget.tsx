// Use Case: Resilient Dashboard Widget Shell (Error Boundary + Suspense + SWR)
// Purpose: Give every widget an independent blast radius — one widget's crash or
//          slow query never blanks the dashboard — with a Retry that actually works.
// Key features: react-error-boundary, SWR suspense mode, reset-triggers-revalidate,
//               resetKeys clearing stale errors on filter change.
// Deps: npm i swr react-error-boundary

import React, { Suspense } from "react";
import useSWR, { useSWRConfig } from "swr";
import { ErrorBoundary, type FallbackProps } from "react-error-boundary";

// 1. Fallbacks -----------------------------------------------------------------

function WidgetErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div role="alert" className="rounded-lg border border-red-300 bg-red-50 p-4">
      <p className="font-semibold text-red-700">This widget failed to load.</p>
      <p className="text-sm text-red-600">{(error as Error).message}</p>
      <button
        onClick={resetErrorBoundary}
        className="mt-2 rounded bg-red-600 px-3 py-1 text-white"
      >
        Retry
      </button>
    </div>
  );
}

function WidgetSkeleton() {
  return <div className="h-40 animate-pulse rounded-lg bg-gray-200" aria-busy="true" />;
}

// 2. The shell: ErrorBoundary wraps Suspense wraps the data component ----------
//    Order matters: a suspense-mode SWR error THROWS during render, and only the
//    boundary above the Suspense catches it.

interface WidgetShellProps {
  swrKey: string; // the exact SWR key the child uses — reset must revalidate it
  children: React.ReactNode;
}

export function WidgetShell({ swrKey, children }: WidgetShellProps) {
  const { mutate } = useSWRConfig();
  return (
    <ErrorBoundary
      FallbackComponent={WidgetErrorFallback}
      // Reset alone would re-render into the same poisoned cache entry;
      // revalidating the key makes Retry a real retry.
      onReset={() => void mutate(swrKey)}
      // Changing filters produces a new key — auto-clear the stale error state.
      resetKeys={[swrKey]}
      onError={(error) => {
        // Centralized reporting: one instrumented boundary, not try/catch confetti.
        console.error(`[widget:${swrKey}]`, error);
      }}
    >
      <Suspense fallback={<WidgetSkeleton />}>{children}</Suspense>
    </ErrorBoundary>
  );
}

// 3. A data component in suspense mode -----------------------------------------
//    No isLoading/error ternaries: pending suspends to the skeleton,
//    failure throws to the boundary, so the happy path is the only path here.

interface Summary {
  tenantId: number;
  totalVolume: number;
  txCount: number;
}

const fetcher = async (url: string): Promise<Summary> => {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`API ${res.status} on ${url}`);
  return res.json();
};

function RevenueSummary({ tenantId }: { tenantId: number }) {
  const key = `/api/v1/analytics/summary/${tenantId}`;
  const { data } = useSWR<Summary>(key, fetcher, { suspense: true });
  return (
    <div className="rounded-lg border p-4">
      <h3 className="text-sm text-gray-500">Total Volume</h3>
      <p className="text-2xl font-bold">${data!.totalVolume.toLocaleString()}</p>
      <p className="text-xs text-gray-400">{data!.txCount} transactions</p>
    </div>
  );
}

// 4. Composition: each widget fails, loads, and retries independently ----------

export function Dashboard({ tenantId }: { tenantId: number }) {
  const summaryKey = `/api/v1/analytics/summary/${tenantId}`;
  return (
    <div className="grid grid-cols-3 gap-4">
      <WidgetShell swrKey={summaryKey}>
        <RevenueSummary tenantId={tenantId} />
      </WidgetShell>
      {/* Sibling widgets get their own shells — a crash here never reaches them */}
    </div>
  );
}
