import React, { useState } from 'react';
import { useBankingSWR } from '../hooks/useBankingSWR';
import { useFormik } from 'formik';
import { z } from 'zod';

// Form validation schema using Zod
const accountSchema = z.object({
  accountNumber: z.string().min(10, 'Account number must be at least 10 chars').max(34),
  holderName: z.string().min(2, 'Name must be at least 2 chars'),
  initialBalance: z.coerce.number().min(0, 'Initial balance cannot be negative'),
});

type AccountFormData = z.infer<typeof accountSchema>;

export const BankingDashboard: React.FC = () => {
  const { accounts, metrics, totalBalance, isLoading, isError, addAccount, addTransaction } = useBankingSWR();
  const [selectedAccountId, setSelectedAccountId] = useState<number | null>(null);
  const [txAmount, setTxAmount] = useState<number>(0);
  const [txType, setTxType] = useState<'deposit' | 'withdrawal'>('deposit');
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Formik validation setup
  const formik = useFormik<AccountFormData>({
    initialValues: {
      accountNumber: '',
      holderName: '',
      initialBalance: 0,
    },
    validate: (values) => {
      const result = accountSchema.safeParse(values);
      if (result.success) return {};
      const errors: Record<string, string> = {};
      for (const issue of result.error.issues) {
        if (issue.path[0]) {
          errors[issue.path[0].toString()] = issue.message;
        }
      }
      return errors;
    },
    onSubmit: async (values, { resetForm }) => {
      try {
        setSubmitError(null);
        await addAccount(values.accountNumber, values.holderName, values.initialBalance);
        resetForm();
      } catch (err: any) {
        setSubmitError(err.response?.data?.detail || 'Failed to create account');
      }
    },
  });

  const handleTransactionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAccountId || txAmount <= 0) return;
    try {
      setSubmitError(null);
      await addTransaction(selectedAccountId, txAmount, txType);
      setTxAmount(0);
    } catch (err: any) {
      setSubmitError(err.response?.data?.detail || 'Transaction failed');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#030712]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#030712] text-red-500 font-bold">
        Error loading banking aggregates. Ensure Docker database is healthy.
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* 1. Header */}
      <div className="flex justify-between items-center mb-8 border-b border-[#1f2937] pb-6">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-white flex items-center gap-2">
            🏦 AESTHETIX <span className="text-blue-500">VIRTUAL BANK</span>
          </h1>
          <p className="text-gray-400 text-sm mt-1">Core Banking Real-time Telemetry Control</p>
        </div>
        <div className="text-right">
          <span className="text-xs font-bold uppercase text-gray-400">Total System Deposits</span>
          <p className="text-3xl font-black text-emerald-400">${totalBalance.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
        </div>
      </div>

      {submitError && (
        <div className="bg-red-950 border border-red-800 text-red-400 px-4 py-3 rounded-lg mb-6 text-sm font-semibold">
          ⚠️ {submitError}
        </div>
      )}

      {/* 2. Visual Area SVG Chart */}
      <div className="bg-[#111827] border border-[#1f2937] rounded-2xl p-6 mb-8">
        <h3 className="text-sm font-bold uppercase text-gray-400 mb-4">Cumulative System Transaction Volume</h3>
        <div className="h-64 flex items-end relative border-l border-b border-gray-800 pt-4 px-2">
          {metrics && metrics.length > 0 ? (
            <svg className="w-full h-full" viewBox="0 0 1000 200" preserveAspectRatio="none">
              <defs>
                <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.4" />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
                </linearGradient>
              </defs>
              {/* Draw area */}
              <path
                d={`M 0,200 ${metrics.map((m, idx) => {
                  const x = (idx / (metrics.length - 1)) * 1000;
                  const maxVal = Math.max(...metrics.map(x => x.running_cumulative_volume), 100);
                  const y = 200 - (m.running_cumulative_volume / maxVal) * 160;
                  return `L ${x},${y}`;
                }).join(' ')} L 1000,200 Z`}
                fill="url(#chartGrad)"
              />
              {/* Draw stroke line */}
              <path
                d={metrics.map((m, idx) => {
                  const x = (idx / (metrics.length - 1)) * 1000;
                  const maxVal = Math.max(...metrics.map(x => x.running_cumulative_volume), 100);
                  const y = 200 - (m.running_cumulative_volume / maxVal) * 160;
                  return `${idx === 0 ? 'M' : 'L'} ${x},${y}`;
                }).join(' ')}
                fill="none"
                stroke="#3b82f6"
                strokeWidth="3"
              />
            </svg>
          ) : (
            <div className="absolute inset-0 flex items-center justify-center text-gray-600 text-sm font-semibold">
              No transactions recorded yet to build time series volumes.
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* 3. Accounts list */}
        <div className="lg:col-span-2 bg-[#111827] border border-[#1f2937] rounded-2xl p-6">
          <h3 className="text-sm font-bold uppercase text-gray-400 mb-4">Accounts Pool</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-[#1f2937] text-gray-500 text-xs font-bold uppercase">
                  <th className="py-3 px-4">Holder Name</th>
                  <th className="py-3 px-4">Account Number</th>
                  <th className="py-3 px-4 text-right">Balance</th>
                  <th className="py-3 px-4 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1f2937] text-sm">
                {accounts && accounts.map((acc) => (
                  <tr
                    key={acc.id}
                    className={`hover:bg-gray-900 transition-colors ${selectedAccountId === acc.id ? 'bg-blue-950/30' : ''}`}
                  >
                    <td className="py-4 px-4 font-semibold text-white">{acc.holder_name}</td>
                    <td className="py-4 px-4 font-mono text-gray-400">{acc.account_number}</td>
                    <td className="py-4 px-4 text-right font-black text-emerald-400">${acc.balance.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                    <td className="py-4 px-4 text-center">
                      <button
                        onClick={() => setSelectedAccountId(acc.id)}
                        className="text-xs bg-blue-600/20 text-blue-400 border border-blue-500/30 hover:bg-blue-600 hover:text-white px-3 py-1.5 rounded-lg transition-all font-bold"
                      >
                        Adjust
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 4. Action Panel Forms */}
        <div className="space-y-8">
          {/* Create account form */}
          <div className="bg-[#111827] border border-[#1f2937] rounded-2xl p-6">
            <h3 className="text-sm font-bold uppercase text-gray-400 mb-4">Register Account</h3>
            <form onSubmit={formik.handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase text-gray-500 mb-1">Holder Name</label>
                <input
                  name="holderName"
                  type="text"
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  value={formik.values.holderName}
                  className="w-full bg-gray-900 border border-[#1f2937] p-2.5 rounded-lg text-sm text-white focus:outline-none focus:border-blue-500"
                />
                {formik.touched.holderName && formik.errors.holderName && (
                  <div className="text-red-500 text-xs mt-1">{formik.errors.holderName}</div>
                )}
              </div>
              <div>
                <label className="block text-xs font-bold uppercase text-gray-500 mb-1">Account Number (IBAN)</label>
                <input
                  name="accountNumber"
                  type="text"
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  value={formik.values.accountNumber}
                  className="w-full bg-gray-900 border border-[#1f2937] p-2.5 rounded-lg text-sm font-mono text-white focus:outline-none focus:border-blue-500"
                />
                {formik.touched.accountNumber && formik.errors.accountNumber && (
                  <div className="text-red-500 text-xs mt-1">{formik.errors.accountNumber}</div>
                )}
              </div>
              <div>
                <label className="block text-xs font-bold uppercase text-gray-500 mb-1">Initial Balance ($)</label>
                <input
                  name="initialBalance"
                  type="number"
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  value={formik.values.initialBalance}
                  className="w-full bg-gray-900 border border-[#1f2937] p-2.5 rounded-lg text-sm text-white focus:outline-none focus:border-blue-500"
                />
                {formik.touched.initialBalance && formik.errors.initialBalance && (
                  <div className="text-red-500 text-xs mt-1">{formik.errors.initialBalance}</div>
                )}
              </div>
              <button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 py-2.5 rounded-lg font-bold text-sm text-white transition-colors"
              >
                Register
              </button>
            </form>
          </div>

          {/* Adjust transaction form */}
          {selectedAccountId && (
            <div className="bg-[#111827] border border-[#1f2937] rounded-2xl p-6">
              <h3 className="text-sm font-bold uppercase text-gray-400 mb-4">Post Transaction</h3>
              <form onSubmit={handleTransactionSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold uppercase text-gray-500 mb-1">Amount ($)</label>
                  <input
                    type="number"
                    value={txAmount}
                    onChange={(e) => setTxAmount(Number(e.target.value))}
                    className="w-full bg-gray-900 border border-[#1f2937] p-2.5 rounded-lg text-sm text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-gray-500 mb-1">Transaction Type</label>
                  <select
                    value={txType}
                    onChange={(e) => setTxType(e.target.value as 'deposit' | 'withdrawal')}
                    className="w-full bg-gray-900 border border-[#1f2937] p-2.5 rounded-lg text-sm text-white focus:outline-none"
                  >
                    <option value="deposit">Deposit</option>
                    <option value="withdrawal">Withdrawal</option>
                  </select>
                </div>
                <button
                  type="submit"
                  className="w-full bg-emerald-600 hover:bg-emerald-700 py-2.5 rounded-lg font-bold text-sm text-white transition-colors"
                >
                  Execute Transaction
                </button>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
