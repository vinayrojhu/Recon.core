'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '../../../components/layout/AppShell';
import { PermissionGate } from '../../../components/ui/PermissionGate';
import api from '../../../lib/api';
import { User } from '../../../types/auth';
import { ApiResponse } from '../../../types/api';

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<ApiResponse<User[]>>('/users')
      .then((res) => {
        if (res.data.data) setUsers(res.data.data);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Identity & Access Management</h1>
          <p className="text-sm text-slate-400 mt-1">Platform Core RBAC Users</p>
        </div>
        <PermissionGate permission="users:create">
          <button className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-md text-sm font-medium transition">
            Create User
          </button>
        </PermissionGate>
      </div>

      <div className="border border-slate-800 rounded-lg overflow-hidden bg-slate-900/40">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-900/80 text-xs font-semibold text-slate-400 uppercase tracking-wider">
              <th className="px-6 py-3">User</th>
              <th className="px-6 py-3">Roles</th>
              <th className="px-6 py-3">Status</th>
              <th className="px-6 py-3">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 text-sm text-slate-300">
            {loading ? (
              <tr><td colSpan={4} className="px-6 py-8 text-center text-slate-500">Loading user registry...</td></tr>
            ) : users.length === 0 ? (
              <tr><td colSpan={4} className="px-6 py-8 text-center text-slate-500">No users found.</td></tr>
            ) : (
              users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-800/30 transition">
                  <td className="px-6 py-4">
                    <p className="font-medium text-slate-200">{u.full_name || 'N/A'}</p>
                    <p className="text-xs text-slate-500">{u.email}</p>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-1.5 flex-wrap">
                      {u.roles.map((r) => (
                        <span key={r.id} className="text-xs px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
                          {r.name}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${u.is_active ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-red-950 text-red-400 border border-red-800'}`}>
                      {u.is_active ? 'Active' : 'Disabled'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-xs text-slate-500">
                    {new Date(u.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}
