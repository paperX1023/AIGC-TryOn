import { apiClient } from '../../shared/api/client'
import { API_ENDPOINTS } from '../../shared/api/endpoints'
import type { ChatRequest, ChatResponse } from './types'

export const sendChatMessage = async (payload: ChatRequest): Promise<ChatResponse> => {
    const res = await apiClient.post(API_ENDPOINTS.CHAT_RECOMMEND, payload)

    return {
        reply: res.data.reply || '已收到你的问题。',
        session_id: res.data.session_id,
        parsed_result: res.data.parsed_result,
        recommend_result: res.data.recommend_result,
    }
}
