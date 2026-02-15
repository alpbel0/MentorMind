'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  PenSquare,
  History,
  BarChart3,
  Settings,
  Brain,
  BookOpen,
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'New Evaluation', href: '/evaluate', icon: PenSquare },
  { name: 'Snapshots', href: '/snapshots', icon: BookOpen },
  { name: 'History', href: '/history', icon: History },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 w-64 bg-white border-r border-slate-200 flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-slate-200">
        <Brain className="w-8 h-8 text-indigo-600" />
        <span className="ml-3 text-xl font-bold text-slate-900">MentorMind</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href || 
            (item.href !== '/' && pathname.startsWith(item.href));
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-200 ${
                isActive
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }`}
            >
              <Icon className={`w-5 h-5 mr-3 ${isActive ? 'text-indigo-600' : 'text-slate-400'}`} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-200">
        <div className="flex items-center px-3 py-2 rounded-lg bg-slate-50">
          <BarChart3 className="w-5 h-5 text-slate-400" />
          <div className="ml-3">
            <p className="text-xs font-medium text-slate-600">EvalOps Training</p>
            <p className="text-xs text-slate-400">v1.0.0-MVP</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
