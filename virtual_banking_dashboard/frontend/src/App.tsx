import React from 'react';
import { BankingDashboard } from './features/banking/components/BankingDashboard';

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#030712] text-[#f3f4f6]">
      <BankingDashboard />
    </div>
  );
};

export default App;
