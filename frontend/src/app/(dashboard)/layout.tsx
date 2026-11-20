import React from 'react';
import Link from 'next/link';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const navigationItems = [
    { name: 'Overview', href: '/', icon: '📊' },
    { name: 'Historical Trends', href: '/trends', icon: '📈' },
    { name: 'Goals & Limits', href: '/goals', icon: '🎯' },
    { name: 'AI Insights', href: '/insights', icon: '🧠' },
    { name: 'Devices & Settings', href: '/settings', icon: '⚙️' },
  ];

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-50 font-sans">
      {/* Sidebar Navigation */}
      <aside className="w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col justify-between">
        <div>
          <div className="p-6 border-b border-slate-200 dark:border-slate-800">
            <h1 className="text-xl font-bold tracking-tight text-indigo-600 dark:text-indigo-400">
              Digital Wellbeing
            </h1>
            <p className="text-xs text-slate-500 mt-1">Personal Telemetry & Habits</p>
          </div>
          <nav className="p-4 space-y-1">
            {navigationItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <span>{item.icon}</span>
                <span>{item.name}</span>
              </Link>
            ))}
          </nav>
        </div>

        {/* User / Status Bar */}
        <div className="p-4 border-t border-slate-200 dark:border-slate-800">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-emerald-500"></span>
              Connected
            </span>
            <span>v1.0.0</span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto">
        <header className="h-16 border-b border-slate-200 dark:border-slate-800 px-8 flex items-center justify-between bg-white dark:bg-slate-900">
          <div className="text-sm font-medium text-slate-500">Personal Wellbeing Analytics</div>
          <div className="flex items-center gap-4">
            <span className="text-xs px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 font-medium">
              Zero-Redis Monolith
            </span>
          </div>
        </header>
        <div className="p-8 max-w-7xl mx-auto">{children}</div>
      </main>
    </div>
  );
}
