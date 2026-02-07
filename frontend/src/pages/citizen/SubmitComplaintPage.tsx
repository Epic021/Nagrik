import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Camera, Upload, MapPin, Sparkles, Check, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { CATEGORIES, DEPARTMENTS } from '@/data/mockData';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

type Step = 'media' | 'classify' | 'location' | 'confirm';

const steps: { id: Step; label: string }[] = [
  { id: 'media', label: 'Upload' },
  { id: 'classify', label: 'Category' },
  { id: 'location', label: 'Location' },
  { id: 'confirm', label: 'Submit' },
];

export default function SubmitComplaintPage() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<Step>('media');
  const [isClassifying, setIsClassifying] = useState(false);
  const [formData, setFormData] = useState({
    imageUrl: '',
    title: '',
    description: '',
    category_id: '',
    suggestedCategory: '',
    confidence: 0,
    urgency: 'normal',
    location: {
      lat: 28.6139,
      lng: 77.2090,
      address: '',
    },
  });

  const currentStepIndex = steps.findIndex((s) => s.id === currentStep);
  const progress = ((currentStepIndex + 1) / steps.length) * 100;

  const handleImageUpload = () => {
    // Simulated image upload
    setFormData((prev) => ({
      ...prev,
      imageUrl: 'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=400',
    }));
    toast.success('Image uploaded');
  };

  const handleAIClassify = async () => {
    setIsClassifying(true);
    // Simulate AI classification
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setFormData((prev) => ({
      ...prev,
      suggestedCategory: 'potholes',
      category_id: 'potholes',
      confidence: 0.92,
      urgency: 'high',
    }));
    setIsClassifying(false);
    toast.success('AI classification complete');
  };

  const handleGetLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData((prev) => ({
            ...prev,
            location: {
              lat: position.coords.latitude,
              lng: position.coords.longitude,
              address: 'MG Road, Near Metro Station, Central Delhi',
            },
          }));
          toast.success('Location detected');
        },
        () => {
          toast.error('Could not get location');
        }
      );
    }
  };

  const handleSubmit = () => {
    toast.success('Complaint submitted successfully!');
    navigate('/citizen/my-complaints');
  };

  const canProceed = () => {
    switch (currentStep) {
      case 'media':
        return formData.title && formData.description;
      case 'classify':
        return formData.category_id;
      case 'location':
        return formData.location.address;
      case 'confirm':
        return true;
      default:
        return false;
    }
  };

  const nextStep = () => {
    const idx = steps.findIndex((s) => s.id === currentStep);
    if (idx < steps.length - 1) {
      setCurrentStep(steps[idx + 1].id);
    }
  };

  const prevStep = () => {
    const idx = steps.findIndex((s) => s.id === currentStep);
    if (idx > 0) {
      setCurrentStep(steps[idx - 1].id);
    } else {
      navigate(-1);
    }
  };

  return (
    <div className="min-h-full bg-background flex flex-col">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-background border-b border-border">
        <div className="flex items-center gap-3 px-4 py-3">
          <Button variant="ghost" size="icon" onClick={prevStep}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="font-semibold text-foreground flex-1">Report Issue</h1>
          <span className="text-sm text-muted-foreground">
            {currentStepIndex + 1}/{steps.length}
          </span>
        </div>
        <Progress value={progress} className="h-1" />
      </div>

      {/* Step Indicators */}
      <div className="flex items-center justify-center gap-2 py-4 px-4 border-b border-border">
        {steps.map((step, index) => (
          <div
            key={step.id}
            className={cn(
              "flex items-center gap-1",
              index <= currentStepIndex ? "text-primary" : "text-muted-foreground"
            )}
          >
            <div
              className={cn(
                "w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium",
                index < currentStepIndex
                  ? "bg-primary text-primary-foreground"
                  : index === currentStepIndex
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground"
              )}
            >
              {index < currentStepIndex ? <Check className="h-3 w-3" /> : index + 1}
            </div>
            <span className="text-xs hidden sm:inline">{step.label}</span>
            {index < steps.length - 1 && (
              <div className="w-6 h-px bg-border mx-1" />
            )}
          </div>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 p-4 overflow-auto">
        {currentStep === 'media' && (
          <div className="space-y-4">
            {/* Image Upload */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Upload Photo</CardTitle>
              </CardHeader>
              <CardContent>
                {formData.imageUrl ? (
                  <div className="relative">
                    <img
                      src={formData.imageUrl}
                      alt="Uploaded"
                      className="w-full h-48 object-cover rounded-lg"
                    />
                    <Button
                      variant="secondary"
                      size="sm"
                      className="absolute top-2 right-2"
                      onClick={() => setFormData((prev) => ({ ...prev, imageUrl: '' }))}
                    >
                      Change
                    </Button>
                  </div>
                ) : (
                  <div className="flex gap-3">
                    <Button variant="outline" className="flex-1 h-24 flex-col" onClick={handleImageUpload}>
                      <Camera className="h-6 w-6 mb-2" />
                      <span className="text-xs">Take Photo</span>
                    </Button>
                    <Button variant="outline" className="flex-1 h-24 flex-col" onClick={handleImageUpload}>
                      <Upload className="h-6 w-6 mb-2" />
                      <span className="text-xs">Upload</span>
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Title & Description */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Describe the Issue</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Title *</Label>
                  <Input
                    id="title"
                    placeholder="e.g., Large pothole on main road"
                    value={formData.title}
                    onChange={(e) => setFormData((prev) => ({ ...prev, title: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description *</Label>
                  <Textarea
                    id="description"
                    placeholder="Provide more details about the issue..."
                    rows={4}
                    value={formData.description}
                    onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {currentStep === 'classify' && (
          <div className="space-y-4">
            {/* AI Classification */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-primary" />
                  AI Classification
                </CardTitle>
              </CardHeader>
              <CardContent>
                {formData.suggestedCategory ? (
                  <div className="p-4 bg-primary/10 rounded-lg border border-primary/20">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Suggested Category</span>
                      <Badge variant="secondary">
                        {Math.round(formData.confidence * 100)}% confident
                      </Badge>
                    </div>
                    <Badge className="text-sm">
                      {CATEGORIES.find((c) => c.id === formData.suggestedCategory)?.icon}{' '}
                      {CATEGORIES.find((c) => c.id === formData.suggestedCategory)?.name}
                    </Badge>
                  </div>
                ) : (
                  <Button
                    onClick={handleAIClassify}
                    disabled={isClassifying}
                    className="w-full"
                  >
                    {isClassifying ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-4 w-4 mr-2" />
                        Auto-classify with AI
                      </>
                    )}
                  </Button>
                )}
              </CardContent>
            </Card>

            {/* Manual Category Selection */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Select Category</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-2">
                  {CATEGORIES.map((category) => (
                    <Button
                      key={category.id}
                      variant={formData.category_id === category.id ? 'default' : 'outline'}
                      className="h-auto py-3 flex-col"
                      onClick={() => setFormData((prev) => ({ ...prev, category_id: category.id }))}
                    >
                      <span className="text-xl mb-1">{category.icon}</span>
                      <span className="text-xs">{category.name}</span>
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Urgency */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Urgency Level</CardTitle>
              </CardHeader>
              <CardContent>
                <Select
                  value={formData.urgency}
                  onValueChange={(value) => setFormData((prev) => ({ ...prev, urgency: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low - Can wait</SelectItem>
                    <SelectItem value="normal">Normal - Within a week</SelectItem>
                    <SelectItem value="high">High - Needs attention soon</SelectItem>
                    <SelectItem value="urgent">Urgent - Immediate danger</SelectItem>
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>
          </div>
        )}

        {currentStep === 'location' && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  Location
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button variant="outline" className="w-full" onClick={handleGetLocation}>
                  <MapPin className="h-4 w-4 mr-2" />
                  Use Current Location
                </Button>

                <div className="relative">
                  <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">
                    or
                  </span>
                  <div className="border-t border-border" />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="address">Enter Address</Label>
                  <Input
                    id="address"
                    placeholder="Enter address or landmark"
                    value={formData.location.address}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        location: { ...prev.location, address: e.target.value },
                      }))
                    }
                  />
                </div>

                {/* Map Preview Placeholder */}
                <div className="h-48 bg-muted rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <MapPin className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                    <p className="text-xs text-muted-foreground">Map preview</p>
                    {formData.location.address && (
                      <p className="text-xs text-foreground mt-2">{formData.location.address}</p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {currentStep === 'confirm' && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Review Your Complaint</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {formData.imageUrl && (
                  <img
                    src={formData.imageUrl}
                    alt="Complaint"
                    className="w-full h-32 object-cover rounded-lg"
                  />
                )}

                <div className="space-y-3">
                  <div>
                    <Label className="text-xs text-muted-foreground">Title</Label>
                    <p className="font-medium">{formData.title}</p>
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground">Description</Label>
                    <p className="text-sm text-muted-foreground">{formData.description}</p>
                  </div>
                  <div className="flex gap-2">
                    <Badge>
                      {CATEGORIES.find((c) => c.id === formData.category_id)?.icon}{' '}
                      {CATEGORIES.find((c) => c.id === formData.category_id)?.name}
                    </Badge>
                    <Badge variant="outline" className="capitalize">{formData.urgency}</Badge>
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground">Location</Label>
                    <p className="text-sm flex items-center gap-1">
                      <MapPin className="h-3 w-3" />
                      {formData.location.address}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-muted/50">
              <CardContent className="py-4">
                <p className="text-xs text-muted-foreground text-center">
                  By submitting, you confirm that the information provided is accurate.
                  Your complaint will be routed to the appropriate department.
                </p>
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="sticky bottom-0 bg-background border-t border-border p-4 safe-area-bottom">
        {currentStep === 'confirm' ? (
          <Button className="w-full" size="lg" onClick={handleSubmit}>
            Submit Complaint
          </Button>
        ) : (
          <Button
            className="w-full"
            size="lg"
            onClick={nextStep}
            disabled={!canProceed()}
          >
            Continue
          </Button>
        )}
      </div>
    </div>
  );
}
