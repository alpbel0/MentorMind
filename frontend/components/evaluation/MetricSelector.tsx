'use client';

import {
  CheckCircle,
  HelpCircle,
  Shield,
  Scale,
  Eye,
  Link,
  Zap,
  Lock,
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { MetricName } from '@/types';
import { METRICS, METRIC_DESCRIPTIONS, METRIC_COLORS_LIGHT } from '@/lib/constants';

interface MetricSelectorProps {
  selectedMetric: MetricName | null;
  onSelect: (metric: MetricName) => void;
}

const metricIcons: Record<MetricName, React.ElementType> = {
  Truthfulness: CheckCircle,
  Helpfulness: HelpCircle,
  Safety: Shield,
  Bias: Scale,
  Clarity: Eye,
  Consistency: Link,
  Efficiency: Zap,
  Robustness: Lock,
};

export function MetricSelector({ selectedMetric, onSelect }: MetricSelectorProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {METRICS.map((metric) => {
        const Icon = metricIcons[metric];
        const isSelected = selectedMetric === metric;
        const colorClasses = METRIC_COLORS_LIGHT[metric];

        return (
          <Card
            key={metric}
            hover
            onClick={() => onSelect(metric)}
            className={`cursor-pointer transition-all duration-200 ${
              isSelected
                ? `ring-2 ring-indigo-500 ${colorClasses}`
                : 'hover:border-slate-300'
            }`}
          >
            <div className="flex flex-col items-center text-center">
              <div
                className={`p-3 rounded-xl mb-3 ${
                  isSelected ? 'bg-white/50' : colorClasses.split(' ')[0]
                }`}
              >
                <Icon
                  className={`w-6 h-6 ${
                    isSelected
                      ? colorClasses.split(' ')[1]
                      : colorClasses.split(' ')[1]
                  }`}
                />
              </div>
              <h3 className="font-semibold text-slate-900">{metric}</h3>
              <p className="text-xs text-slate-500 mt-1">
                {METRIC_DESCRIPTIONS[metric]}
              </p>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
