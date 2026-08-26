'use client';

import React, { ReactNode } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '../../context/AuthContext';
import { Users, Shield, Layers, LogOut } from 'lucide-react';

export const AppShell = ({ children }: { children: ReactNode }) => {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  const navigation = [
    { name: 'Core Overview', href: '/dashboard', icon: Layers },
    { name: 'User Management', href: '/dashboard/users', icon: Users, permission: 'users:read' },
  ];

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 antialiased overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 bg-slate-900 flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-2 h-16 px-6 border-b border-slate-800">
            <Shield className="w-6 h-6 text-blue-500" />
            <span className="font-bold tracking-wide text-md">Platform Core</span>
          </div>
          <nav className="p-4 space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition ${
                    isActive
                      ? 'bg-blue-600/10 text-blue-400 border border-blue-600/20'
                      : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* User Info & Signout */}
        <div className="p-4 border-t border-slate-800 flex items-center justify-between">
          <div className="overflow-hidden pr-2">
            <p className="text-xs font-semibold truncate text-slate-200">{user?.full_name || 'Admin User'}</p>
            <p className="text-xs text-slate-500 truncate">{user?.email}</p>
          </div>
          <button
            onClick={logout}
            aria-label="Logout"
            className="p-1.5 hover:bg-red-500/10 text-slate-400 hover:text-red-400 rounded-md transition"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-y-auto">
        <header className="h-16 border-b border-slate-800 px-8 flex items-center justify-between bg-slate-900/50 backdrop-blur">
          <div className="text-sm font-medium text-slate-400">Environment: <span className="text-emerald-400">Production</span></div>
          <div className="text-xs px-2.5 py-1 rounded-full border border-blue-500/30 bg-blue-500/10 text-blue-400">Core Engine 1.0</div>
        </header>
        <div className="p-8 max-w-7xl w-full mx-auto">{children}</div>
      </main>
    </div>
  );
};
