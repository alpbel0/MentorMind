import { ReactNode } from 'react';
import { Card } from '@/components/ui/Card';
import { TrendIndicator } from './TrendIndicator';

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
  trend?: 'improving' | 'stable' | 'declining' | 'insufficient_data';
  className?: string;
}

export function StatsCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  className = '',
}: StatsCardProps) {
  return (
    <Card className={className}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="mt-2 text-3xl font-bold text-slate-900">{value}</p>
          {subtitle && (
            <p className="mt-1 text-sm text-slate-500">{subtitle}</p>
          )}
          {trend && (
            <div className="mt-2">
              <TrendIndicator trend={trend} />
            </div>
          )}
        </div>
        {icon && (
          <div className="p-3 bg-indigo-50 rounded-xl text-indigo-600">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}
