import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { BodyAnalysisResult } from '../../features/analyze/types'
import type { UserProfile } from '../../features/user/types'

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

interface AppState {
    currentUser: UserProfile | null
    authToken: string
    currentChatSessionId: string
    bodyAnalysis: BodyAnalysisResult | null
    tryOnHistory: TryOnHistoryItem[]
    setCurrentUser: (user: UserProfile | null) => void
    setAuthSession: (user: UserProfile, token: string) => void
    clearCurrentUser: () => void
    setCurrentChatSessionId: (sessionId: string) => void
    setBodyAnalysis: (data: BodyAnalysisResult | null) => void
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
            tryOnHistory: [],
            setCurrentUser: (user) => set({ currentUser: user }),
            setAuthSession: (user, token) =>
                set({
                    currentUser: user,
                    authToken: token,
                    currentChatSessionId: '',
                    bodyAnalysis: null,
                }),
            clearCurrentUser: () =>
                set({
                    currentUser: null,
                    authToken: '',
                    currentChatSessionId: '',
                    bodyAnalysis: null,
                }),
            setCurrentChatSessionId: (sessionId) => set({ currentChatSessionId: sessionId }),
            setBodyAnalysis: (data) => set({ bodyAnalysis: data }),
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
