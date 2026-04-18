export type Status = 'Applied' | 'Interviewing' | 'Offer Received' | 'Rejected' | 'No Response';

export interface Application {
  id: number;
  company: string;
  role: string;
  status: Status;
  applied_date: string | null;
  last_updated: string;
  notes: string | null;
  is_manual: boolean;
}

export const STATUSES: Status[] = ['Applied', 'Interviewing', 'Offer Received', 'Rejected', 'No Response'];
