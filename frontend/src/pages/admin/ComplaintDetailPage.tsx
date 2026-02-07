import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  MapPin,
  Calendar,
  User,
  Phone,
  ThumbsUp,
  Clock,
  UserPlus,
  CheckCircle,
  XCircle,
  ArrowUpRight,
  MessageSquare,
  Image as ImageIcon,
  Loader2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { StatusBadge, UrgencyBadge } from '@/components/StatusBadge';
import { useComplaintDetail } from '@/hooks/use-complaints';
import { useAssignComplaint, useResolveComplaint, useUpdateComplaintStatus } from '@/hooks/use-admin';
import { format } from 'date-fns';
import { useState } from 'react';
import { toast } from 'sonner';

export default function ComplaintDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [assignDialogOpen, setAssignDialogOpen] = useState(false);
  const [resolveDialogOpen, setResolveDialogOpen] = useState(false);

  // Form states
  const [staffName, setStaffName] = useState('');
  const [staffPhone, setStaffPhone] = useState('');
  const [priority, setPriority] = useState('normal');
  const [resNotes, setResNotes] = useState('');
  const [resBy, setResBy] = useState('');

  const { data: complaint, isLoading } = useComplaintDetail(id);
  const assignMutation = useAssignComplaint();
  const resolveMutation = useResolveComplaint();
  const statusMutation = useUpdateComplaintStatus();

  const handleAssign = () => {
    if (!id || !staffName) return;
    assignMutation.mutate({
      complaintId: id,
      assignedToName: staffName,
      assignedToPhone: staffPhone,
      priority
    }, {
      onSuccess: () => setAssignDialogOpen(false)
    });
  };

  const handleResolve = () => {
    if (!id || !resNotes) return;
    resolveMutation.mutate({
      complaintId: id,
      resolutionNotes: resNotes
    }, {
      onSuccess: () => {
        setResolveDialogOpen(false);
        setResNotes('');
      },
      onError: (error: any) => {
        const detail = error.response?.data?.detail;
        toast.error(detail || 'Failed to resolve complaint');
      }
    });
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
        <p className="text-muted-foreground">Loading complaint details...</p>
      </div>
    );
  }

  if (!complaint) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <p className="text-lg font-medium">Complaint not found</p>
        <Button variant="link" onClick={() => navigate('/admin/complaints')}>
          Back to complaints
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div className="flex items-start gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate('/admin/complaints')}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold tracking-tight">
                {complaint.title}
              </h1>
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span>#{complaint.id}</span>
              <span className="flex items-center gap-1">
                <Calendar className="h-3.5 w-3.5" />
                {format(new Date(complaint.created_at), 'MMM d, yyyy h:mm a')}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2 pl-12 sm:pl-0">
          <StatusBadge status={complaint.status} />
          <UrgencyBadge urgency={complaint.urgency} />
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-2">
        <Dialog open={assignDialogOpen} onOpenChange={setAssignDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" disabled={complaint.status === 'resolved'}>
              <UserPlus className="mr-2 h-4 w-4" />
              Assign Staff
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Assign Staff</DialogTitle>
              <DialogDescription>
                Assign this complaint to a field worker
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="staff-name">Staff Name</Label>
                <Input
                  id="staff-name"
                  placeholder="Enter staff name"
                  value={staffName}
                  onChange={(e) => setStaffName(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="staff-phone">Phone Number</Label>
                <Input
                  id="staff-phone"
                  placeholder="Enter phone number"
                  value={staffPhone}
                  onChange={(e) => setStaffPhone(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="priority">Priority</Label>
                <Select value={priority} onValueChange={setPriority}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="normal">Normal</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="urgent">Urgent</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setAssignDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleAssign} disabled={assignMutation.isPending}>
                {assignMutation.isPending ? 'Assigning...' : 'Assign'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <Dialog open={resolveDialogOpen} onOpenChange={setResolveDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" disabled={complaint.status === 'resolved'}>
              <CheckCircle className="mr-2 h-4 w-4" />
              Mark Resolved
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Resolve Complaint</DialogTitle>
              <DialogDescription>
                Provide resolution details for this complaint
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="resolution-notes">Resolution Notes</Label>
                <Textarea
                  id="resolution-notes"
                  placeholder="Describe the resolution..."
                  rows={4}
                  value={resNotes}
                  onChange={(e) => setResNotes(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="resolved-by">Resolved By</Label>
                <Input
                  id="resolved-by"
                  placeholder="Enter name or team"
                  value={resBy}
                  onChange={(e) => setResBy(e.target.value)}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setResolveDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleResolve} disabled={resolveMutation.isPending}>
                {resolveMutation.isPending ? 'Resolving...' : 'Resolve'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <Button
          variant="outline"
          onClick={() => toast.info('Escalation flow coming soon')}
        >
          <ArrowUpRight className="mr-2 h-4 w-4" />
          Escalate
        </Button>

        <Button
          variant="outline"
          className="text-destructive hover:text-destructive"
          onClick={() => {
            if (confirm('Are you sure you want to reject this complaint?')) {
              statusMutation.mutate({ complaintId: id!, status: 'rejected' });
            }
          }}
        >
          <XCircle className="mr-2 h-4 w-4" />
          Reject
        </Button>
      </div>

      {/* Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <Card>
            <CardHeader>
              <CardTitle>Description</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground leading-relaxed">
                {complaint.description}
              </p>
            </CardContent>
          </Card>

          {/* Media */}
          {complaint.media_urls && complaint.media_urls.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ImageIcon className="h-5 w-5" />
                  Attached Media
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {Array.isArray(complaint.media_urls) && complaint.media_urls.map((url, index) => (
                    <img
                      key={index}
                      src={url}
                      alt={`Complaint media ${index + 1}`}
                      className="rounded-lg object-cover w-full h-40"
                    />
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Location */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                Location
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-4">{complaint.location.address}</p>
              <div className="h-48 bg-muted rounded-lg flex items-center justify-center">
                <div className="text-center text-muted-foreground">
                  <MapPin className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">
                    Lat: {complaint.location.lat.toFixed(4)}, Lng:{' '}
                    {complaint.location.lng.toFixed(4)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* History Timeline */}
          {complaint.history && complaint.history.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Activity Timeline
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Array.isArray(complaint.history) && complaint.history.map((item, index) => (
                    <div key={index} className="flex gap-4">
                      <div className="relative">
                        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                          <MessageSquare className="h-4 w-4 text-primary" />
                        </div>
                        {index !== (complaint.history?.length || 0) - 1 && (
                          <div className="absolute top-8 left-1/2 -translate-x-1/2 w-0.5 h-full bg-border" />
                        )}
                      </div>
                      <div className="flex-1 pb-4">
                        <div className="flex items-center justify-between mb-1">
                          <p className="font-medium capitalize">
                            {item.action?.replace('_', ' ') || 'Action'}
                          </p>
                          <span className="text-sm text-muted-foreground">
                            {item.created_at ? format(new Date(item.created_at), 'MMM d, h:mm a') : 'Unknown'}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground">{item.notes}</p>
                        <p className="text-sm text-muted-foreground mt-1">
                          by {item.by?.name || 'Unknown'}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Complaint Info */}
          <Card>
            <CardHeader>
              <CardTitle>Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Category</span>
                <span className="flex items-center gap-2">
                  {complaint.category?.icon}
                  <span className="font-medium">{complaint.category?.name}</span>
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Department</span>
                <span className="font-medium">{complaint.department?.short_name}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Upvotes</span>
                <span className="flex items-center gap-1 font-medium">
                  <ThumbsUp className="h-4 w-4" />
                  {complaint.upvote_count || 0}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Submitter Info */}
          <Card>
            <CardHeader>
              <CardTitle>Submitted By</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                  <User className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="font-medium">{complaint.created_by?.name || 'Anonymous'}</p>
                  <p className="text-sm text-muted-foreground flex items-center gap-1">
                    <Phone className="h-3 w-3" />
                    {complaint.created_by?.phone}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Assignment Info */}
          {complaint.assigned_to && (
            <Card>
              <CardHeader>
                <CardTitle>Assigned To</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-accent/20 flex items-center justify-center">
                    <User className="h-5 w-5 text-accent" />
                  </div>
                  <div>
                    <p className="font-medium">{complaint.assigned_to.name}</p>
                    <p className="text-sm text-muted-foreground flex items-center gap-1">
                      <Phone className="h-3 w-3" />
                      {complaint.assigned_to.phone}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Resolution Info */}
          {complaint.status === 'resolved' && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-status-resolved" />
                  Resolution
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  {complaint.resolution_notes}
                </p>
                {complaint.resolved_at && (
                  <p className="text-sm text-muted-foreground">
                    Resolved on {format(new Date(complaint.resolved_at), 'MMM d, yyyy')}
                  </p>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
