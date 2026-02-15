'use client';

import { useState, useCallback, useRef } from 'react';
import { initChatGreeting, sendChatMessage } from '@/lib/api';

interface StreamState {
  isStreaming: boolean;
  streamedContent: string;
  error: string | null;
}

export function useChatStream(snapshotId: string) {
  const [state, setState] = useState<StreamState>({
    isStreaming: false,
    streamedContent: '',
    error: null,
  });
  const abortRef = useRef<AbortController | null>(null);

  const processSSEStream = useCallback(
    async (response: Response, onComplete: (fullContent: string) => void) => {
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Hata oluştu' }));
        const errorMsg = errorData.error === 'turn_limit_reached'
          ? 'Mesaj limitine ulaşıldı'
          : errorData.detail || `HTTP ${response.status}`;
        setState((prev) => ({ ...prev, isStreaming: false, error: errorMsg }));
        return;
      }

      const reader = response.body?.getReader();
      if (!reader) {
        setState((prev) => ({ ...prev, isStreaming: false, error: 'Stream okunamadı' }));
        return;
      }

      const decoder = new TextDecoder();
      let accumulated = '';
      let buffer = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed || !trimmed.startsWith('data: ')) continue;

            const data = trimmed.slice(6);
            if (data === '[DONE]') {
              setState((prev) => ({ ...prev, isStreaming: false }));
              onComplete(accumulated);
              return;
            }

            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                accumulated += parsed.content;
                setState((prev) => ({
                  ...prev,
                  streamedContent: accumulated,
                }));
              }
            } catch {
              // Partial JSON, skip
            }
          }
        }

        // Stream ended without [DONE]
        if (accumulated) {
          setState((prev) => ({ ...prev, isStreaming: false }));
          onComplete(accumulated);
        }
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          setState((prev) => ({
            ...prev,
            isStreaming: false,
            error: 'Bağlantı kesildi',
          }));
        }
      }
    },
    []
  );

  const sendInit = useCallback(
    async (
      selectedMetrics: string[],
      onComplete: (fullContent: string) => void
    ) => {
      setState({ isStreaming: true, streamedContent: '', error: null });

      try {
        const response = await initChatGreeting(snapshotId, selectedMetrics);
        await processSSEStream(response, onComplete);
      } catch (err) {
        setState((prev) => ({
          ...prev,
          isStreaming: false,
          error: err instanceof Error ? err.message : 'Init hatası',
        }));
      }
    },
    [snapshotId, processSSEStream]
  );

  const sendMessage = useCallback(
    async (
      message: string,
      clientMessageId: string,
      selectedMetrics: string[],
      onComplete: (fullContent: string) => void
    ) => {
      setState({ isStreaming: true, streamedContent: '', error: null });

      try {
        const response = await sendChatMessage(
          snapshotId,
          message,
          clientMessageId,
          selectedMetrics
        );
        await processSSEStream(response, onComplete);
      } catch (err) {
        setState((prev) => ({
          ...prev,
          isStreaming: false,
          error: err instanceof Error ? err.message : 'Mesaj gönderilemedi',
        }));
      }
    },
    [snapshotId, processSSEStream]
  );

  const abort = useCallback(() => {
    abortRef.current?.abort();
    setState((prev) => ({ ...prev, isStreaming: false }));
  }, []);

  return {
    ...state,
    sendInit,
    sendMessage,
    abort,
  };
}
