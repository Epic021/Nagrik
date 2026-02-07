import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import { DashboardData, TrendsData } from '@/types';
import { toast } from 'sonner';

export function useDepartments() {
    return useQuery<any[]>({
        queryKey: ['admin', 'departments'],
        queryFn: async () => {
            const response = await api.get('/admin/departments'); // We'll need to check if this exists or add it
            return response.data;
        },
    });
}

export function useRegisterAdmin() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (data: any) => {
            const response = await api.post('/admin/register', data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'staff'] });
            toast.success('Admin registered successfully');
        },
    });
}

export function useAdminDashboard() {
    return useQuery<DashboardData>({
        queryKey: ['admin', 'dashboard'],
        queryFn: async () => {
            const response = await api.get('/admin/dashboard');
            return response.data;
        },
    });
}

export function useAdminTrends(days: number = 30) {
    return useQuery<TrendsData>({
        queryKey: ['admin', 'trends', days],
        queryFn: async () => {
            const response = await api.get('/admin/dashboard/trends', { params: { days } });
            return response.data;
        },
    });
}

export function useUpdateComplaintStatus() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async ({
            complaintId,
            status,
            notes
        }: {
            complaintId: string;
            status: string;
            notes?: string
        }) => {
            const response = await api.put(`/admin/complaints/${complaintId}/status`, { status, notes });
            return response.data;
        },
        onSuccess: (data, variables) => {
            queryClient.invalidateQueries({ queryKey: ['complaints'] });
            queryClient.invalidateQueries({ queryKey: ['admin', 'dashboard'] });
            toast.success(`Status updated to ${variables.status}`);
        },
    });
}

export function useAssignComplaint() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async ({
            complaintId,
            assignedToName,
            assignedToPhone,
            priority
        }: {
            complaintId: string;
            assignedToName: string;
            assignedToPhone?: string;
            priority?: string;
        }) => {
            const response = await api.put(`/admin/complaints/${complaintId}/assign`, {
                assigned_to_name: assignedToName,
                assigned_to_phone: assignedToPhone,
                priority
            });
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['complaints'] });
            queryClient.invalidateQueries({ queryKey: ['admin', 'dashboard'] });
            toast.success('Complaint assigned successfully');
        },
    });
}

export function useResolveComplaint() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async ({
            complaintId,
            resolutionNotes
        }: {
            complaintId: string;
            resolutionNotes: string
        }) => {
            const response = await api.put(`/admin/complaints/${complaintId}/resolve`, { resolution_notes: resolutionNotes });
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['complaints'] });
            queryClient.invalidateQueries({ queryKey: ['admin', 'dashboard'] });
            toast.success('Complaint marked as resolved');
        },
    });
}
