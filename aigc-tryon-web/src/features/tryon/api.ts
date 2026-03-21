import { apiClient } from '../../shared/api/client'
import { API_ENDPOINTS } from '../../shared/api/endpoints'
import type { TryOnResult } from './types'

export const createTryOn = async (personFile: File, clothFile: File): Promise<TryOnResult> => {
    const formData = new FormData()
    formData.append('person_file', personFile)
    formData.append('cloth_file', clothFile)

    const res = await apiClient.post(API_ENDPOINTS.TRY_ON, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    })

    return res.data
}
