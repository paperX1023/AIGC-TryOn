import { apiClient } from '../../shared/api/client'
import { API_ENDPOINTS } from '../../shared/api/endpoints'
import type { TryOnResult } from './types'

interface CreateTryOnOptions {
    userId?: number
    sessionId?: string
    wardrobeItemId?: string
}

export const createTryOn = async (
    personFile: File,
    clothFile?: File | null,
    options: CreateTryOnOptions = {},
): Promise<TryOnResult> => {
    const formData = new FormData()
    formData.append('person_file', personFile)
    if (clothFile) {
        formData.append('cloth_file', clothFile)
    }
    if (options.wardrobeItemId) {
        formData.append('wardrobe_item_id', options.wardrobeItemId)
    }
    if (options.userId) {
        formData.append('user_id', String(options.userId))
    }
    if (options.sessionId) {
        formData.append('session_id', options.sessionId)
    }

    const res = await apiClient.post(API_ENDPOINTS.TRY_ON, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    })

    return res.data
}
