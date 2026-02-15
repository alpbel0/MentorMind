'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Lock } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
  isStreaming: boolean;
  remainingTurns: number;
  maxTurns: number;
}

export function ChatInput({
  onSend,
  disabled,
  isStreaming,
  remainingTurns,
  maxTurns,
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const isLimitReached = remainingTurns <= 0;
  const isDisabled = disabled || isStreaming || isLimitReached;

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
  }, [message]);

  const handleSend = () => {
    const trimmed = message.trim();
    if (!trimmed || isDisabled) return;
    if (trimmed.length > 500) return;
    onSend(trimmed);
    setMessage('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (isLimitReached) {
    return (
      <div className="border-t border-slate-200 p-4">
        <div className="flex items-center gap-3 p-4 bg-amber-50 border border-amber-200 rounded-xl">
          <Lock className="w-5 h-5 text-amber-500 shrink-0" />
          <div>
            <p className="text-sm font-medium text-amber-800">
              Bu değerlendirme üzerine yeterince konuştuk!
            </p>
            <p className="text-xs text-amber-600 mt-0.5">
              Öğrendiklerini pekiştirmek için yeni bir soru çözmeye ne dersin?
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="border-t border-slate-200 p-4">
      {/* Turn Counter */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-slate-400">
          Kalan mesaj: {remainingTurns}/{maxTurns}
        </span>
        {message.length > 400 && (
          <span className={`text-xs ${message.length > 500 ? 'text-rose-500' : 'text-amber-500'}`}>
            {message.length}/500
          </span>
        )}
      </div>

      {/* Input */}
      <div className="flex items-end gap-2">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isDisabled}
          placeholder={isStreaming ? 'Coach yanıt veriyor...' : 'Mesajını yaz...'}
          className="flex-1 resize-none rounded-xl border border-slate-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:opacity-50 disabled:bg-slate-50 min-h-[44px] max-h-[120px]"
          rows={1}
        />
        <button
          onClick={handleSend}
          disabled={isDisabled || !message.trim() || message.length > 500}
          className="p-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shrink-0"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
