import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { AdminLayout } from "@/components/layout/AdminLayout";
import { CitizenLayout } from "@/components/layout/CitizenLayout";
import Index from "./pages/Index";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/admin/DashboardPage";
import ComplaintsListPage from "./pages/admin/ComplaintsListPage";
import ComplaintDetailPage from "./pages/admin/ComplaintDetailPage";
import StaffPage from "./pages/admin/StaffPage";
import SettingsPage from "./pages/admin/SettingsPage";
import HomePage from "./pages/citizen/HomePage";
import CitizenComplaintDetailPage from "./pages/citizen/CitizenComplaintDetailPage";
import SubmitComplaintPage from "./pages/citizen/SubmitComplaintPage";
import MyComplaintsPage from "./pages/citizen/MyComplaintsPage";
import LeaderboardsPage from "./pages/citizen/LeaderboardsPage";
import ProfilePage from "./pages/citizen/ProfilePage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isAdmin } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (!isAdmin) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function CitizenRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isCitizen } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (!isCitizen) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Index />} />
      <Route path="/login" element={<LoginPage />} />
      
      {/* Citizen App Routes */}
      <Route
        path="/citizen"
        element={
          <CitizenRoute>
            <CitizenLayout />
          </CitizenRoute>
        }
      >
        <Route index element={<HomePage />} />
        <Route path="complaints/:id" element={<CitizenComplaintDetailPage />} />
        <Route path="submit" element={<SubmitComplaintPage />} />
        <Route path="my-complaints" element={<MyComplaintsPage />} />
        <Route path="leaderboards" element={<LeaderboardsPage />} />
        <Route path="profile" element={<ProfilePage />} />
      </Route>

      {/* Admin Dashboard Routes */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute>
            <AdminLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="complaints" element={<ComplaintsListPage />} />
        <Route path="complaints/:id" element={<ComplaintDetailPage />} />
        <Route path="staff" element={<StaffPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
