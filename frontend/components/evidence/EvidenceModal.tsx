'use client';

import { useState, useEffect, useCallback } from 'react';
import { EvidenceItem } from '@/types';
import { EvidenceHighlighter } from './EvidenceHighlighter';
import { EvidenceList } from './EvidenceList';
import { slugToDisplay } from '@/lib/constants';
import { X, FileText, List } from 'lucide-react';

interface EvidenceModalProps {
  isOpen: boolean;
  onClose: () => void;
  metricSlug: string;
  modelAnswer: string;
  evidenceItems: EvidenceItem[];
  userScore?: number | null;
  judgeScore?: number | null;
}

export function EvidenceModal({
  isOpen,
  onClose,
  metricSlug,
  modelAnswer,
  evidenceItems,
  userScore,
  judgeScore,
}: EvidenceModalProps) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const [view, setView] = useState<'combined' | 'text' | 'list'>('combined');

  // Close on Escape
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    },
    [onClose]
  );

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [isOpen, handleKeyDown]);

  if (!isOpen) return null;

  const gap = userScore != null && judgeScore != null ? Math.abs(userScore - judgeScore) : null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col m-4">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold text-slate-900">
              {slugToDisplay(metricSlug)} — Kanıtlar
            </h2>
            {gap !== null && (
              <span
                className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                  gap === 0
                    ? 'bg-emerald-100 text-emerald-700'
                    : gap <= 1
                    ? 'bg-amber-100 text-amber-700'
                    : 'bg-rose-100 text-rose-700'
                }`}
              >
                Gap: {gap}
              </span>
            )}
            {userScore != null && (
              <span className="text-xs text-slate-500">
                Sen: {userScore} | Judge: {judgeScore}
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* View Toggle */}
            <div className="flex bg-slate-100 rounded-lg p-0.5">
              <button
                onClick={() => setView('combined')}
                className={`px-3 py-1 text-xs rounded-md transition-colors ${
                  view === 'combined' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500'
                }`}
              >
                Birlikte
              </button>
              <button
                onClick={() => setView('text')}
                className={`px-3 py-1 text-xs rounded-md transition-colors ${
                  view === 'text' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500'
                }`}
              >
                <FileText className="w-3 h-3" />
              </button>
              <button
                onClick={() => setView('list')}
                className={`px-3 py-1 text-xs rounded-md transition-colors ${
                  view === 'list' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500'
                }`}
              >
                <List className="w-3 h-3" />
              </button>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          {view === 'combined' ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 h-full divide-x divide-slate-200">
              {/* Left: Highlighted Text */}
              <div className="overflow-y-auto p-6">
                <h3 className="text-xs font-medium text-slate-500 mb-3 uppercase tracking-wider">
                  Model Cevabı
                </h3>
                <EvidenceHighlighter
                  text={modelAnswer}
                  evidenceItems={evidenceItems}
                  activeIndex={activeIndex}
                  onHighlightClick={setActiveIndex}
                />
              </div>

              {/* Right: Evidence List */}
              <div className="overflow-y-auto p-6">
                <h3 className="text-xs font-medium text-slate-500 mb-3 uppercase tracking-wider">
                  Kanıtlar ({evidenceItems.length})
                </h3>
                <EvidenceList
                  evidenceItems={evidenceItems}
                  activeIndex={activeIndex}
                  onItemClick={setActiveIndex}
                />
              </div>
            </div>
          ) : view === 'text' ? (
            <div className="overflow-y-auto p-6">
              <h3 className="text-xs font-medium text-slate-500 mb-3 uppercase tracking-wider">
                Model Cevabı
              </h3>
              <EvidenceHighlighter
                text={modelAnswer}
                evidenceItems={evidenceItems}
                activeIndex={activeIndex}
                onHighlightClick={setActiveIndex}
              />
            </div>
          ) : (
            <div className="overflow-y-auto p-6">
              <EvidenceList
                evidenceItems={evidenceItems}
                activeIndex={activeIndex}
                onItemClick={setActiveIndex}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
