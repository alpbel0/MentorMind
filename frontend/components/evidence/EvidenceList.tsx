'use client';

import { EvidenceItem } from '@/types';
import { CheckCircle, AlertTriangle, XCircle, Quote } from 'lucide-react';

interface EvidenceListProps {
  evidenceItems: EvidenceItem[];
  activeIndex?: number | null;
  onItemClick?: (index: number) => void;
}

export function EvidenceList({ evidenceItems, activeIndex = null, onItemClick }: EvidenceListProps) {
  if (!evidenceItems || evidenceItems.length === 0) {
    return (
      <div className="text-center py-6 text-slate-400">
        <Quote className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">Bu metrik için kanıt bulunamadı</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {evidenceItems.map((item, index) => {
        const isActive = activeIndex === index;
        return (
          <div
            key={index}
            onClick={() => onItemClick?.(index)}
            className={`p-4 rounded-lg border cursor-pointer transition-all ${
              isActive
                ? 'border-amber-300 bg-amber-50 shadow-sm'
                : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
            }`}
          >
            {/* Quote */}
            <div className="flex items-start gap-2 mb-3">
              <Quote className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" />
              <p className="text-sm font-mono text-slate-800 italic leading-relaxed">
                &ldquo;{item.quote}&rdquo;
              </p>
            </div>

            {/* Why */}
            <div className="mb-2 pl-6">
              <p className="text-xs font-medium text-slate-500 mb-0.5">Neden:</p>
              <p className="text-sm text-slate-700">{item.why}</p>
            </div>

            {/* Better */}
            {item.better && (
              <div className="mb-2 pl-6">
                <p className="text-xs font-medium text-emerald-600 mb-0.5">Daha iyi:</p>
                <p className="text-sm text-slate-700">{item.better}</p>
              </div>
            )}

            {/* Verification Badge */}
            <div className="pl-6 mt-2">
              <VerificationBadge verified={item.verified} highlightAvailable={item.highlight_available} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

function VerificationBadge({
  verified,
  highlightAvailable,
}: {
  verified: boolean;
  highlightAvailable: boolean;
}) {
  if (verified && highlightAvailable) {
    return (
      <span className="inline-flex items-center gap-1 text-xs text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
        <CheckCircle className="w-3 h-3" />
        Doğrulandı
      </span>
    );
  }

  if (verified && !highlightAvailable) {
    return (
      <span className="inline-flex items-center gap-1 text-xs text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full">
        <AlertTriangle className="w-3 h-3" />
        Pozisyon tespit edilemedi
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 text-xs text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full">
      <XCircle className="w-3 h-3" />
      Kanıt doğrulanamadı
    </span>
  );
}
