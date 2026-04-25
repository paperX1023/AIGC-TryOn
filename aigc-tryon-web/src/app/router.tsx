import { createBrowserRouter } from 'react-router-dom'
import AppLayout from '../shared/components/Layout/AppLayout'
import HomePage from '../pages/Home'
import AnalyzePage from '../pages/Analyze'
import ChatPage from '../pages/Chat'
import TryOnPage from '../pages/TryOn'
import HistoryPage from '../pages/History'
import ProfilePage from '../pages/Profile'
import RequireUser from './RequireUser'

const router = createBrowserRouter([
    {
        path: '/',
        element: <AppLayout />,
        children: [
            { index: true, element: <HomePage /> },
            { path: 'analyze', element: <RequireUser><AnalyzePage /></RequireUser> },
            { path: 'chat', element: <RequireUser><ChatPage /></RequireUser> },
            { path: 'tryon', element: <RequireUser><TryOnPage /></RequireUser> },
            { path: 'history', element: <RequireUser><HistoryPage /></RequireUser> },
            { path: 'profile', element: <RequireUser><ProfilePage /></RequireUser> },
        ],
    },
])

export default router
