import { useState } from 'react';
import { Trophy, TrendingUp, MapPin, Building2, Award, Medal } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { DEPARTMENTS, CATEGORIES } from '@/data/mockData';

const departmentRankings = [
  { id: 'dmrc', resolutionRate: 94.5, avgHours: 24, totalResolved: 156 },
  { id: 'ndmc', resolutionRate: 89.2, avgHours: 36, totalResolved: 234 },
  { id: 'mcd', resolutionRate: 78.5, avgHours: 48, totalResolved: 512 },
  { id: 'djb', resolutionRate: 72.3, avgHours: 72, totalResolved: 189 },
  { id: 'pwd', resolutionRate: 68.9, avgHours: 96, totalResolved: 145 },
  { id: 'bses', resolutionRate: 65.4, avgHours: 48, totalResolved: 198 },
].map((d) => ({
  ...d,
  department: Array.isArray(DEPARTMENTS) ? DEPARTMENTS.find((dept) => dept.id === d.id) : undefined,
}));

const topIssues = [
  { category_id: 'potholes', count: 234, trend: 12 },
  { category_id: 'garbage', count: 189, trend: -5 },
  { category_id: 'streetlights', count: 156, trend: 8 },
  { category_id: 'water', count: 134, trend: 3 },
  { category_id: 'sewage', count: 98, trend: 15 },
].map((issue) => ({
  ...issue,
  category: Array.isArray(CATEGORIES) ? CATEGORIES.find((c) => c.id === issue.category_id) : undefined,
}));

const hotspots = [
  { area: 'Connaught Place', complaints: 45, topIssue: 'Parking' },
  { area: 'Chandni Chowk', complaints: 38, topIssue: 'Encroachment' },
  { area: 'Rohini Sector 15', complaints: 32, topIssue: 'Garbage' },
  { area: 'Mayur Vihar', complaints: 28, topIssue: 'Water Supply' },
  { area: 'Dwarka Sector 12', complaints: 24, topIssue: 'Street Lights' },
];

export default function LeaderboardsPage() {
  const [activeTab, setActiveTab] = useState('departments');

  const getRankIcon = (index: number) => {
    if (index === 0) return <Trophy className="h-5 w-5 text-status-resolved" />;
    if (index === 1) return <Medal className="h-5 w-5 text-muted-foreground" />;
    if (index === 2) return <Award className="h-5 w-5 text-urgency-high" />;
    return <span className="w-5 h-5 flex items-center justify-center text-sm font-medium text-muted-foreground">{index + 1}</span>;
  };

  return (
    <div className="min-h-full bg-background">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-background border-b border-border">
        <div className="px-4 py-4">
          <div className="flex items-center gap-2">
            <Trophy className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-bold text-foreground">Leaderboards</h1>
          </div>
          <p className="text-sm text-muted-foreground mt-1">See how departments are performing</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="w-full justify-start px-4 h-auto pb-0 bg-transparent gap-4">
            <TabsTrigger
              value="departments"
              className="data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none pb-3"
            >
              <Building2 className="h-4 w-4 mr-1" />
              Departments
            </TabsTrigger>
            <TabsTrigger
              value="issues"
              className="data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none pb-3"
            >
              <TrendingUp className="h-4 w-4 mr-1" />
              Top Issues
            </TabsTrigger>
            <TabsTrigger
              value="hotspots"
              className="data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none pb-3"
            >
              <MapPin className="h-4 w-4 mr-1" />
              Hotspots
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Content */}
      <div className="p-4">
        {activeTab === 'departments' && (
          <div className="space-y-3">
            {Array.isArray(departmentRankings) && departmentRankings.map((dept, index) => (
              <Card key={dept.id} className={index < 3 ? 'border-primary/30' : ''}>
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-1">
                      {getRankIcon(index)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <h3 className="font-medium text-foreground truncate">
                          {dept.department?.name}
                        </h3>
                        <Badge variant="secondary" className="flex-shrink-0">
                          {dept.department?.short_name}
                        </Badge>
                      </div>

                      <div className="space-y-2">
                        <div>
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span className="text-muted-foreground">Resolution Rate</span>
                            <span className="font-medium text-foreground">{dept.resolutionRate}%</span>
                          </div>
                          <Progress value={dept.resolutionRate} className="h-2" />
                        </div>

                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span>{dept.totalResolved} resolved</span>
                          <span>Avg: {dept.avgHours}h</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {activeTab === 'issues' && (
          <div className="space-y-3">
            {Array.isArray(topIssues) && topIssues.map((issue, index) => (
              <Card key={issue.category_id}>
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="flex-shrink-0">
                      {getRankIcon(index)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xl">{issue.category?.icon}</span>
                          <h3 className="font-medium text-foreground">{issue.category?.name}</h3>
                        </div>
                        <Badge
                          variant={issue.trend > 0 ? 'destructive' : 'secondary'}
                          className="text-xs"
                        >
                          {issue.trend > 0 ? '+' : ''}{issue.trend}%
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {issue.count} complaints this month
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}

            <Card className="bg-muted/50">
              <CardContent className="py-3 px-4">
                <p className="text-xs text-muted-foreground text-center">
                  Based on complaints in your area (10km radius)
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === 'hotspots' && (
          <div className="space-y-3">
            {Array.isArray(hotspots) && hotspots.map((spot, index) => (
              <Card key={spot.area}>
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="flex-shrink-0">
                      {getRankIcon(index)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-medium text-foreground">{spot.area}</h3>
                        <Badge variant="outline">{spot.complaints} issues</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Top issue: {spot.topIssue}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}

            {/* Map placeholder */}
            <Card>
              <CardContent className="p-0">
                <div className="h-48 bg-muted flex items-center justify-center rounded-lg">
                  <div className="text-center">
                    <MapPin className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">Hotspot map coming soon</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
