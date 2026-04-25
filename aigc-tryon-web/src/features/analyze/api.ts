import { apiClient } from '../../shared/api/client'
import { API_ENDPOINTS } from '../../shared/api/endpoints'
import type { BodyAnalysisResult } from './types'

export const analyzeBody = async (file: File, userId?: number): Promise<BodyAnalysisResult> => {
    const formData = new FormData()
    formData.append('file', file)
    if (userId) {
        formData.append('user_id', String(userId))
    }

    const res = await apiClient.post(API_ENDPOINTS.ANALYZE_BODY, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    })

    return res.data
}
