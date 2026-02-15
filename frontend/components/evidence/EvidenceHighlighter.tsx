'use client';

import { useMemo, useRef } from 'react';
import { EvidenceItem } from '@/types';

interface HighlightSegment {
  text: string;
  isHighlight: boolean;
  evidenceIndex?: number;
  evidence?: EvidenceItem;
}

interface EvidenceHighlighterProps {
  text: string;
  evidenceItems: EvidenceItem[];
  activeIndex?: number | null;
  onHighlightClick?: (index: number) => void;
}

export function EvidenceHighlighter({
  text,
  evidenceItems,
  activeIndex = null,
  onHighlightClick,
}: EvidenceHighlighterProps) {
  const highlightRefs = useRef<Map<number, HTMLElement>>(new Map());

  const segments = useMemo(() => {
    if (!evidenceItems || evidenceItems.length === 0) {
      return [{ text, isHighlight: false }] as HighlightSegment[];
    }

    // Only include items with verified=true and highlight_available=true
    const highlightable = evidenceItems
      .map((item, idx) => ({ ...item, originalIndex: idx }))
      .filter((item) => item.verified && item.highlight_available)
      .sort((a, b) => a.start - b.start);

    if (highlightable.length === 0) {
      return [{ text, isHighlight: false }] as HighlightSegment[];
    }

    const result: HighlightSegment[] = [];
    let lastEnd = 0;

    for (const item of highlightable) {
      const start = Math.max(0, Math.min(item.start, text.length));
      const end = Math.max(start, Math.min(item.end, text.length));

      // Skip overlapping highlights
      if (start < lastEnd) continue;

      // Text before highlight
      if (start > lastEnd) {
        result.push({ text: text.slice(lastEnd, start), isHighlight: false });
      }

      // Highlighted text
      result.push({
        text: text.slice(start, end),
        isHighlight: true,
        evidenceIndex: item.originalIndex,
        evidence: item,
      });

      lastEnd = end;
    }

    // Remaining text
    if (lastEnd < text.length) {
      result.push({ text: text.slice(lastEnd), isHighlight: false });
    }

    return result;
  }, [text, evidenceItems]);

  return (
    <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap font-mono">
      {segments.map((seg, i) => {
        if (!seg.isHighlight) {
          return <span key={i}>{seg.text}</span>;
        }

        const isActive = activeIndex === seg.evidenceIndex;

        return (
          <mark
            key={i}
            ref={(el) => {
              if (el && seg.evidenceIndex !== undefined) {
                highlightRefs.current.set(seg.evidenceIndex, el);
              }
            }}
            className={`cursor-pointer rounded px-0.5 transition-colors ${
              isActive
                ? 'bg-amber-300 ring-2 ring-amber-400'
                : 'bg-amber-100 hover:bg-amber-200'
            }`}
            onClick={() => {
              if (onHighlightClick && seg.evidenceIndex !== undefined) {
                onHighlightClick(seg.evidenceIndex);
              }
            }}
            title={seg.evidence?.why || ''}
          >
            {seg.text}
          </mark>
        );
      })}
    </div>
  );
}

export function scrollToHighlight(
  containerRef: React.RefObject<HTMLElement | null>,
  highlightRefs: Map<number, HTMLElement>,
  index: number
) {
  const el = highlightRefs.get(index);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}
