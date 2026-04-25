export interface WardrobeDetectionResult {
    passed: boolean
    score: number
    message: string
    checks: Record<string, boolean>
}

export interface WardrobeItem {
    id: string
    numeric_id?: number | null
    user_id?: number | null
    name: string
    category: string
    image_path: string
    image_url: string
    source: 'default' | 'user' | 'uploaded'
    detection_result?: WardrobeDetectionResult | null
    created_at?: string | null
}

export interface WardrobeListResponse {
    items: WardrobeItem[]
}
