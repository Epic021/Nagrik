import { Outlet } from 'react-router-dom';
import { AdminSidebar } from './AdminSidebar';

export function AdminLayout() {
  return (
    <div className="flex min-h-screen w-full bg-background">
      <AdminSidebar />
      <main className="flex-1 overflow-auto">
        <div className="container py-6 lg:py-8 px-4 lg:px-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
