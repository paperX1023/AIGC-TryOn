import { apiClient } from '../../shared/api/client'
import { API_ENDPOINTS } from '../../shared/api/endpoints'
import type {
    AuthResponse,
    CreateUserPayload,
    LoginPayload,
    RegisterPayload,
    UpdateUserPayload,
    UserDashboard,
    UserProfile,
} from './types'

export const registerUser = async (payload: RegisterPayload): Promise<AuthResponse> => {
    const res = await apiClient.post(API_ENDPOINTS.AUTH_REGISTER, payload)
    return res.data
}

export const loginUser = async (payload: LoginPayload): Promise<AuthResponse> => {
    const res = await apiClient.post(API_ENDPOINTS.AUTH_LOGIN, payload)
    return res.data
}

export const getCurrentUser = async (): Promise<UserProfile> => {
    const res = await apiClient.get(API_ENDPOINTS.AUTH_ME)
    return res.data
}

export const listUsers = async (): Promise<UserProfile[]> => {
    const res = await apiClient.get(API_ENDPOINTS.USERS)
    return res.data
}

export const createUser = async (payload: CreateUserPayload): Promise<UserProfile> => {
    const res = await apiClient.post(API_ENDPOINTS.USERS, payload)
    return res.data
}

export const updateUser = async (userId: number, payload: UpdateUserPayload): Promise<UserProfile> => {
    const res = await apiClient.patch(API_ENDPOINTS.USER_DETAIL(userId), payload)
    return res.data
}

export const getUserDashboard = async (userId: number): Promise<UserDashboard> => {
    const res = await apiClient.get(API_ENDPOINTS.USER_DASHBOARD(userId))
    return res.data
}

export const getMyDashboard = async (): Promise<UserDashboard> => {
    const res = await apiClient.get(API_ENDPOINTS.USER_ME_DASHBOARD)
    return res.data
}
