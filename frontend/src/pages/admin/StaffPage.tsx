import { Users, Phone, Building2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const MOCK_STAFF = [
  { id: '1', name: 'Ramesh Kumar', phone: '9876543220', department: 'MCD', active_tasks: 3 },
  { id: '2', name: 'Suresh Yadav', phone: '9876543221', department: 'MCD', active_tasks: 5 },
  { id: '3', name: 'Manoj Singh', phone: '9876543222', department: 'PWD', active_tasks: 2 },
  { id: '4', name: 'Priya Sharma', phone: '9876543223', department: 'DJB', active_tasks: 4 },
];

export default function StaffPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Staff Management</h1>
          <p className="text-muted-foreground mt-1">
            View and manage field staff assignments
          </p>
        </div>
        <Button>
          <Users className="mr-2 h-4 w-4" />
          Add Staff
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {MOCK_STAFF.map((staff) => (
          <Card key={staff.id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                  <span className="text-lg font-semibold text-primary">
                    {staff.name.charAt(0)}
                  </span>
                </div>
                <div>
                  <CardTitle className="text-lg">{staff.name}</CardTitle>
                  <CardDescription className="flex items-center gap-1">
                    <Phone className="h-3 w-3" />
                    {staff.phone}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Building2 className="h-4 w-4" />
                  {staff.department}
                </div>
                <div className="text-sm">
                  <span className="font-medium">{staff.active_tasks}</span> active tasks
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
