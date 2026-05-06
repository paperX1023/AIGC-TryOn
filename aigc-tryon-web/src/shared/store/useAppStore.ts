import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { BodyAnalysisResult } from '../../features/analyze/types'
import type { ChatMessage, ParsedStyleResult, RecommendResult } from '../../features/chat/types'
import type { TryOnResult } from '../../features/tryon/types'
import type { UserProfile } from '../../features/user/types'

const createInitialChatMessages = (): ChatMessage[] => [
    {
        id: 'init',
        role: 'assistant',
        content: '你好，我可以根据你的体型分析结果，为你推荐更适合的穿搭方向。',
    },
]

export interface TryOnHistoryItem {
    id: string
    userId: number | null
    createdAt: string
    personImageUrl: string
    clothImageUrl: string
    resultImageUrl: string
    status: string
    message: string
}

interface TryOnDraftState {
    selectedWardrobeItemId: string
    personPreviewUrl: string
    personDataUrl: string
    personFileName: string
    result: TryOnResult | null
}

interface AppState {
    currentUser: UserProfile | null
    authToken: string
    currentChatSessionId: string
    bodyAnalysis: BodyAnalysisResult | null
    chatMessages: ChatMessage[]
    chatParsedResult: ParsedStyleResult | null
    chatRecommendResult: RecommendResult | null
    tryOnDraft: TryOnDraftState
    tryOnHistory: TryOnHistoryItem[]
    setCurrentUser: (user: UserProfile | null) => void
    setAuthSession: (user: UserProfile, token: string) => void
    clearCurrentUser: () => void
    setCurrentChatSessionId: (sessionId: string) => void
    setBodyAnalysis: (data: BodyAnalysisResult | null) => void
    appendChatMessages: (messages: ChatMessage[]) => void
    updateChatMessage: (messageId: string, updater: string | ((content: string) => string)) => void
    setChatMeta: (parsedResult: ParsedStyleResult | null, recommendResult: RecommendResult | null) => void
    clearChatState: () => void
    setTryOnSelectedWardrobeItemId: (itemId: string) => void
    setTryOnPersonDraft: (previewUrl: string, dataUrl: string, fileName: string) => void
    setTryOnResult: (result: TryOnResult | null) => void
    clearTryOnDraft: () => void
    addTryOnHistory: (item: TryOnHistoryItem) => void
    clearTryOnHistory: () => void
}

export const useAppStore = create<AppState>()(
    persist(
        (set) => ({
            currentUser: null,
            authToken: '',
            currentChatSessionId: '',
            bodyAnalysis: null,
            chatMessages: createInitialChatMessages(),
            chatParsedResult: null,
            chatRecommendResult: null,
            tryOnDraft: {
                selectedWardrobeItemId: '',
                personPreviewUrl: '',
                personDataUrl: '',
                personFileName: '',
                result: null,
            },
            tryOnHistory: [],
            setCurrentUser: (user) => set({ currentUser: user }),
            setAuthSession: (user, token) =>
                set({
                    currentUser: user,
                    authToken: token,
                    currentChatSessionId: '',
                    bodyAnalysis: null,
                    chatMessages: createInitialChatMessages(),
                    chatParsedResult: null,
                    chatRecommendResult: null,
                    tryOnDraft: {
                        selectedWardrobeItemId: '',
                        personPreviewUrl: '',
                        personDataUrl: '',
                        personFileName: '',
                        result: null,
                    },
                }),
            clearCurrentUser: () =>
                set({
                    currentUser: null,
                    authToken: '',
                    currentChatSessionId: '',
                    bodyAnalysis: null,
                    chatMessages: createInitialChatMessages(),
                    chatParsedResult: null,
                    chatRecommendResult: null,
                    tryOnDraft: {
                        selectedWardrobeItemId: '',
                        personPreviewUrl: '',
                        personDataUrl: '',
                        personFileName: '',
                        result: null,
                    },
                }),
            setCurrentChatSessionId: (sessionId) => set({ currentChatSessionId: sessionId }),
            setBodyAnalysis: (data) => set({ bodyAnalysis: data }),
            appendChatMessages: (messages) =>
                set((state) => ({
                    chatMessages: [...state.chatMessages, ...messages],
                })),
            updateChatMessage: (messageId, updater) =>
                set((state) => ({
                    chatMessages: state.chatMessages.map((item) => {
                        if (item.id !== messageId) {
                            return item
                        }

                        return {
                            ...item,
                            content: typeof updater === 'function' ? updater(item.content) : updater,
                        }
                    }),
                })),
            setChatMeta: (parsedResult, recommendResult) =>
                set({
                    chatParsedResult: parsedResult,
                    chatRecommendResult: recommendResult,
                }),
            clearChatState: () =>
                set({
                    currentChatSessionId: '',
                    chatMessages: createInitialChatMessages(),
                    chatParsedResult: null,
                    chatRecommendResult: null,
                }),
            setTryOnSelectedWardrobeItemId: (itemId) =>
                set((state) => ({
                    tryOnDraft: {
                        ...state.tryOnDraft,
                        selectedWardrobeItemId: itemId,
                    },
                })),
            setTryOnPersonDraft: (previewUrl, dataUrl, fileName) =>
                set((state) => ({
                    tryOnDraft: {
                        ...state.tryOnDraft,
                        personPreviewUrl: previewUrl,
                        personDataUrl: dataUrl,
                        personFileName: fileName,
                    },
                })),
            setTryOnResult: (result) =>
                set((state) => ({
                    tryOnDraft: {
                        ...state.tryOnDraft,
                        result,
                    },
                })),
            clearTryOnDraft: () =>
                set((state) => ({
                    tryOnDraft: {
                        ...state.tryOnDraft,
                        personPreviewUrl: '',
                        personDataUrl: '',
                        personFileName: '',
                        result: null,
                    },
                })),
            addTryOnHistory: (item) =>
                set((state) => ({
                    tryOnHistory: [item, ...state.tryOnHistory].slice(0, 20),
                })),
            clearTryOnHistory: () => set({ tryOnHistory: [] }),
        }),
        {
            name: 'aigc-tryon-store',
        },
    ),
)
