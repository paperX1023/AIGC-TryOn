import { API_BASE_URL, apiClient } from '../../shared/api/client'
import { API_ENDPOINTS } from '../../shared/api/endpoints'
import { useAppStore } from '../../shared/store/useAppStore'
import type { ChatRequest, ChatResponse, ChatStreamChunk, ChatStreamMeta } from './types'

interface ChatStreamCallbacks {
    signal?: AbortSignal
    onSession?: (sessionId: string) => void
    onMeta?: (data: ChatStreamMeta) => void
    onChunk?: (data: ChatStreamChunk) => void
    onDone?: (data: ChatResponse) => void
}

interface SseMessage {
    event: string
    data: unknown
}

const buildApiUrl = (endpoint: string) => new URL(endpoint, API_BASE_URL).toString()

const isRecord = (value: unknown): value is Record<string, unknown> => {
    return typeof value === 'object' && value !== null
}

const parseSseMessage = (rawMessage: string): SseMessage | null => {
    let event = 'message'
    const dataLines: string[] = []

    rawMessage.split('\n').forEach((line) => {
        if (line.startsWith('event:')) {
            event = line.slice(6).trim()
        }

        if (line.startsWith('data:')) {
            dataLines.push(line.slice(5).trimStart())
        }
    })

    if (dataLines.length === 0) {
        return null
    }

    return {
        event,
        data: JSON.parse(dataLines.join('\n')),
    }
}

const readErrorMessage = async (response: Response) => {
    try {
        const payload = await response.clone().json() as { detail?: unknown }
        const detail = payload.detail

        if (typeof detail === 'string' && detail.trim()) {
            return detail
        }

        if (Array.isArray(detail)) {
            const message = detail
                .map((item) => isRecord(item) && typeof item.msg === 'string' ? item.msg : '')
                .filter(Boolean)
                .join('；')

            if (message) {
                return message
            }
        }
    } catch {
        const text = await response.text()

        if (text.trim()) {
            return text
        }
    }

    return `请求失败 (${response.status})`
}

const dispatchSseMessage = (message: SseMessage, callbacks: ChatStreamCallbacks) => {
    if (message.event === 'session') {
        if (isRecord(message.data) && typeof message.data.session_id === 'string') {
            callbacks.onSession?.(message.data.session_id)
        }
        return
    }

    if (message.event === 'meta') {
        callbacks.onMeta?.(message.data as ChatStreamMeta)
        return
    }

    if (message.event === 'chunk') {
        callbacks.onChunk?.(message.data as ChatStreamChunk)
        return
    }

    if (message.event === 'done') {
        callbacks.onDone?.(message.data as ChatResponse)
        return
    }

    if (message.event === 'error') {
        const errorMessage = isRecord(message.data) && typeof message.data.message === 'string'
            ? message.data.message
            : '生成推荐失败'
        throw new Error(errorMessage)
    }
}

export const sendChatMessage = async (payload: ChatRequest): Promise<ChatResponse> => {
    const res = await apiClient.post(API_ENDPOINTS.CHAT_RECOMMEND, payload)

    return {
        reply: res.data.reply || '已收到你的问题。',
        session_id: res.data.session_id,
        parsed_result: res.data.parsed_result,
        recommend_result: res.data.recommend_result,
    }
}

export const streamChatMessage = async (
    payload: ChatRequest,
    callbacks: ChatStreamCallbacks,
) => {
    const token = useAppStore.getState().authToken
    const headers: Record<string, string> = {
        Accept: 'text/event-stream',
        'Content-Type': 'application/json',
    }

    if (token) {
        headers.Authorization = `Bearer ${token}`
    }

    const response = await fetch(buildApiUrl(API_ENDPOINTS.CHAT_RECOMMEND_STREAM), {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
        signal: callbacks.signal,
    })

    if (!response.ok) {
        throw new Error(await readErrorMessage(response))
    }

    if (!response.body) {
        throw new Error('当前浏览器不支持流式响应')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
        const { value, done } = await reader.read()

        if (done) {
            break
        }

        buffer += decoder.decode(value, { stream: true })
        const messages = buffer.split('\n\n')
        buffer = messages.pop() ?? ''

        messages.forEach((rawMessage) => {
            const message = parseSseMessage(rawMessage)

            if (message) {
                dispatchSseMessage(message, callbacks)
            }
        })
    }

    buffer += decoder.decode()

    if (buffer.trim()) {
        const message = parseSseMessage(buffer)

        if (message) {
            dispatchSseMessage(message, callbacks)
        }
    }
}
