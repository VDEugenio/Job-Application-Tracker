import { useState } from 'react';
import type { Application, Status } from '../types';
import { STATUSES } from '../types';
import { StatusBadge } from './StatusBadge';

type SortKey = 'company' | 'role' | 'status' | 'applied_date' | 'last_updated';

interface Props {
  applications: Application[];
  onEdit: (app: Application) => void;
  onDelete: (id: number) => void;
}

export function ApplicationTable({ applications, onEdit, onDelete }: Props) {
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState<Status | 'All'>('All');
  const [sortKey, setSortKey] = useState<SortKey>('last_updated');
  const [sortAsc, setSortAsc] = useState(false);

  function handleSort(key: SortKey) {
    if (sortKey === key) setSortAsc(a => !a);
    else { setSortKey(key); setSortAsc(true); }
  }

  const filtered = applications
    .filter(a => filterStatus === 'All' || a.status === filterStatus)
    .filter(a => {
      const q = search.toLowerCase();
      return a.company.toLowerCase().includes(q) || a.role.toLowerCase().includes(q);
    })
    .sort((a, b) => {
      const av = a[sortKey] ?? '';
      const bv = b[sortKey] ?? '';
      const cmp = String(av).localeCompare(String(bv));
      return sortAsc ? cmp : -cmp;
    });

  function SortIcon({ col }: { col: SortKey }) {
    if (sortKey !== col) return <span className="text-gray-300 ml-1">↕</span>;
    return <span className="ml-1">{sortAsc ? '↑' : '↓'}</span>;
  }

  function th(label: string, key: SortKey) {
    return (
      <th
        className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider cursor-pointer select-none hover:text-gray-800 transition-colors"
        onClick={() => handleSort(key)}
      >
        {label}<SortIcon col={key} />
      </th>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Search company or role…"
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={filterStatus}
          onChange={e => setFilterStatus(e.target.value as Status | 'All')}
        >
          <option value="All">All statuses</option>
          {STATUSES.map(s => <option key={s}>{s}</option>)}
        </select>
        <span className="self-center text-sm text-gray-500">{filtered.length} result{filtered.length !== 1 ? 's' : ''}</span>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {th('Company', 'company')}
              {th('Role', 'role')}
              {th('Status', 'status')}
              {th('Applied', 'applied_date')}
              {th('Last Updated', 'last_updated')}
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filtered.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-10 text-center text-sm text-gray-400">
                  No applications found.
                </td>
              </tr>
            )}
            {filtered.map(app => (
              <tr key={app.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3 text-sm font-medium text-gray-900">{app.company}</td>
                <td className="px-4 py-3 text-sm text-gray-700">{app.role}</td>
                <td className="px-4 py-3"><StatusBadge status={app.status} /></td>
                <td className="px-4 py-3 text-sm text-gray-500">{app.applied_date ?? '—'}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{new Date(app.last_updated).toLocaleDateString()}</td>
                <td className="px-4 py-3 text-right space-x-2">
                  <button
                    onClick={() => onEdit(app)}
                    className="text-xs font-medium text-blue-600 hover:text-blue-800 transition-colors"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => { if (confirm(`Delete ${app.company} — ${app.role}?`)) onDelete(app.id); }}
                    className="text-xs font-medium text-red-500 hover:text-red-700 transition-colors"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
