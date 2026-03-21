import { apiClient } from './client'

export const resolveApiAssetUrl = (assetPath: string): string => {
    if (!assetPath) {
        return ''
    }

    return new URL(assetPath, apiClient.defaults.baseURL as string).toString()
}
