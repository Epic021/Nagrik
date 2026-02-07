import {
  FileText,
  Clock,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  Users,
} from 'lucide-react';
import { StatCard } from '@/components/StatCard';
import { StatusBadge } from '@/components/StatusBadge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/contexts/AuthContext';
import { MOCK_DASHBOARD_DATA, MOCK_TRENDS_DATA, MOCK_COMPLAINTS } from '@/data/mockData';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from 'recharts';
import { ComplaintStatus } from '@/types';
import { format } from 'date-fns';

const STATUS_COLORS: Record<ComplaintStatus, string> = {
  pending: 'hsl(45, 93%, 47%)',
  assigned: 'hsl(217, 91%, 50%)',
  in_progress: 'hsl(25, 95%, 53%)',
  resolved: 'hsl(142, 71%, 45%)',
  rejected: 'hsl(0, 0%, 60%)',
  citizen_rejected: 'hsl(0, 84%, 60%)',
};

export default function DashboardPage() {
  const { user, isSuperAdmin } = useAuth();
  const data = MOCK_DASHBOARD_DATA;
  const trends = MOCK_TRENDS_DATA;

  const pieData = [
    { name: 'Pending', value: data.by_status.pending, status: 'pending' as ComplaintStatus },
    { name: 'Assigned', value: data.by_status.assigned, status: 'assigned' as ComplaintStatus },
    { name: 'In Progress', value: data.by_status.in_progress, status: 'in_progress' as ComplaintStatus },
    { name: 'Resolved', value: data.by_status.resolved, status: 'resolved' as ComplaintStatus },
    { name: 'Rejected', value: data.by_status.rejected, status: 'rejected' as ComplaintStatus },
  ];

  const trendChartData = trends.new_complaints.map((item, index) => ({
    date: format(new Date(item.date), 'MMM d'),
    new: item.count,
    resolved: trends.resolutions[index]?.count || 0,
  }));

  const recentComplaints = MOCK_COMPLAINTS.slice(0, 5);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          {isSuperAdmin
            ? 'Overview of all departments'
            : `${user?.department_id?.toUpperCase() || 'Department'} Overview`}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Complaints"
          value={data.summary.total_complaints}
          icon={<FileText className="h-6 w-6 text-primary" />}
          description="All time"
        />
        <StatCard
          title="New Today"
          value={data.summary.today_new}
          icon={<Clock className="h-6 w-6 text-primary" />}
          trend={{ value: 12, isPositive: false }}
          description="vs yesterday"
        />
        <StatCard
          title="High Urgency Pending"
          value={data.summary.high_urgency_pending}
          icon={<AlertTriangle className="h-6 w-6 text-urgency-high" />}
          iconClassName="bg-urgency-high/10"
          description="Needs attention"
        />
        <StatCard
          title="Resolution Rate"
          value={`${data.performance.resolution_rate}%`}
          icon={<CheckCircle2 className="h-6 w-6 text-status-resolved" />}
          iconClassName="bg-status-resolved/10"
          trend={{ value: 5.2, isPositive: true }}
          description="This week"
        />
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Trends Chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Complaint Trends
            </CardTitle>
            <CardDescription>New complaints vs resolutions over time</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trendChartData}>
                  <defs>
                    <linearGradient id="colorNew" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(217, 91%, 50%)" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="hsl(217, 91%, 50%)" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorResolved" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(142, 71%, 45%)" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="hsl(142, 71%, 45%)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="date" className="text-xs" />
                  <YAxis className="text-xs" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="new"
                    stroke="hsl(217, 91%, 50%)"
                    fillOpacity={1}
                    fill="url(#colorNew)"
                    name="New Complaints"
                  />
                  <Area
                    type="monotone"
                    dataKey="resolved"
                    stroke="hsl(142, 71%, 45%)"
                    fillOpacity={1}
                    fill="url(#colorResolved)"
                    name="Resolved"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Status Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Status Distribution</CardTitle>
            <CardDescription>Current complaint breakdown</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {pieData.map((entry) => (
                      <Cell key={entry.name} fill={STATUS_COLORS[entry.status]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-2 gap-2 mt-4">
              {pieData.map((item) => (
                <div key={item.name} className="flex items-center gap-2 text-sm">
                  <div
                    className="h-3 w-3 rounded-full"
                    style={{ backgroundColor: STATUS_COLORS[item.status] }}
                  />
                  <span className="text-muted-foreground">{item.name}</span>
                  <span className="font-medium ml-auto">{item.value}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Top Categories */}
        <Card>
          <CardHeader>
            <CardTitle>Top Issue Categories</CardTitle>
            <CardDescription>Most reported complaint types</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.top_categories} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" horizontal={false} />
                  <XAxis type="number" className="text-xs" />
                  <YAxis type="category" dataKey="category" className="text-xs" width={100} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="count" fill="hsl(217, 91%, 50%)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Recent Complaints */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Recent Complaints
            </CardTitle>
            <CardDescription>Latest submitted complaints</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentComplaints.map((complaint) => (
                <div
                  key={complaint.id}
                  className="flex items-start gap-4 p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{complaint.title}</p>
                    <p className="text-sm text-muted-foreground truncate">
                      {complaint.location.address}
                    </p>
                  </div>
                  <StatusBadge status={complaint.status} />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Metrics */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Satisfaction Rate</p>
              <p className="text-2xl font-bold">{data.performance.satisfaction_rate}%</p>
            </div>
            <div className="h-12 w-12 rounded-full bg-status-resolved/20 flex items-center justify-center">
              <span className="text-2xl">😊</span>
            </div>
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Avg Resolution Time</p>
              <p className="text-2xl font-bold">{data.performance.avg_resolution_hours}h</p>
            </div>
            <div className="h-12 w-12 rounded-full bg-primary/20 flex items-center justify-center">
              <Clock className="h-6 w-6 text-primary" />
            </div>
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Weekly Resolved</p>
              <p className="text-2xl font-bold">{data.summary.week_resolved}</p>
            </div>
            <div className="h-12 w-12 rounded-full bg-accent/20 flex items-center justify-center">
              <CheckCircle2 className="h-6 w-6 text-accent" />
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
