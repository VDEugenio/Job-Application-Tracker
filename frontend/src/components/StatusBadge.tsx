import type { Status } from '../types';

const colors: Record<Status, string> = {
  'Applied': 'bg-blue-100 text-blue-800',
  'Interviewing': 'bg-yellow-100 text-yellow-800',
  'Offer Received': 'bg-green-100 text-green-800',
  'Rejected': 'bg-red-100 text-red-800',
  'No Response': 'bg-gray-100 text-gray-600',
};

export function StatusBadge({ status }: { status: Status }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[status] ?? 'bg-gray-100 text-gray-600'}`}>
      {status}
    </span>
  );
}
