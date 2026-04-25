import { useEffect } from 'react'
import { Layout, Button, Space } from 'antd'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { getCurrentUser } from '../../../features/user/api'
import { useAppStore } from '../../store/useAppStore'

const { Header, Content } = Layout

const navItems = [
    { path: '/', label: '首页' },
    { path: '/analyze', label: '体型分析' },
    { path: '/chat', label: '智能推荐' },
    { path: '/tryon', label: '虚拟试穿' },
    { path: '/history', label: '历史记录' },
    { path: '/profile', label: '个人中心' },
]

export default function AppLayout() {
    const location = useLocation()
    const navigate = useNavigate()
    const currentUser = useAppStore((state) => state.currentUser)
    const authToken = useAppStore((state) => state.authToken)
    const setCurrentUser = useAppStore((state) => state.setCurrentUser)
    const clearCurrentUser = useAppStore((state) => state.clearCurrentUser)
    const isAuthenticated = Boolean(currentUser && authToken)

    useEffect(() => {
        if (!authToken) {
            return
        }

        let cancelled = false

        const syncCurrentUser = async () => {
            try {
                const user = await getCurrentUser()

                if (!cancelled) {
                    setCurrentUser(user)
                }
            } catch {
                if (!cancelled) {
                    clearCurrentUser()
                    navigate('/', { replace: true })
                }
            }
        }

        void syncCurrentUser()

        return () => {
            cancelled = true
        }
    }, [authToken, clearCurrentUser, navigate, setCurrentUser])

    return (
        <Layout style={{ minHeight: '100vh', background: '#f5f7fb' }}>
            <Header
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    background: '#ffffff',
                    borderBottom: '1px solid #eef1f5',
                    padding: '0 24px',
                    position: 'sticky',
                    top: 0,
                    zIndex: 10,
                }}
            >
                <div
                    onClick={() => navigate('/')}
                    style={{
                        fontSize: 20,
                        fontWeight: 700,
                        color: '#1f1f1f',
                        cursor: 'pointer',
                        userSelect: 'none',
                    }}
                >
                    AIGC 智能穿搭系统
                </div>

                {isAuthenticated && currentUser ? (
                    <Space size={8} wrap>
                        {navItems.map((item) => (
                            <Button
                                key={item.path}
                                type={location.pathname === item.path ? 'primary' : 'text'}
                                onClick={() => navigate(item.path)}
                            >
                                {item.label}
                            </Button>
                        ))}
                    </Space>
                ) : null}
            </Header>

            <Content style={{ padding: '24px' }}>
                <Outlet />
            </Content>
        </Layout>
    )
}
