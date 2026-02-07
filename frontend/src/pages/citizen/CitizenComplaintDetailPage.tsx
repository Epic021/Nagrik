import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, MapPin, ChevronUp, Share2, Clock, User, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { StatusBadge } from '@/components/StatusBadge';
import { useAuth } from '@/contexts/AuthContext';
import { useComplaintDetail, useUpvoteComplaint, useVerifyResolution } from '@/hooks/use-complaints';
import { toast } from 'sonner';

export default function CitizenComplaintDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [verifyDialogOpen, setVerifyDialogOpen] = useState(false);
  const [feedback, setFeedback] = useState('');

  const { data: complaint, isLoading } = useComplaintDetail(id);
  const upvoteMutation = useUpvoteComplaint();
  const verifyMutation = useVerifyResolution();

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
        <p className="text-muted-foreground">Loading details...</p>
      </div>
    );
  }

  if (!complaint) {
    return (
      <div className="flex items-center justify-center h-full py-12">
        <p className="text-muted-foreground">Complaint not found</p>
      </div>
    );
  }

  const isOwner = user?.id === complaint.created_by.id;
  const canVerify = isOwner && complaint.status === 'resolved';

  const handleUpvote = () => {
    if (!id) return;
    upvoteMutation.mutate(id);
  };

  const handleVerify = (accepted: boolean) => {
    if (!id) return;
    verifyMutation.mutate({
      id,
      accepted,
      feedback: feedback || undefined
    }, {
      onSuccess: () => {
        setVerifyDialogOpen(false);
        setFeedback('');
      }
    });
  };

  const handleShare = async () => {
    try {
      await navigator.share({
        title: complaint.title,
        text: complaint.description,
        url: window.location.href,
      });
    } catch {
      navigator.clipboard.writeText(window.location.href);
      toast.success('Link copied to clipboard');
    }
  };

  const urgencyColors: Record<string, string> = {
    low: 'bg-muted text-muted-foreground',
    normal: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    high: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
    urgent: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  };

  return (
    <div className="min-h-full bg-background">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-background border-b border-border">
        <div className="flex items-center gap-3 px-4 py-3">
          <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="font-semibold text-foreground flex-1 truncate">Complaint Details</h1>
          <Button variant="ghost" size="icon" onClick={handleShare}>
            <Share2 className="h-5 w-5" />
          </Button>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Media Gallery */}
        {complaint.media_urls && complaint.media_urls.length > 0 && (
          <div className="rounded-xl overflow-hidden">
            <img
              src={complaint.media_urls[0]}
              alt="Complaint"
              className="w-full h-48 object-cover"
            />
          </div>
        )}

        {/* Title & Status */}
        <div>
          <div className="flex items-start justify-between gap-3 mb-2">
            <h2 className="text-lg font-semibold text-foreground">{complaint.title}</h2>
            <StatusBadge status={complaint.status} />
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="secondary" className="text-xs">
              {complaint.category?.icon} {complaint.category?.name}
            </Badge>
            <Badge className={urgencyColors[complaint.urgency]}>
              {complaint.urgency.toUpperCase()}
            </Badge>
          </div>
        </div>

        {/* Upvote & Actions */}
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            className="flex-1"
            onClick={handleUpvote}
            disabled={upvoteMutation.isPending}
          >
            <ChevronUp className="h-4 w-4 mr-1" />
            Upvote ({complaint.upvote_count || 0})
          </Button>
          {canVerify && (
            <Button variant="outline" className="flex-1" onClick={() => setVerifyDialogOpen(true)}>
              <CheckCircle className="h-4 w-4 mr-1" />
              Verify Resolution
            </Button>
          )}
        </div>

        <Separator />

        {/* Description */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Description</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{complaint.description}</p>
          </CardContent>
        </Card>

        {/* Location */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <MapPin className="h-4 w-4" />
              Location
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{complaint.location.address}</p>
            <div className="mt-3 h-32 bg-muted rounded-lg flex items-center justify-center">
              <div className="text-center">
                <MapPin className="h-6 w-6 mx-auto mb-1 opacity-50" />
                <p className="text-[10px] text-muted-foreground">
                  {complaint.location.lat.toFixed(4)}, {complaint.location.lng.toFixed(4)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Details */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Submitted
              </span>
              <span>{new Date(complaint.created_at).toLocaleDateString()}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground flex items-center gap-2">
                <User className="h-4 w-4" />
                Reported by
              </span>
              <span>{complaint.created_by?.name || 'Anonymous'}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Department</span>
              <Badge variant="outline">{complaint.department?.short_name}</Badge>
            </div>
            {complaint.assigned_to && (
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Assigned to</span>
                <span>{complaint.assigned_to.name}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Resolution (if resolved) */}
        {complaint.status === 'resolved' && complaint.resolution_notes && (
          <Card className="border-status-resolved/30 bg-status-resolved/5">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-status-resolved flex items-center gap-2">
                <CheckCircle className="h-4 w-4" />
                Resolution
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{complaint.resolution_notes}</p>
              {complaint.resolved_at && (
                <p className="text-xs text-muted-foreground mt-2">
                  Resolved on {new Date(complaint.resolved_at).toLocaleDateString()}
                </p>
              )}
            </CardContent>
          </Card>
        )}

        {/* Activity Timeline */}
        {complaint.history && complaint.history.length > 0 && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Array.isArray(complaint.history) && complaint.history.map((entry, index) => (
                  <div key={index} className="flex gap-3">
                    <div className="flex flex-col items-center">
                      <div className="w-2 h-2 rounded-full bg-primary" />
                      {index < (complaint.history?.length || 0) - 1 && (
                        <div className="w-px h-full bg-border flex-1" />
                      )}
                    </div>
                    <div className="flex-1 pb-4">
                      <p className="text-sm font-medium capitalize">{entry.action?.replace('_', ' ') || 'Action'}</p>
                      {entry.notes && (
                        <p className="text-xs text-muted-foreground mt-1">{entry.notes}</p>
                      )}
                      <p className="text-xs text-muted-foreground mt-1">
                        {entry.by?.name || 'Unknown'} • {entry.created_at ? new Date(entry.created_at).toLocaleString() : 'Unknown date'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Verify Dialog */}
      <Dialog open={verifyDialogOpen} onOpenChange={setVerifyDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Verify Resolution</DialogTitle>
            <DialogDescription>
              Has this issue been resolved to your satisfaction?
            </DialogDescription>
          </DialogHeader>
          <Textarea
            placeholder="Add feedback (optional)"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
          />
          <DialogFooter className="flex gap-2">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => handleVerify(false)}
              disabled={verifyMutation.isPending}
            >
              <XCircle className="h-4 w-4 mr-1" />
              Not Fixed
            </Button>
            <Button
              className="flex-1"
              onClick={() => handleVerify(true)}
              disabled={verifyMutation.isPending}
            >
              <CheckCircle className="h-4 w-4 mr-1" />
              Confirm Fixed
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
