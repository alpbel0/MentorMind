'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/Spinner';
import { SnapshotMetricCard } from '@/components/snapshot';
import { EvidenceModal } from '@/components/evidence';
import { MetaScoreGauge } from '@/components/stats/MetaScoreGauge';
import { getSnapshot } from '@/lib/api';
import { SnapshotResponse, EvidenceItem } from '@/types';
import { METRIC_SLUGS, slugToDisplay } from '@/lib/constants';
import {
  ArrowLeft,
  MessageCircle,
  PenSquare,
  Clock,
  Tag,
  Bot,
  MessageSquare,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';

export default function SnapshotDetailPage() {
  const params = useParams();
  const router = useRouter();
  const snapshotId = params.id as string;

  const [snapshot, setSnapshot] = useState<SnapshotResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Evidence modal state
  const [evidenceModal, setEvidenceModal] = useState<{
    isOpen: boolean;
    metricSlug: string;
    evidenceItems: EvidenceItem[];
    userScore?: number | null;
    judgeScore?: number | null;
  }>({ isOpen: false, metricSlug: '', evidenceItems: [] });

  useEffect(() => {
    async function fetchSnapshot() {
      try {
        const data = await getSnapshot(snapshotId);
        setSnapshot(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Snapshot yüklenemedi');
      } finally {
        setIsLoading(false);
      }
    }
    fetchSnapshot();
  }, [snapshotId]);

  if (isLoading) return <LoadingState message="Snapshot yükleniyor..." />;

  if (error || !snapshot) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="mb-6 p-4 bg-rose-50 border border-rose-200 rounded-xl">
          <p className="text-rose-700">{error || 'Snapshot bulunamadı'}</p>
        </div>
        <Link href="/history">
          <Button variant="outline">Geçmişe Dön</Button>
        </Link>
      </div>
    );
  }

  const openEvidenceModal = (metricSlug: string) => {
    const evidenceItems = snapshot.evidence_json?.[metricSlug] || [];
    const userScoreData = snapshot.user_scores_json?.[metricSlug];
    const judgeScoreData = snapshot.judge_scores_json?.[metricSlug];
    setEvidenceModal({
      isOpen: true,
      metricSlug,
      evidenceItems,
      userScore: userScoreData?.score ?? null,
      judgeScore: judgeScoreData?.score ?? null,
    });
  };

  const formattedDate = new Date(snapshot.created_at).toLocaleString('tr-TR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  // Calculate improvement areas and positive metrics
  const metricGaps = METRIC_SLUGS.map((slug) => {
    const userScore = snapshot.user_scores_json?.[slug]?.score;
    const judgeScore = snapshot.judge_scores_json?.[slug]?.score;
    const gap = userScore != null && judgeScore != null ? Math.abs(userScore - judgeScore) : null;
    return { slug, gap };
  }).filter((m) => m.gap !== null);

  const badMetrics = metricGaps.filter((m) => m.gap! >= 2);
  const goodMetrics = metricGaps.filter((m) => m.gap! === 0);

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          onClick={() => router.back()}
          icon={<ArrowLeft className="w-4 h-4" />}
        >
          Geri
        </Button>
        <div className="flex gap-3">
          {snapshot.is_chat_available && (
            <Link href={`/snapshots/${snapshotId}/chat`}>
              <Button icon={<MessageCircle className="w-4 h-4" />}>
                Sohbet Başlat
              </Button>
            </Link>
          )}
          <Link href="/evaluate">
            <Button variant="outline" icon={<PenSquare className="w-4 h-4" />}>
              Yeni Değerlendirme
            </Button>
          </Link>
        </div>
      </div>

      {/* Top: Meta Score + Overall Feedback */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Meta Score */}
        <Card className="flex flex-col items-center justify-center py-8">
          <h3 className="text-sm font-medium text-slate-500 mb-4">Değerlendirme Kalitesi</h3>
          <MetaScoreGauge score={snapshot.judge_meta_score || 0} size="lg" />
          <div className="mt-4 flex flex-wrap gap-2 justify-center">
            <Badge className="bg-slate-100 text-slate-600">
              <Tag className="w-3 h-3 mr-1" />
              {snapshot.category}
            </Badge>
            <Badge className="bg-slate-100 text-slate-600">
              <Bot className="w-3 h-3 mr-1" />
              {snapshot.model_name}
            </Badge>
          </div>
          <p className="text-xs text-slate-400 mt-2 flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {formattedDate}
          </p>
        </Card>

        {/* Overall Feedback */}
        <Card className="lg:col-span-2">
          <CardHeader
            title="Genel Geri Bildirim"
            subtitle={`${slugToDisplay(snapshot.primary_metric)} odaklı değerlendirme`}
          />
          <div className="flex items-start gap-3 mb-4">
            <div className="p-2 bg-indigo-100 rounded-lg shrink-0">
              <MessageSquare className="w-5 h-5 text-indigo-600" />
            </div>
            <p className="text-slate-700 text-sm leading-relaxed">{snapshot.overall_feedback}</p>
          </div>
          <div className="flex items-center gap-4 text-xs text-slate-400">
            <span>Ağırlıklı Fark: {snapshot.weighted_gap.toFixed(2)}</span>
            <span>Chat: {snapshot.chat_turn_count}/{snapshot.max_chat_turns}</span>
          </div>
        </Card>
      </div>

      {/* Metric Cards Grid */}
      <Card>
        <CardHeader
          title="Metrik Analizi"
          subtitle="Her metrik için puan karşılaştırması ve kanıtlar"
        />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {METRIC_SLUGS.map((slug) => {
            const userScoreData = snapshot.user_scores_json?.[slug];
            const judgeScoreData = snapshot.judge_scores_json?.[slug];
            const evidenceItems = snapshot.evidence_json?.[slug] || [];

            return (
              <SnapshotMetricCard
                key={slug}
                metricSlug={slug}
                userScore={userScoreData?.score ?? null}
                judgeScore={judgeScoreData?.score ?? null}
                evidenceItems={evidenceItems}
                onViewEvidence={() => openEvidenceModal(slug)}
              />
            );
          })}
        </div>
      </Card>

      {/* Improvement + Positive Areas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Bad */}
        <Card>
          <CardHeader title="İyileştirme Alanları" subtitle="Bu metriklere daha dikkat et" />
          {badMetrics.length > 0 ? (
            <ul className="space-y-2">
              {badMetrics.map((m) => (
                <li key={m.slug} className="flex items-center gap-2 text-sm">
                  <TrendingDown className="w-4 h-4 text-rose-500" />
                  <span className="text-slate-700">
                    {slugToDisplay(m.slug)} <span className="text-rose-500 font-mono">(±{m.gap})</span>
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="flex items-center gap-2 text-emerald-600 text-sm">
              <CheckCircle className="w-4 h-4" />
              Büyük fark yok, iyi gidiyorsun!
            </div>
          )}
        </Card>

        {/* Good */}
        <Card>
          <CardHeader title="İyi Yaptıkların" subtitle="Bu metriklerde hizalı değerlendirme" />
          {goodMetrics.length > 0 ? (
            <ul className="space-y-2">
              {goodMetrics.map((m) => (
                <li key={m.slug} className="flex items-center gap-2 text-sm">
                  <TrendingUp className="w-4 h-4 text-emerald-500" />
                  <span className="text-slate-700">{slugToDisplay(m.slug)}</span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="flex items-center gap-2 text-slate-400 text-sm">
              <AlertCircle className="w-4 h-4" />
              Henüz tam hizalı metrik yok
            </div>
          )}
        </Card>
      </div>

      {/* Question & Model Answer (Collapsible) */}
      <Card>
        <details>
          <summary className="cursor-pointer text-sm font-medium text-slate-600 hover:text-slate-900">
            Soru & Model Cevabını Göster
          </summary>
          <div className="mt-4 space-y-4">
            <div>
              <h4 className="text-xs font-medium text-slate-500 mb-1 uppercase tracking-wider">Soru</h4>
              <p className="text-sm text-slate-700 bg-slate-50 p-4 rounded-lg">{snapshot.question}</p>
            </div>
            <div>
              <h4 className="text-xs font-medium text-slate-500 mb-1 uppercase tracking-wider">Model Cevabı</h4>
              <p className="text-sm text-slate-700 bg-slate-50 p-4 rounded-lg whitespace-pre-wrap font-mono">
                {snapshot.model_answer}
              </p>
            </div>
          </div>
        </details>
      </Card>

      {/* Snapshot ID */}
      <div className="text-center text-xs text-slate-400">
        Snapshot: <code className="font-mono">{snapshot.id}</code>
      </div>

      {/* Evidence Modal */}
      <EvidenceModal
        isOpen={evidenceModal.isOpen}
        onClose={() => setEvidenceModal((prev) => ({ ...prev, isOpen: false }))}
        metricSlug={evidenceModal.metricSlug}
        modelAnswer={snapshot.model_answer}
        evidenceItems={evidenceModal.evidenceItems}
        userScore={evidenceModal.userScore}
        judgeScore={evidenceModal.judgeScore}
      />
    </div>
  );
}
