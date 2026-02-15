'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/Spinner';
import { MessageBubble } from '@/components/chat/MessageBubble';
import { ChatInput } from '@/components/chat/ChatInput';
import { MetricSelectionModal } from '@/components/chat/MetricSelectionModal';
import { useChatStream } from '@/hooks/useChatStream';
import { getSnapshot, getChatHistory } from '@/lib/api';
import { SnapshotResponse, ChatMessage } from '@/types';
import { slugToDisplay } from '@/lib/constants';
import { ArrowLeft, FileText, PenSquare } from 'lucide-react';

function generateUUID(): string {
  return crypto.randomUUID();
}

export default function CoachChatPage() {
  const params = useParams();
  const router = useRouter();
  const snapshotId = params.id as string;

  const [snapshot, setSnapshot] = useState<SnapshotResponse | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
  const [showMetricModal, setShowMetricModal] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chatTurnCount, setChatTurnCount] = useState(0);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { isStreaming, streamedContent, error: streamError, sendInit, sendMessage } =
    useChatStream(snapshotId);

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamedContent, scrollToBottom]);

  // Fetch snapshot and existing chat history
  useEffect(() => {
    async function init() {
      try {
        const [snap, history] = await Promise.all([
          getSnapshot(snapshotId),
          getChatHistory(snapshotId).catch(() => null),
        ]);

        setSnapshot(snap);
        setChatTurnCount(snap.chat_turn_count);

        if (history && history.messages.length > 0) {
          setMessages(history.messages);
          // Extract selected_metrics from first user message
          const firstMsg = history.messages.find(
            (m) => m.selected_metrics && m.selected_metrics.length > 0
          );
          if (firstMsg?.selected_metrics) {
            setSelectedMetrics(firstMsg.selected_metrics);
            setIsInitialized(true);
          }
        }

        // If no messages, show metric selection
        if (!history || history.messages.length === 0) {
          setShowMetricModal(true);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Yüklenemedi');
      } finally {
        setIsLoading(false);
      }
    }
    init();
  }, [snapshotId]);

  // Handle metric selection and init greeting
  const handleStartChat = async (metrics: string[]) => {
    setSelectedMetrics(metrics);
    setShowMetricModal(false);

    // Send init greeting
    await sendInit(metrics, (fullContent) => {
      const initMsg: ChatMessage = {
        id: `init_${snapshotId}`,
        snapshot_id: snapshotId,
        client_message_id: `init_${snapshotId}`,
        role: 'assistant',
        content: fullContent,
        is_complete: true,
        selected_metrics: metrics,
        token_count: 0,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, initMsg]);
      setIsInitialized(true);
    });
  };

  // Handle user message send
  const handleSendMessage = async (text: string) => {
    const clientMessageId = generateUUID();

    // Optimistic add user message
    const userMsg: ChatMessage = {
      id: `local_user_${clientMessageId}`,
      snapshot_id: snapshotId,
      client_message_id: clientMessageId,
      role: 'user',
      content: text,
      is_complete: true,
      selected_metrics: selectedMetrics,
      token_count: 0,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setChatTurnCount((prev) => prev + 1);

    // Send and stream response
    await sendMessage(text, clientMessageId, selectedMetrics, (fullContent) => {
      const assistantMsg: ChatMessage = {
        id: `local_assistant_${clientMessageId}`,
        snapshot_id: snapshotId,
        client_message_id: clientMessageId,
        role: 'assistant',
        content: fullContent,
        is_complete: true,
        selected_metrics: null,
        token_count: 0,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    });
  };

  if (isLoading) return <LoadingState message="Chat yükleniyor..." />;

  if (error || !snapshot) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <p className="text-rose-500 mb-4">{error || 'Snapshot bulunamadı'}</p>
        <Link href="/history">
          <Button variant="outline">Geçmişe Dön</Button>
        </Link>
      </div>
    );
  }

  const maxTurns = snapshot.max_chat_turns;
  const remainingTurns = maxTurns - chatTurnCount;

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)]">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 bg-white shrink-0">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.back()}
            icon={<ArrowLeft className="w-4 h-4" />}
          >
            Geri
          </Button>
          <div className="h-5 w-px bg-slate-200" />
          <div>
            <h2 className="text-sm font-semibold text-slate-900">Coach Sohbeti</h2>
            <div className="flex items-center gap-2 mt-0.5">
              {selectedMetrics.map((slug) => (
                <Badge key={slug} size="sm" className="bg-indigo-100 text-indigo-700">
                  {slugToDisplay(slug)}
                </Badge>
              ))}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Link href={`/snapshots/${snapshotId}`}>
            <Button variant="ghost" size="sm" icon={<FileText className="w-4 h-4" />}>
              Rapor
            </Button>
          </Link>
          <Link href="/evaluate">
            <Button variant="outline" size="sm" icon={<PenSquare className="w-4 h-4" />}>
              Yeni Soru
            </Button>
          </Link>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            role={msg.role}
            content={msg.content}
            timestamp={msg.created_at}
          />
        ))}

        {/* Streaming message */}
        {isStreaming && (
          <MessageBubble
            role="assistant"
            content={streamedContent}
            isTyping={true}
          />
        )}

        {/* Stream error */}
        {streamError && (
          <div className="text-center text-sm text-rose-500 py-2">{streamError}</div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput
        onSend={handleSendMessage}
        disabled={!isInitialized}
        isStreaming={isStreaming}
        remainingTurns={remainingTurns}
        maxTurns={maxTurns}
      />

      {/* Metric Selection Modal */}
      <MetricSelectionModal
        isOpen={showMetricModal}
        onClose={() => {
          if (messages.length > 0) setShowMetricModal(false);
          else router.back();
        }}
        snapshot={snapshot}
        onStartChat={handleStartChat}
      />
    </div>
  );
}
