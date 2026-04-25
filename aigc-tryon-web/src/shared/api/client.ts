import axios from 'axios'
import { useAppStore } from '../store/useAppStore'

export const API_BASE_URL = 'http://127.0.0.1:8000/'

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000,
})

apiClient.interceptors.request.use((config) => {
    const token = useAppStore.getState().authToken

    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }

    return config
})

apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            useAppStore.getState().clearCurrentUser()
        }

        return Promise.reject(error)
    },
)
