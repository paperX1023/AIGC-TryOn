export interface UserProfile {
    id: number
    username: string
    nickname?: string | null
    email?: string | null
    phone?: string | null
    avatar_url?: string | null
    gender?: string | null
    birthday?: string | null
    height_cm?: number | null
    weight_kg?: number | null
    preferred_styles: string[]
    bio?: string | null
    created_at: string
    updated_at: string
}

export interface BodyAnalysisRecord {
    id: number
    user_id: number
    image_path: string
    image_url: string
    gender: string
    body_shape: string
    shoulder_type: string
    waist_type: string
    leg_ratio: string
    analysis_summary: string
    created_at: string
}

export interface ChatSessionSummary {
    id: number
    session_id: string
    user_id?: number | null
    title?: string | null
    status: string
    latest_body_analysis_id?: number | null
    message_count: number
    created_at: string
    updated_at: string
}

export interface RecommendationRecord {
    id: number
    user_id: number
    chat_session_id?: number | null
    source: string
    input_summary: Record<string, unknown>
    recommend_result: {
        recommended_items?: string[]
        recommended_style_direction?: string
        reason?: string
        categorized_items?: {
            name: string
            category: string
            target_gender: string
        }[]
    }
    created_at: string
}

export interface TryOnRecord {
    id: number
    user_id?: number | null
    chat_session_id?: number | null
    body_analysis_record_id?: number | null
    person_image_path: string
    person_image_url: string
    cloth_image_path: string
    cloth_image_url: string
    result_image_path: string
    result_image_url: string
    status: string
    message: string
    source: string
    created_at: string
}

export interface UserDashboard {
    user: UserProfile
    latest_body_analysis?: BodyAnalysisRecord | null
    recent_chat_sessions: ChatSessionSummary[]
    recent_recommendations: RecommendationRecord[]
    recent_tryons: TryOnRecord[]
}

export interface AuthResponse {
    user: UserProfile
    access_token: string
    token_type: string
}

export interface RegisterPayload {
    username: string
    password: string
}

export interface LoginPayload {
    account: string
    password: string
}

export interface CreateUserPayload {
    username: string
    password?: string
    nickname?: string
    email?: string
    phone?: string
    avatar_url?: string
    gender?: string
    birthday?: string
    height_cm?: number
    weight_kg?: number
    preferred_styles: string[]
    bio?: string
}

export interface UpdateUserPayload {
    nickname?: string
    email?: string
    phone?: string
    avatar_url?: string
    gender?: string
    birthday?: string
    height_cm?: number
    weight_kg?: number
    preferred_styles?: string[]
    bio?: string
}
