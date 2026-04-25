export interface ChatMessage {
    id: string
    role: 'user' | 'assistant'
    content: string
}

export interface ParsedStyleResult {
    styles: string[]
    scene: string
    goals: string[]
}

export interface RecommendResult {
    recommended_items: string[]
    categorized_items: {
        name: string
        category: string
        target_gender: string
    }[]
    recommended_style_direction: string
    reason: string
}

export interface ChatRequest {
    text: string
    user_id?: number
    session_id?: string
    body_context?: {
        gender: string
        body_shape: string
        shoulder_type: string
        waist_type: string
        leg_ratio: string
        analysis_summary: string
    } | null
}

export interface ChatResponse {
    reply: string
    session_id: string
    parsed_result: ParsedStyleResult
    recommend_result?: RecommendResult | null
}

export interface ChatStreamMeta {
    session_id: string
    parsed_result: ParsedStyleResult
    recommend_result?: RecommendResult | null
}

export interface ChatStreamChunk {
    content: string
}
