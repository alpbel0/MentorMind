'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

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
  interval = 3000,
  shouldStop,
  onSuccess,
  onError,
  enabled = true,
}: UsePollingOptions<T>): UsePollingResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isPolling, setIsPolling] = useState(enabled);
  
  // Use refs to avoid stale closures in interval
  const fetcherRef = useRef(fetcher);
  const shouldStopRef = useRef(shouldStop);
  const onSuccessRef = useRef(onSuccess);
  const onErrorRef = useRef(onError);
  
  // Update refs when callbacks change
  useEffect(() => {
    fetcherRef.current = fetcher;
    shouldStopRef.current = shouldStop;
    onSuccessRef.current = onSuccess;
    onErrorRef.current = onError;
  }, [fetcher, shouldStop, onSuccess, onError]);

  const stop = useCallback(() => {
    setIsPolling(false);
  }, []);

  const fetchData = useCallback(async () => {
    try {
      const result = await fetcherRef.current();
      setData(result);
      setError(null);
      
      if (onSuccessRef.current) {
        onSuccessRef.current(result);
      }
      
      if (shouldStopRef.current && shouldStopRef.current(result)) {
        setIsPolling(false);
      }
      
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

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

    // Set up polling with fixed interval
    const pollInterval = setInterval(() => {
      if (isPolling) {
        fetchData();
      }
    }, interval);

    return () => {
      clearInterval(pollInterval);
    };
  }, [enabled, interval]); // Remove fetchData and isPolling from deps

  return {
    data,
    error,
    isLoading,
    isPolling,
    refetch,
    stop,
  };
}
