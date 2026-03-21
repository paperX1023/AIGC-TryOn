import { createBrowserRouter } from 'react-router-dom'
import AppLayout from '../shared/components/Layout/AppLayout'
import HomePage from '../pages/Home'
import AnalyzePage from '../pages/Analyze'
import ChatPage from '../pages/Chat'
import TryOnPage from '../pages/TryOn'
import HistoryPage from '../pages/History'

const router = createBrowserRouter([
    {
        path: '/',
        element: <AppLayout />,
        children: [
            { index: true, element: <HomePage /> },
            { path: 'analyze', element: <AnalyzePage /> },
            { path: 'chat', element: <ChatPage /> },
            { path: 'tryon', element: <TryOnPage /> },
            { path: 'history', element: <HistoryPage /> },
        ],
    },
])

export default router