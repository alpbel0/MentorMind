'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/Spinner';
import { listSnapshots } from '@/lib/api';
import { SnapshotListItem, SnapshotListResponse } from '@/types';
import { slugToDisplay, SLUG_COLORS_LIGHT } from '@/lib/constants';
import type { MetricSlug } from '@/types';
import {
  PenSquare,
  MessageCircle,
  FileText,
  Clock,
  Star,
  ChevronLeft,
  ChevronRight,
  BookOpen,
} from 'lucide-react';

const PAGE_SIZE = 20;

export default function SnapshotsPage() {
  const [data, setData] = useState<SnapshotListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);

  const fetchData = async (offset: number) => {
    setIsLoading(true);
    try {
      const result = await listSnapshots(PAGE_SIZE, offset);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Yüklenemedi');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData(page * PAGE_SIZE);
  }, [page]);

  if (isLoading && !data) return <LoadingState message="Snapshotlar yükleniyor..." />;

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-rose-500 mb-4">{error}</p>
        <Button onClick={() => fetchData(page * PAGE_SIZE)}>Tekrar Dene</Button>
      </div>
    );
  }

  const items = data?.items || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Değerlendirme Snapshotları</h1>
          <p className="text-sm text-slate-500">
            {total > 0 ? `${total} snapshot` : 'Henüz snapshot yok'}
          </p>
        </div>
        <Link href="/evaluate">
          <Button icon={<PenSquare className="w-4 h-4" />}>Yeni Değerlendirme</Button>
        </Link>
      </div>

      {/* Content */}
      {items.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {items.map((item) => (
              <SnapshotCard key={item.id} item={item} />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-4">
              <Button
                variant="outline"
                size="sm"
                disabled={page === 0}
                onClick={() => setPage((p) => p - 1)}
                icon={<ChevronLeft className="w-4 h-4" />}
              >
                Önceki
              </Button>
              <span className="text-sm text-slate-500">
                {page + 1} / {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= totalPages - 1}
                onClick={() => setPage((p) => p + 1)}
              >
                Sonraki
                <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
          )}
        </>
      ) : (
        <Card>
          <div className="text-center py-12">
            <BookOpen className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Henüz Snapshot Yok</h3>
            <p className="text-slate-500 mb-6 max-w-md mx-auto">
              İlk değerlendirmeni yap ve Judge geri bildirimi aldıktan sonra burada snapshotlarını göreceksin.
            </p>
            <Link href="/evaluate">
              <Button icon={<PenSquare className="w-4 h-4" />} size="lg">
                İlk Değerlendirmeyi Başlat
              </Button>
            </Link>
          </div>
        </Card>
      )}
    </div>
  );
}

function SnapshotCard({ item }: { item: SnapshotListItem }) {
  const colorClasses = SLUG_COLORS_LIGHT[item.primary_metric as MetricSlug] || 'bg-slate-100 text-slate-700';
  const date = new Date(item.created_at).toLocaleString('tr-TR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <Card hover className="flex flex-col">
      <div className="flex items-start justify-between mb-3">
        <Badge className={colorClasses}>{slugToDisplay(item.primary_metric)}</Badge>
        <div className="flex items-center gap-1">
          {Array.from({ length: 5 }).map((_, i) => (
            <Star
              key={i}
              className={`w-3.5 h-3.5 ${
                i < item.judge_meta_score ? 'text-amber-400 fill-amber-400' : 'text-slate-200'
              }`}
            />
          ))}
        </div>
      </div>

      <div className="flex items-center gap-2 text-xs text-slate-500 mb-3">
        <Badge size="sm">{item.category}</Badge>
        {item.model_name && (
          <span className="text-slate-400">{item.model_name}</span>
        )}
      </div>

      <div className="flex items-center gap-1 text-xs text-slate-400 mb-4">
        <Clock className="w-3 h-3" />
        {date}
      </div>

      <div className="mt-auto flex items-center gap-2">
        <Link href={`/snapshots/${item.id}`} className="flex-1">
          <Button variant="outline" size="sm" className="w-full" icon={<FileText className="w-3.5 h-3.5" />}>
            Detay
          </Button>
        </Link>
        <Link href={`/snapshots/${item.id}/chat`} className="flex-1">
          <Button size="sm" className="w-full" icon={<MessageCircle className="w-3.5 h-3.5" />}>
            Sohbet
          </Button>
        </Link>
      </div>
    </Card>
  );
}
