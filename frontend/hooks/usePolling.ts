'use client';

import { useState, useEffect, useCallback } from 'react';

interface UsePollingOptions<T> {
  fetcher: () => Promise<T>;
  interval?: number;
  shouldStop?: (data: T) => boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
  enabled?: boolean;
}

interface UsePollingResult<T> {
  data: T | null;
  error: Error | null;
  isLoading: boolean;
  isPolling: boolean;
  refetch: () => Promise<void>;
  stop: () => void;
}

export function usePolling<T>({
  fetcher,
  interval = 2000,
  shouldStop,
  onSuccess,
  onError,
  enabled = true,
}: UsePollingOptions<T>): UsePollingResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isPolling, setIsPolling] = useState(enabled);

  const stop = useCallback(() => {
    setIsPolling(false);
  }, []);

  const fetchData = useCallback(async () => {
    try {
      const result = await fetcher();
      setData(result);
      setError(null);
      
      if (onSuccess) {
        onSuccess(result);
      }
      
      if (shouldStop && shouldStop(result)) {
        setIsPolling(false);
      }
      
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      if (onError) {
        onError(error);
      }
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [fetcher, shouldStop, onSuccess, onError]);

  const refetch = useCallback(async () => {
    setIsLoading(true);
    await fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!enabled) {
      setIsPolling(false);
      return;
    }

    // Initial fetch
    fetchData();

    // Set up polling
    const pollInterval = setInterval(() => {
      if (isPolling) {
        fetchData();
      }
    }, interval);

    return () => {
      clearInterval(pollInterval);
    };
  }, [enabled, interval, isPolling, fetchData]);

  return {
    data,
    error,
    isLoading,
    isPolling,
    refetch,
    stop,
  };
}
