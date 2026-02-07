import { useNavigate } from 'react-router-dom';
import { User, Phone, Shield, LogOut, ChevronRight, Bell, Moon, HelpCircle, FileText, Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
    navigate('/');
  };

  const menuItems = [
    {
      icon: Bell,
      label: 'Notifications',
      description: 'Manage notification preferences',
      action: 'navigate',
    },
    {
      icon: Moon,
      label: 'Dark Mode',
      description: 'Toggle dark theme',
      action: 'toggle',
    },
    {
      icon: Star,
      label: 'Rate App',
      description: 'Share your feedback',
      action: 'external',
    },
    {
      icon: HelpCircle,
      label: 'Help & Support',
      description: 'FAQs and contact us',
      action: 'navigate',
    },
    {
      icon: FileText,
      label: 'Terms & Privacy',
      description: 'Legal information',
      action: 'navigate',
    },
  ];

  const stats = [
    { label: 'Submitted', value: 5 },
    { label: 'Resolved', value: 3 },
    { label: 'Upvotes', value: 127 },
  ];

  return (
    <div className="min-h-full bg-background">
      {/* Header */}
      <div className="bg-primary text-primary-foreground px-4 pt-8 pb-12">
        <h1 className="text-xl font-bold mb-1">Profile</h1>
        <p className="text-sm opacity-80">Manage your account</p>
      </div>

      {/* Profile Card */}
      <div className="px-4 -mt-8">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <Avatar className="h-16 w-16">
                <AvatarFallback className="text-lg bg-primary text-primary-foreground">
                  {user?.name?.charAt(0) || 'U'}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <h2 className="font-semibold text-lg text-foreground truncate">
                  {user?.name || 'Guest User'}
                </h2>
                <p className="text-sm text-muted-foreground flex items-center gap-1">
                  <Phone className="h-3 w-3" />
                  {user?.phone || 'Not logged in'}
                </p>
                <div className="flex items-center gap-1 mt-1">
                  <Shield className="h-3 w-3 text-primary" />
                  <span className="text-xs text-primary capitalize">{user?.role || 'Guest'}</span>
                </div>
              </div>
              <Button variant="outline" size="sm">
                Edit
              </Button>
            </div>

            <Separator className="my-4" />

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 text-center">
              {stats.map((stat) => (
                <div key={stat.label}>
                  <p className="text-2xl font-bold text-foreground">{stat.value}</p>
                  <p className="text-xs text-muted-foreground">{stat.label}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Menu Items */}
      <div className="px-4 mt-4 space-y-2">
        {menuItems.map((item) => (
          <Card key={item.label} className="cursor-pointer hover:bg-muted/50 transition-colors">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center">
                  <item.icon className="h-5 w-5 text-muted-foreground" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-foreground">{item.label}</h3>
                  <p className="text-xs text-muted-foreground">{item.description}</p>
                </div>
                {item.action === 'toggle' ? (
                  <Switch />
                ) : (
                  <ChevronRight className="h-5 w-5 text-muted-foreground" />
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Logout */}
      <div className="px-4 mt-6 pb-8">
        <Button
          variant="outline"
          className="w-full text-destructive border-destructive/30 hover:bg-destructive/10"
          onClick={handleLogout}
        >
          <LogOut className="h-4 w-4 mr-2" />
          Logout
        </Button>

        <p className="text-xs text-center text-muted-foreground mt-4">
          NAGRIK v1.0.0 • Made with ❤️ for Delhi
        </p>
      </div>
    </div>
  );
}
