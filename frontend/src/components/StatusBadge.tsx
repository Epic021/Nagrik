import { ComplaintStatus, UrgencyLevel } from '@/types';
import { cn } from '@/lib/utils';

const STATUS_CONFIG: Record<ComplaintStatus, { label: string; className: string }> = {
  pending: { label: 'Pending', className: 'status-pending' },
  assigned: { label: 'Assigned', className: 'status-assigned' },
  in_progress: { label: 'In Progress', className: 'status-in-progress' },
  resolved: { label: 'Resolved', className: 'status-resolved' },
  citizen_rejected: { label: 'Citizen Rejected', className: 'status-rejected' },
  rejected: { label: 'Rejected', className: 'bg-muted text-muted-foreground' },
};

const URGENCY_CONFIG: Record<UrgencyLevel, { label: string; className: string }> = {
  low: { label: 'Low', className: 'bg-urgency-low/10 text-urgency-low' },
  normal: { label: 'Normal', className: 'bg-urgency-normal/10 text-urgency-normal' },
  high: { label: 'High', className: 'bg-urgency-high/10 text-urgency-high' },
  urgent: { label: 'Urgent', className: 'bg-urgency-urgent/10 text-urgency-urgent' },
};

interface StatusBadgeProps {
  status: ComplaintStatus;
  className?: string;
  size?: 'sm' | 'default';
}

export function StatusBadge({ status, className, size = 'default' }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status];
  const sizeClasses = size === 'sm' ? 'text-[10px] px-1.5 py-0.5' : '';
  return (
    <span className={cn('status-badge', config.className, sizeClasses, className)}>
      {config.label}
    </span>
  );
}

interface UrgencyBadgeProps {
  urgency: UrgencyLevel;
  className?: string;
}

export function UrgencyBadge({ urgency, className }: UrgencyBadgeProps) {
  const config = URGENCY_CONFIG[urgency];
  return (
    <span className={cn('status-badge', config.className, className)}>
      {config.label}
    </span>
  );
}
