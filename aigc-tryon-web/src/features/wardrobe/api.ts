import { apiClient } from '../../shared/api/client'
import { API_ENDPOINTS } from '../../shared/api/endpoints'
import type { WardrobeItem, WardrobeListResponse } from './types'

interface ListWardrobeOptions {
    userId?: number
}

interface UploadWardrobeOptions {
    userId?: number
    name?: string
    category?: string
}

export const listWardrobeItems = async (options: ListWardrobeOptions = {}): Promise<WardrobeItem[]> => {
    const res = await apiClient.get<WardrobeListResponse>(API_ENDPOINTS.WARDROBE, {
        params: options.userId ? { user_id: options.userId } : undefined,
    })

    return res.data.items
}

export const uploadWardrobeItem = async (
    clothFile: File,
    options: UploadWardrobeOptions = {},
): Promise<WardrobeItem> => {
    const formData = new FormData()
    formData.append('cloth_file', clothFile)
    if (options.userId) {
        formData.append('user_id', String(options.userId))
    }
    if (options.name) {
        formData.append('name', options.name)
    }
    if (options.category) {
        formData.append('category', options.category)
    }

    const res = await apiClient.post<WardrobeItem>(API_ENDPOINTS.WARDROBE_UPLOAD, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    })

    return res.data
}
