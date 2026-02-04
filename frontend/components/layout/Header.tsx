'use client';

import { usePathname } from 'next/navigation';
import { Bell, Search } from 'lucide-react';

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  '/': {
    title: 'Dashboard',
    subtitle: 'Overview of your evaluation performance',
  },
  '/evaluate': {
    title: 'New Evaluation',
    subtitle: 'Start a new AI response evaluation session',
  },
  '/history': {
    title: 'Evaluation History',
    subtitle: 'View your past evaluations and feedback',
  },
  '/feedback': {
    title: 'Judge Feedback',
    subtitle: 'Detailed analysis of your evaluation',
  },
};

export function Header() {
  const pathname = usePathname();
  
  // Handle dynamic routes
  const basePath = pathname.startsWith('/feedback/') ? '/feedback' : pathname;
  const pageInfo = pageTitles[basePath] || { title: 'MentorMind', subtitle: '' };

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">{pageInfo.title}</h1>
        <p className="text-sm text-slate-500">{pageInfo.subtitle}</p>
      </div>

      <div className="flex items-center space-x-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search evaluations..."
            className="w-64 pl-10 pr-4 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
          />
        </div>

        {/* Notifications */}
        <button className="relative p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-indigo-600 rounded-full" />
        </button>

        {/* User Avatar */}
        <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
          <span className="text-sm font-medium text-indigo-600">U</span>
        </div>
      </div>
    </header>
  );
}
