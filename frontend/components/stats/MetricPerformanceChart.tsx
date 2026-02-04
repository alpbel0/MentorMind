'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { MetricName, MetricPerformance } from '@/types';
import { METRIC_COLORS } from '@/lib/constants';

interface MetricPerformanceChartProps {
  data: Partial<Record<MetricName, MetricPerformance>>;
}

const barColors: Record<MetricName, string> = {
  Truthfulness: '#3b82f6',
  Helpfulness: '#10b981',
  Safety: '#f43f5e',
  Bias: '#a855f7',
  Clarity: '#f59e0b',
  Consistency: '#06b6d4',
  Efficiency: '#f97316',
  Robustness: '#6366f1',
};

export function MetricPerformanceChart({ data }: MetricPerformanceChartProps) {
  const chartData = Object.entries(data).map(([metric, perf]) => ({
    metric: metric.slice(0, 8), // Truncate for display
    fullMetric: metric,
    avgGap: perf?.avg_gap || 0,
    count: perf?.count || 0,
    trend: perf?.trend || 'insufficient_data',
  }));

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400">
        No evaluation data yet
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis
          dataKey="metric"
          tick={{ fontSize: 12, fill: '#64748b' }}
          axisLine={{ stroke: '#e2e8f0' }}
        />
        <YAxis
          tick={{ fontSize: 12, fill: '#64748b' }}
          axisLine={{ stroke: '#e2e8f0' }}
          domain={[0, 'auto']}
          label={{
            value: 'Avg Gap',
            angle: -90,
            position: 'insideLeft',
            style: { fontSize: 12, fill: '#64748b' },
          }}
        />
        <Tooltip
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              const data = payload[0].payload;
              return (
                <div className="bg-white p-3 rounded-lg shadow-lg border border-slate-200">
                  <p className="font-medium text-slate-900">{data.fullMetric}</p>
                  <p className="text-sm text-slate-600">
                    Avg Gap: <span className="font-mono">{data.avgGap.toFixed(2)}</span>
                  </p>
                  <p className="text-sm text-slate-600">
                    Evaluations: <span className="font-mono">{data.count}</span>
                  </p>
                  <p className="text-sm text-slate-600">
                    Trend: <span className="capitalize">{data.trend.replace('_', ' ')}</span>
                  </p>
                </div>
              );
            }
            return null;
          }}
        />
        <Bar dataKey="avgGap" radius={[4, 4, 0, 0]}>
          {chartData.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={barColors[entry.fullMetric as MetricName] || '#6366f1'}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
