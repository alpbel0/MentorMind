'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

interface UsePollingOptions<T> {
  fetcher: () => Promise<T>;
  interval?: number;
  timeout?: number; // Timeout in milliseconds (default: no timeout)
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
  timeout,
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
  const startTimeRef = useRef<number | null>(null);
  
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
      // Network errors (Failed to fetch) — don't stop polling, just log
      const isNetworkError = error.message === 'Failed to fetch' ||
        error.message.includes('NetworkError') ||
        error.message.includes('network');
      
      if (!isNetworkError) {
        setError(error);
      }
      
      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
      // Don't re-throw — prevents unhandled promise rejection
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

    // Record start time for timeout tracking
    startTimeRef.current = Date.now();

    // Initial fetch
    fetchData().catch(() => {});

    // Set up polling with fixed interval
    const pollInterval = setInterval(() => {
      if (isPolling) {
        // Check timeout
        if (timeout && startTimeRef.current) {
          const elapsed = Date.now() - startTimeRef.current;
          if (elapsed >= timeout) {
            setIsPolling(false);
            const timeoutError = new Error(
              `Polling timed out after ${Math.floor(timeout / 1000)} seconds. Please check the evaluation status manually or contact support if the issue persists.`
            );
            setError(timeoutError);
            if (onErrorRef.current) {
              onErrorRef.current(timeoutError);
            }
            return;
          }
        }
        fetchData().catch(() => {});
      }
    }, interval);

    return () => {
      clearInterval(pollInterval);
    };
  }, [enabled, interval, timeout]); // Remove fetchData and isPolling from deps

  return {
    data,
    error,
    isLoading,
    isPolling,
    refetch,
    stop,
  };
}
