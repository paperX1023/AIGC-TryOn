import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAppStore } from '../shared/store/useAppStore'

export default function RequireUser({ children }: { children: ReactNode }) {
    const currentUser = useAppStore((state) => state.currentUser)
    const authToken = useAppStore((state) => state.authToken)
    const location = useLocation()

    if (!currentUser || !authToken) {
        return (
            <Navigate
                to="/"
                replace
                state={{ authRequired: true, redirectTo: location.pathname }}
            />
        )
    }

    return children
}
