import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { BodyAnalysisResult } from '../../features/analyze/types'

export interface TryOnHistoryItem {
    id: string
    createdAt: string
    personImageUrl: string
    clothImageUrl: string
    resultImageUrl: string
    status: string
    message: string
}

interface AppState {
    bodyAnalysis: BodyAnalysisResult | null
    tryOnHistory: TryOnHistoryItem[]
    setBodyAnalysis: (data: BodyAnalysisResult | null) => void
    addTryOnHistory: (item: TryOnHistoryItem) => void
    clearTryOnHistory: () => void
}

export const useAppStore = create<AppState>()(
    persist(
        (set) => ({
            bodyAnalysis: null,
            tryOnHistory: [],
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
