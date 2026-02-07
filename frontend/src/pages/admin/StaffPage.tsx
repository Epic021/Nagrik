import { useState } from 'react';
import { Users, Phone, Building2, Plus, Loader2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useRegisterAdmin, useDepartments } from '@/hooks/use-admin';
import { useAuth } from '@/contexts/AuthContext';

export default function StaffPage() {
  const { user } = useAuth();
  const isSuperAdmin = user?.role === 'super_admin';
  const { data: departments = [], isLoading: isLoadingDepts } = useDepartments();
  const registerAdmin = useRegisterAdmin();

  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    password: '',
    department_id: '',
  });

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await registerAdmin.mutateAsync(formData);
      setOpen(false);
      setFormData({ name: '', phone: '', password: '', department_id: '' });
    } catch (error) {
      // Error handled by hook/interceptor
    }
  };

  // For now we still show some mock data if there's no real staff list from backend
  const MOCK_STAFF = [
    { id: '1', name: 'Ramesh Kumar', phone: '9876543220', department: 'MCD', active_tasks: 3 },
    { id: '2', name: 'Suresh Yadav', phone: '9876543221', department: 'MCD', active_tasks: 5 },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Staff Management</h1>
          <p className="text-muted-foreground mt-1">
            View and manage department administrators and field staff
          </p>
        </div>

        {isSuperAdmin && (
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Add Department Admin
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <form onSubmit={handleRegister}>
                <DialogHeader>
                  <DialogTitle>Add Department Admin</DialogTitle>
                  <DialogDescription>
                    Register a new administrator for a specific department.
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="name" className="text-right text-xs">Name</Label>
                    <Input
                      id="name"
                      className="col-span-3"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="e.g. John Doe"
                      required
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="phone" className="text-right text-xs">Phone</Label>
                    <Input
                      id="phone"
                      className="col-span-3"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      placeholder="10 digit mobile"
                      required
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="dept" className="text-right text-xs">Dept</Label>
                    <div className="col-span-3">
                      <Select
                        value={formData.department_id}
                        onValueChange={(val) => setFormData({ ...formData, department_id: val })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select Department" />
                        </SelectTrigger>
                        <SelectContent>
                          {departments.map((dept) => (
                            <SelectItem key={dept.id} value={dept.id}>
                              {dept.short_name} - {dept.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="pass" className="text-right text-xs">Pass</Label>
                    <Input
                      id="pass"
                      type="password"
                      className="col-span-3"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      placeholder="Min 6 characters"
                      required
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit" disabled={registerAdmin.isPending}>
                    {registerAdmin.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Register Admin
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        )}
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
