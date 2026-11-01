"use client";

import React, { useState } from "react";
import { Fuel, PieChart, Receipt, TrendingDown, Wrench } from "lucide-react";

interface ExpensesProps {
  expenses: any[];
  summary: any;
}

export const ExpensesSection: React.FC<ExpensesProps> = ({ expenses, summary }) => {
  const [selectedCategory, setSelectedCategory] = useState<string>("all");

  const analytics = summary?.analytics;
  const earnings = analytics?.earnings;

  const totalExpensePaise = expenses.reduce((acc, curr) => acc + curr.amount_paise, 0);
  const grossPaise = earnings?.gross_paise || 1;
  const expenseRatio = ((totalExpensePaise / Math.max(1, grossPaise)) * 100).toFixed(1);

  // Group by category
  const categoryTotals: Record<string, number> = {};
  expenses.forEach((e) => {
    categoryTotals[e.category] = (categoryTotals[e.category] || 0) + e.amount_paise;
  });

  const filtered = expenses.filter((e) =>
    selectedCategory === "all" ? true : e.category === selectedCategory
  );

  return (
    <div className="p-5 md:p-8 space-y-6 max-w-[1600px] mx-auto select-none">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-content-primary flex items-center space-x-2">
          <span>Attributable Operating Expenses & Cost Burden</span>
        </h2>
        <p className="text-xs text-content-muted mt-0.5">
          Audited operating deductions: fuel, vehicle maintenance, mobile connectivity, and safety gear
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="bg-surface-1 border border-hairline rounded-2xl p-5 shadow-card">
          <span className="text-[10px] text-content-muted uppercase tracking-wider block font-semibold">Total Logged Costs</span>
          <div className="text-2xl font-bold font-mono text-semantic-red mt-1">
            ₹{(totalExpensePaise / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </div>
          <span className="text-[11px] text-content-muted mt-1 block">
            {expenses.length} verified operating expense receipts
          </span>
        </div>

        <div className="bg-surface-1 border border-hairline rounded-2xl p-5 shadow-card">
          <span className="text-[10px] text-content-muted uppercase tracking-wider block font-semibold">Operating Expense Ratio</span>
          <div className="text-2xl font-bold font-mono text-content-primary mt-1">
            {expenseRatio}%
          </div>
          <span className="text-[11px] text-content-muted mt-1 block">
            Fraction of gross earnings consumed by transit costs
          </span>
        </div>

        <div className="bg-surface-1 border border-hairline rounded-2xl p-5 shadow-card">
          <span className="text-[10px] text-content-muted uppercase tracking-wider block font-semibold">Primary Cost Driver</span>
          <div className="text-2xl font-bold font-mono text-lime mt-1 capitalize">
            {Object.keys(categoryTotals)[0] || "Fuel"}
          </div>
          <span className="text-[11px] text-content-muted mt-1 block">
            Petroleum consumption constitutes ~70% of overhead
          </span>
        </div>
      </div>

      {/* Categories Bar Distribution */}
      <div className="bg-surface-1 border border-hairline rounded-2xl p-6 space-y-4 shadow-card">
        <h3 className="font-semibold text-xs text-content-primary uppercase tracking-wider">
          Expense Category Breakdown
        </h3>

        <div className="space-y-3">
          {Object.entries(categoryTotals).map(([cat, amt]) => {
            const pct = ((amt / Math.max(1, totalExpensePaise)) * 100).toFixed(1);
            return (
              <div key={cat} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="font-medium capitalize text-content-primary">{cat}</span>
                  <span className="font-mono text-content-muted">
                    ₹{(amt / 100).toFixed(2)} ({pct}%)
                  </span>
                </div>
                <div className="w-full bg-surface-2 h-2 rounded-full overflow-hidden border border-hairline/40">
                  <div
                    className="bg-lime h-full rounded-full transition-all duration-500 shadow-lime-sm"
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Expenses Table */}
      <div className="bg-surface-1 border border-hairline rounded-2xl overflow-hidden shadow-card">
        <div className="p-5 border-b border-hairline flex justify-between items-center">
          <h3 className="font-semibold text-xs text-content-primary uppercase tracking-wider">Verified Receipts</h3>
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-content-muted text-[10px] uppercase font-semibold">Filter:</span>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-surface-2 border border-hairline rounded-full px-3 py-1 text-xs text-content-primary focus:outline-none cursor-pointer"
            >
              <option value="all" className="bg-surface-1">All Categories</option>
              {Object.keys(categoryTotals).map((cat) => (
                <option key={cat} value={cat} className="bg-surface-1">
                  {cat}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="overflow-x-auto max-h-80 overflow-y-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-surface-2/80 text-content-muted uppercase text-[10px] tracking-wider sticky top-0 border-b border-hairline backdrop-blur-sm">
              <tr>
                <th className="py-3 px-4 font-semibold">Date & Time</th>
                <th className="py-3 px-4 font-semibold">Category</th>
                <th className="py-3 px-4 font-semibold">Notes</th>
                <th className="py-3 px-4 text-right font-semibold">Amount (INR)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-hairline">
              {filtered.map((e) => (
                <tr key={e.id} className="hover:bg-surface-hover/50 transition-colors">
                  <td className="py-2.5 px-4 text-content-secondary font-mono text-[11px] whitespace-nowrap">
                    {new Date(e.occurred_at).toLocaleString("en-IN", {
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </td>
                  <td className="py-2.5 px-4 font-semibold capitalize text-content-primary whitespace-nowrap">
                    {e.category}
                  </td>
                  <td className="py-2.5 px-4 text-content-muted text-[11px]">{e.notes || "—"}</td>
                  <td className="py-2.5 px-4 text-right font-mono font-bold text-semantic-red whitespace-nowrap">
                    ₹{(e.amount_paise / 100).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
