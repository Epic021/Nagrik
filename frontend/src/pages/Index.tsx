import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Shield, Users, ArrowRight } from 'lucide-react';

const Index = () => {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Hero */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">NAGRIK</h1>
          <p className="text-lg text-muted-foreground">
            Civic Complaints Management Platform
          </p>
        </div>

        <div className="w-full max-w-sm space-y-4">
          {/* Citizen App */}
          <Link to="/citizen">
            <Card className="cursor-pointer hover:shadow-lg transition-shadow border-primary/20 hover:border-primary/40">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                    <Users className="h-6 w-6 text-primary" />
                  </div>
                  <div className="flex-1 text-left">
                    <h2 className="font-semibold text-foreground">Citizen App</h2>
                    <p className="text-sm text-muted-foreground">Report & track issues</p>
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>
          </Link>

          {/* Admin Dashboard */}
          <Link to="/login">
            <Card className="cursor-pointer hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
                    <Shield className="h-6 w-6 text-muted-foreground" />
                  </div>
                  <div className="flex-1 text-left">
                    <h2 className="font-semibold text-foreground">Admin Dashboard</h2>
                    <p className="text-sm text-muted-foreground">Department login</p>
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>
          </Link>
        </div>
      </div>

      {/* Footer */}
      <div className="p-6 text-center">
        <p className="text-xs text-muted-foreground">
          Made with ❤️ for Delhi Citizens
        </p>
      </div>
    </div>
  );
};

export default Index;
