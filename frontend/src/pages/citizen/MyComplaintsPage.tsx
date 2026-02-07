import { useState } from 'react';
import { Link } from 'react-router-dom';
import { FileText, ChevronRight, MapPin, Clock, Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { StatusBadge } from '@/components/StatusBadge';
import { useMyComplaints } from '@/hooks/use-complaints';

export default function MyComplaintsPage() {
  const [activeTab, setActiveTab] = useState<'all' | 'active' | 'resolved'>('all');
  const { data: myComplaints = [], isLoading } = useMyComplaints();

  const complaintsArray = Array.isArray(myComplaints) ? myComplaints : [];

  const filteredComplaints = complaintsArray.filter((complaint) => {
    if (activeTab === 'all') return true;
    if (activeTab === 'active') {
      return ['pending', 'assigned', 'in_progress'].includes(complaint.status);
    }
    return ['resolved', 'rejected', 'citizen_rejected'].includes(complaint.status);
  });

  const statusCounts = {
    all: complaintsArray.length,
    active: complaintsArray.filter((c) => ['pending', 'assigned', 'in_progress'].includes(c.status)).length,
    resolved: complaintsArray.filter((c) => ['resolved', 'rejected', 'citizen_rejected'].includes(c.status)).length,
  };

  return (
    <div className="min-h-full bg-background">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-background border-b border-border">
        <div className="px-4 py-4">
          <h1 className="text-xl font-bold text-foreground">My Complaints</h1>
          <p className="text-sm text-muted-foreground">Track your submitted issues</p>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)}>
          <TabsList className="w-full justify-start px-4 h-auto pb-0 bg-transparent gap-4">
            <TabsTrigger
              value="all"
              className="data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none pb-3"
            >
              All ({statusCounts.all})
            </TabsTrigger>
            <TabsTrigger
              value="active"
              className="data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none pb-3"
            >
              Active ({statusCounts.active})
            </TabsTrigger>
            <TabsTrigger
              value="resolved"
              className="data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none pb-3"
            >
              Resolved ({statusCounts.resolved})
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
            <p className="text-sm text-muted-foreground">Loading your complaints...</p>
          </div>
        ) : Array.isArray(filteredComplaints) && filteredComplaints.length > 0 ? (
          filteredComplaints.map((complaint) => (
            <Link key={complaint.id} to={`/citizen/complaints/${complaint.id}`}>
              <Card className="overflow-hidden hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <h3 className="font-medium text-sm line-clamp-2 text-foreground flex-1">
                      {complaint.title}
                    </h3>
                    <ChevronRight className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                  </div>

                  <div className="flex items-center gap-2 mb-3">
                    <StatusBadge status={complaint.status} size="sm" />
                    <Badge variant="secondary" className="text-xs">
                      {complaint.category?.icon} {complaint.category?.name}
                    </Badge>
                  </div>

                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <MapPin className="h-3 w-3" />
                      {complaint.location.address.split(',')[0]}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {new Date(complaint.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  {/* Progress indicator for active complaints */}
                  {['assigned', 'in_progress'].includes(complaint.status) && (
                    <div className="mt-3 pt-3 border-t border-border">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary transition-all"
                            style={{
                              width: complaint.status === 'assigned' ? '33%' : '66%',
                            }}
                          />
                        </div>
                        <span className="text-xs text-muted-foreground">
                          {complaint.status === 'assigned' ? 'Assigned' : 'In Progress'}
                        </span>
                      </div>
                      {complaint.assigned_to_name && (
                        <p className="text-xs text-muted-foreground mt-2">
                          Assigned to: {complaint.assigned_to_name}
                        </p>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </Link>
          ))
        ) : (
          <div className="text-center py-16">
            <FileText className="h-16 w-16 mx-auto mb-4 text-muted-foreground/50" />
            <h3 className="font-medium text-foreground mb-1">No complaints found</h3>
            <p className="text-sm text-muted-foreground">
              {activeTab === 'active'
                ? 'No active complaints at the moment'
                : activeTab === 'resolved'
                  ? 'No resolved complaints yet'
                  : 'You haven\'t submitted any complaints yet'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
