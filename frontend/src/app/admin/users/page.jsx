'use client';
/**
 * File: frontend/src/app/admin/users/page.jsx
 * User management — list, create, edit role/status, delete.
 */
import { useState } from 'react';
import { Users, Plus, Trash2, Edit2, X } from 'lucide-react';
import { useAdminUsers } from '@/hooks/useAdmin';
import BackendPendingNotice from '@/components/admin/BackendPendingNotice';

const ROLES = ['user', 'admin'];

function UserModal({ user, onClose, onSave }) {
  const [form, setForm] = useState(user || { username: '', email: '', password: '', role: 'user', is_active: true });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try { await onSave(form); onClose(); } finally { setSaving(false); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="rounded-2xl border p-6 w-full max-w-md" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-bold" style={{ color: 'var(--text-primary)' }}>{user ? 'Edit User' : 'New User'}</h2>
          <button onClick={onClose}><X size={18} style={{ color: 'var(--text-muted)' }} /></button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="text-xs font-semibold mb-1 block" style={{ color: 'var(--text-muted)' }}>Username</label>
            <input value={form.username} onChange={e => setForm(p => ({ ...p, username: e.target.value }))}
              disabled={!!user}
              className="w-full rounded-lg border px-3 py-2 text-sm outline-none disabled:opacity-50"
              style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }} />
          </div>
          <div>
            <label className="text-xs font-semibold mb-1 block" style={{ color: 'var(--text-muted)' }}>Email</label>
            <input type="email" value={form.email} onChange={e => setForm(p => ({ ...p, email: e.target.value }))}
              className="w-full rounded-lg border px-3 py-2 text-sm outline-none"
              style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }} />
          </div>
          {!user && (
            <div>
              <label className="text-xs font-semibold mb-1 block" style={{ color: 'var(--text-muted)' }}>Password</label>
              <input type="password" value={form.password} onChange={e => setForm(p => ({ ...p, password: e.target.value }))}
                className="w-full rounded-lg border px-3 py-2 text-sm outline-none"
                style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }} />
            </div>
          )}
          <div>
            <label className="text-xs font-semibold mb-1 block" style={{ color: 'var(--text-muted)' }}>Role</label>
            <select value={form.role} onChange={e => setForm(p => ({ ...p, role: e.target.value }))}
              className="w-full rounded-lg border px-3 py-2 text-sm outline-none"
              style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
              {ROLES.map(r => <option key={r} value={r}>{r.replace('_', ' ')}</option>)}
            </select>
          </div>
          <label className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
            <input type="checkbox" checked={form.is_active} onChange={e => setForm(p => ({ ...p, is_active: e.target.checked }))} />
            Active
          </label>
          <div className="flex gap-2 pt-2">
            <button type="button" onClick={onClose} className="flex-1 py-2 rounded-xl text-sm border"
              style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}>Cancel</button>
            <button type="submit" disabled={saving} className="flex-1 py-2 rounded-xl text-sm font-semibold text-white disabled:opacity-50"
              style={{ background: '#B5451B' }}>{saving ? 'Saving…' : 'Save'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}

const ROLE_BADGE = {
  admin: 'text-orange-400 bg-orange-400/10 border-orange-400/30',
  user: 'text-gray-400 bg-gray-400/10 border-gray-400/30',
};

export default function UserManagementPage() {
  const { users, loading, error, createUser, updateUser, deleteUser } = useAdminUsers();
  const [modalUser, setModalUser] = useState(undefined);

  const isPending = error && error.includes('NOT_IMPLEMENTED');

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(198,40,40,0.1)' }}>
            <Users size={20} color="#B5451B" />
          </div>
          <div>
            <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>User Management</h1>
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{users.length} users</p>
          </div>
        </div>
        <button onClick={() => setModalUser(null)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-white"
          style={{ background: '#B5451B' }}>
          <Plus size={14} />New User
        </button>
      </div>

      {loading ? (
        <div className="space-y-2">{[...Array(4)].map((_, i) => (
          <div key={i} className="rounded-xl border animate-pulse h-14" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }} />
        ))}</div>
      ) : isPending || users.length === 0 && error ? (
        <BackendPendingNotice module="User management" />
      ) : (
        <div className="rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border)' }}>
          <table className="w-full text-sm">
            <thead style={{ background: 'var(--bg-secondary)' }}>
              <tr className="text-xs" style={{ color: 'var(--text-muted)', borderBottom: '1px solid var(--border)' }}>
                {['Username', 'Email', 'Role', 'Status', ''].map(h => (
                  <th key={h} className="px-4 py-2.5 text-left font-semibold">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody style={{ background: 'var(--bg-card)' }}>
              {users.map(u => (
                <tr key={u.id} className="border-b last:border-0" style={{ borderColor: 'var(--border)' }}>
                  <td className="px-4 py-3 font-medium" style={{ color: 'var(--text-primary)' }}>{u.username}</td>
                  <td className="px-4 py-3" style={{ color: 'var(--text-secondary)' }}>{u.email}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full border font-semibold ${ROLE_BADGE[u.role] || ROLE_BADGE.user}`}>
                      {u.role?.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={u.is_active ? 'text-green-400 text-xs font-semibold' : 'text-gray-500 text-xs'}>
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-3 flex gap-1 justify-end">
                    <button onClick={() => setModalUser(u)} className="p-1.5 rounded hover:bg-white/10">
                      <Edit2 size={13} style={{ color: 'var(--text-muted)' }} />
                    </button>
                    <button onClick={() => deleteUser(u.id)} className="p-1.5 rounded hover:bg-red-500/20">
                      <Trash2 size={13} className="text-red-400" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {modalUser !== undefined && (
        <UserModal
          user={modalUser}
          onClose={() => setModalUser(undefined)}
          onSave={async (data) => modalUser ? updateUser(modalUser.id, data) : createUser(data)}
        />
      )}
    </div>
  );
}
