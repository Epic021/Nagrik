import { useState } from 'react';
import { Link } from 'react-router-dom';
import { MapPin, List, Filter, Search, ChevronUp, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { StatusBadge } from '@/components/StatusBadge';
import { MOCK_COMPLAINTS, CATEGORIES } from '@/data/mockData';

export default function HomePage() {
  const [viewMode, setViewMode] = useState<'list' | 'map'>('list');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredComplaints = MOCK_COMPLAINTS.filter((complaint) => {
    const matchesCategory = selectedCategory === 'all' || complaint.category_id === selectedCategory;
    const matchesSearch = complaint.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      complaint.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-background border-b border-border">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h1 className="text-xl font-bold text-foreground">NAGRIK</h1>
              <p className="text-xs text-muted-foreground">Civic Complaints Near You</p>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="icon" className="h-9 w-9">
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Search */}
          <div className="relative mb-3">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search complaints..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 h-10"
            />
          </div>

          {/* View Toggle & Category Filter */}
          <div className="flex items-center gap-2">
            <Tabs value={viewMode} onValueChange={(v) => setViewMode(v as 'list' | 'map')} className="flex-shrink-0">
              <TabsList className="h-8">
                <TabsTrigger value="list" className="text-xs px-3 h-7">
                  <List className="h-3 w-3 mr-1" />
                  List
                </TabsTrigger>
                <TabsTrigger value="map" className="text-xs px-3 h-7">
                  <MapPin className="h-3 w-3 mr-1" />
                  Map
                </TabsTrigger>
              </TabsList>
            </Tabs>

            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="h-8 text-xs flex-1">
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {CATEGORIES.map((cat) => (
                  <SelectItem key={cat.id} value={cat.id}>
                    {cat.icon} {cat.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {viewMode === 'list' ? (
          <div className="p-4 space-y-3">
            {filteredComplaints.map((complaint) => (
              <Link key={complaint.id} to={`/citizen/complaints/${complaint.id}`}>
                <Card className="overflow-hidden hover:shadow-md transition-shadow">
                  <CardContent className="p-0">
                    <div className="flex">
                      {/* Image */}
                      {complaint.media_urls.length > 0 && (
                        <div className="w-24 h-24 flex-shrink-0">
                          <img
                            src={complaint.media_urls[0]}
                            alt=""
                            className="w-full h-full object-cover"
                          />
                        </div>
                      )}
                      
                      {/* Content */}
                      <div className="flex-1 p-3">
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <h3 className="font-medium text-sm line-clamp-2 text-foreground">
                            {complaint.title}
                          </h3>
                          <StatusBadge status={complaint.status} size="sm" />
                        </div>
                        
                        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                          <span>{complaint.category?.icon} {complaint.category?.name}</span>
                          <span>•</span>
                          <span>{new Date(complaint.created_at).toLocaleDateString()}</span>
                        </div>

                        <div className="flex items-center gap-3 text-xs">
                          <div className="flex items-center gap-1 text-muted-foreground">
                            <MapPin className="h-3 w-3" />
                            <span className="truncate max-w-[120px]">{complaint.location.address.split(',')[0]}</span>
                          </div>
                          <div className="flex items-center gap-1 text-primary font-medium">
                            <ChevronUp className="h-3 w-3" />
                            <span>{complaint.upvotes}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}

            {filteredComplaints.length === 0 && (
              <div className="text-center py-12 text-muted-foreground">
                <MessageSquare className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No complaints found</p>
              </div>
            )}
          </div>
        ) : (
          <div className="h-full flex items-center justify-center bg-muted/30">
            <div className="text-center p-8">
              <MapPin className="h-16 w-16 mx-auto mb-4 text-muted-foreground/50" />
              <p className="text-muted-foreground">Map view coming soon</p>
              <p className="text-xs text-muted-foreground mt-1">Integration with maps API pending</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
