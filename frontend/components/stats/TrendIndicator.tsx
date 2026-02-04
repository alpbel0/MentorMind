import { TrendingUp, TrendingDown, Minus, HelpCircle } from 'lucide-react';

interface TrendIndicatorProps {
  trend: 'improving' | 'stable' | 'declining' | 'insufficient_data';
  showLabel?: boolean;
  size?: 'sm' | 'md';
}

const trendConfig = {
  improving: {
    icon: TrendingUp,
    color: 'text-emerald-600',
    bg: 'bg-emerald-50',
    label: 'Improving',
  },
  stable: {
    icon: Minus,
    color: 'text-slate-600',
    bg: 'bg-slate-50',
    label: 'Stable',
  },
  declining: {
    icon: TrendingDown,
    color: 'text-rose-600',
    bg: 'bg-rose-50',
    label: 'Declining',
  },
  insufficient_data: {
    icon: HelpCircle,
    color: 'text-slate-400',
    bg: 'bg-slate-50',
    label: 'Insufficient Data',
  },
};

const sizeClasses = {
  sm: { icon: 'w-3 h-3', text: 'text-xs', padding: 'px-1.5 py-0.5' },
  md: { icon: 'w-4 h-4', text: 'text-sm', padding: 'px-2 py-1' },
};

export function TrendIndicator({
  trend,
  showLabel = true,
  size = 'sm',
}: TrendIndicatorProps) {
  const config = trendConfig[trend];
  const sizes = sizeClasses[size];
  const Icon = config.icon;

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full font-medium ${config.color} ${config.bg} ${sizes.padding} ${sizes.text}`}
    >
      <Icon className={sizes.icon} />
      {showLabel && <span>{config.label}</span>}
    </span>
  );
}
