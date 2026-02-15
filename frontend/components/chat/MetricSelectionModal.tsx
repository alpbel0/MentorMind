'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { SnapshotResponse } from '@/types';
import { METRIC_SLUGS, slugToDisplay, SLUG_COLORS_LIGHT } from '@/lib/constants';
import type { MetricSlug } from '@/types';
import { X, MessageCircle, CheckCircle } from 'lucide-react';

interface MetricSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  snapshot: SnapshotResponse;
  onStartChat: (selectedMetrics: string[]) => void;
}

const MAX_METRICS = 3;

export function MetricSelectionModal({
  isOpen,
  onClose,
  snapshot,
  onStartChat,
}: MetricSelectionModalProps) {
  const [selected, setSelected] = useState<string[]>([]);

  if (!isOpen) return null;

  const toggleMetric = (slug: string) => {
    setSelected((prev) => {
      if (prev.includes(slug)) return prev.filter((s) => s !== slug);
      if (prev.length >= MAX_METRICS) return prev;
      return [...prev, slug];
    });
  };

  const getGap = (slug: string): number | null => {
    const u = snapshot.user_scores_json?.[slug]?.score;
    const j = snapshot.judge_scores_json?.[slug]?.score;
    if (u == null || j == null) return null;
    return Math.abs(u - j);
  };

  const hasEvidence = (slug: string): boolean => {
    const items = snapshot.evidence_json?.[slug];
    return Array.isArray(items) && items.length > 0;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />

      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg m-4">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Metrik Seç</h2>
            <p className="text-sm text-slate-500">Hangi metrikleri konuşmak istersin? (Max {MAX_METRICS})</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Metric List */}
        <div className="p-6 space-y-2 max-h-[50vh] overflow-y-auto">
          {METRIC_SLUGS.map((slug) => {
            const gap = getGap(slug);
            const isSelected = selected.includes(slug);
            const isDisabled = !isSelected && selected.length >= MAX_METRICS;
            const isNA = gap === null;
            const colorClass = SLUG_COLORS_LIGHT[slug as MetricSlug];

            return (
              <button
                key={slug}
                disabled={isDisabled || isNA}
                onClick={() => toggleMetric(slug)}
                className={`w-full flex items-center justify-between p-3 rounded-lg border transition-all ${
                  isSelected
                    ? 'border-indigo-300 bg-indigo-50 ring-1 ring-indigo-200'
                    : isNA || isDisabled
                    ? 'border-slate-100 bg-slate-50 opacity-50 cursor-not-allowed'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                      isSelected ? 'border-indigo-500 bg-indigo-500' : 'border-slate-300'
                    }`}
                  >
                    {isSelected && <CheckCircle className="w-3 h-3 text-white" />}
                  </div>
                  <span className={`text-sm font-medium ${isSelected ? 'text-indigo-700' : 'text-slate-700'}`}>
                    {slugToDisplay(slug)}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  {hasEvidence(slug) && (
                    <span className="text-[10px] text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded">
                      Kanıt
                    </span>
                  )}
                  {gap !== null ? (
                    <span
                      className={`text-xs font-mono px-2 py-0.5 rounded-full ${
                        gap === 0
                          ? 'bg-emerald-100 text-emerald-700'
                          : gap <= 1
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-rose-100 text-rose-700'
                      }`}
                    >
                      Gap: {gap}
                    </span>
                  ) : (
                    <span className="text-xs text-slate-400">N/A</span>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-200 flex items-center justify-between">
          <p className="text-sm text-slate-500">
            {selected.length}/{MAX_METRICS} metrik seçildi
          </p>
          <Button
            disabled={selected.length === 0}
            onClick={() => onStartChat(selected)}
            icon={<MessageCircle className="w-4 h-4" />}
          >
            Sohbeti Başlat
          </Button>
        </div>
      </div>
    </div>
  );
}
