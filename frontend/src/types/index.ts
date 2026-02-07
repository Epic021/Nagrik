export type UserRole = 'citizen' | 'department_admin' | 'super_admin';

export type ComplaintStatus = 'pending' | 'assigned' | 'in_progress' | 'resolved' | 'citizen_rejected' | 'rejected';

export type UrgencyLevel = 'low' | 'normal' | 'high' | 'urgent';

export interface User {
  id: string;
  name: string;
  phone: string;
  role: UserRole;
  department_id?: string;
}

export interface Department {
  id: string;
  name: string;
  short_name: string;
}

export interface Category {
  id: string;
  name: string;
  icon: string;
}

export interface Location {
  lat: number;
  lng: number;
  address: string;
}

export interface Complaint {
  id: string;
  title: string;
  description: string;
  category_id: string;
  category?: Category;
  department_id: string;
  department?: Department;
  status: ComplaintStatus;
  urgency: UrgencyLevel;
  location: Location;
  media_urls: string[];
  upvotes: number;
  created_at: string;
  updated_at: string;
  created_by: User;
  assigned_to_name?: string;
  assigned_to_phone?: string;
  resolved_at?: string;
  resolution_notes?: string;
}

export interface ComplaintHistory {
  action: string;
  by: User;
  notes?: string;
  created_at: string;
}

export interface DashboardSummary {
  total_complaints: number;
  today_new: number;
  week_new: number;
  week_resolved: number;
  high_urgency_pending: number;
}

export interface DashboardByStatus {
  pending: number;
  assigned: number;
  in_progress: number;
  resolved: number;
  rejected: number;
  citizen_rejected: number;
}

export interface DashboardPerformance {
  resolution_rate: number;
  satisfaction_rate: number;
  avg_resolution_hours: number;
}

export interface TopCategory {
  category: string;
  count: number;
}

export interface DashboardData {
  department_id?: string;
  summary: DashboardSummary;
  by_status: DashboardByStatus;
  performance: DashboardPerformance;
  top_categories: TopCategory[];
}

export interface TrendDataPoint {
  date: string;
  count: number;
}

export interface TrendsData {
  period_days: number;
  new_complaints: TrendDataPoint[];
  resolutions: TrendDataPoint[];
}
