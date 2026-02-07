import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import { Category, Complaint, UrgencyLevel } from '@/types';
import { toast } from 'sonner';

export function useCategories() {
    return useQuery<Category[]>({
        queryKey: ['categories'],
        queryFn: async () => {
            const response = await api.get('/categories');
            return response.data;
        },
    });
}

export function useComplaints(filters: any = {}) {
    return useQuery<Complaint[]>({
        queryKey: ['complaints', filters],
        queryFn: async () => {
            const response = await api.get('/complaints', { params: filters });
            return response.data.complaints;
        },
    });
}

export function useComplaintDetail(id: string | undefined) {
    return useQuery<Complaint>({
        queryKey: ['complaints', id],
        queryFn: async () => {
            if (!id) throw new Error('Complaint ID is required');
            const response = await api.get(`/complaints/${id}`);
            return response.data;
        },
        enabled: !!id,
    });
}

export function useMyComplaints() {
    return useQuery<Complaint[]>({
        queryKey: ['complaints', 'my'],
        queryFn: async () => {
            const response = await api.get('/complaints/my');
            return response.data.complaints;
        },
    });
}

export function useSubmitComplaint() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (data: {
            title: string;
            description: string;
            category_id: string;
            location: { lat: number; lng: number; address: string };
            media_urls: string[];
            urgency: UrgencyLevel;
        }) => {
            const response = await api.post('/complaints', data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['complaints'] });
            toast.success('Complaint submitted successfully!');
        },
    });
}

export function useClassifyImage() {
    return useMutation({
        mutationFn: async (data: { image_url: string; description?: string }) => {
            const response = await api.post('/classify/from-image', data);
            return response.data;
        },
    });
}

export function useClassifyText() {
    return useMutation({
        mutationFn: async (data: { title: string; description: string }) => {
            const response = await api.post('/classify/from-text', data);
            return response.data;
        },
    });
}

export function useUploadFile() {
    return useMutation({
        mutationFn: async (file: File) => {
            const formData = new FormData();
            formData.append('file', file);
            const response = await api.post('/files/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return response.data;
        },
    });
}

export function useUpvoteComplaint() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (id: string) => {
            const response = await api.post(`/complaints/${id}/upvote`);
            return response.data;
        },
        onSuccess: (_, id) => {
            queryClient.invalidateQueries({ queryKey: ['complaints', id] });
            queryClient.invalidateQueries({ queryKey: ['complaints'] });
        },
    });
}

export function useVerifyResolution() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async ({ id, accepted, feedback }: { id: string; accepted: boolean; feedback?: string }) => {
            const response = await api.post(`/complaints/${id}/verify`, { accepted, feedback });
            return response.data;
        },
        onSuccess: (_, { id }) => {
            queryClient.invalidateQueries({ queryKey: ['complaints', id] });
            queryClient.invalidateQueries({ queryKey: ['complaints'] });
            toast.success('Resolution verification submitted');
        },
    });
}
export function useGeocode() {
    return useMutation({
        mutationFn: async (address: string) => {
            const response = await api.get('/geo/geocode', { params: { address } });
            return response.data;
        },
    });
}
