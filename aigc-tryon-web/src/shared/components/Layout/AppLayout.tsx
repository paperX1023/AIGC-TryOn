import { Layout, Menu, Button } from 'antd'
import {
    HomeOutlined,
    CameraOutlined,
    MessageOutlined,
    SkinOutlined,
    HistoryOutlined,
} from '@ant-design/icons'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'

const { Header, Content } = Layout

const menuItems = [
    { key: '/', icon: <HomeOutlined />, label: '首页' },
    { key: '/analyze', icon: <CameraOutlined />, label: '体型分析' },
    { key: '/chat', icon: <MessageOutlined />, label: '智能推荐' },
    { key: '/tryon', icon: <SkinOutlined />, label: '虚拟试穿' },
    { key: '/history', icon: <HistoryOutlined />, label: '历史记录' },
]

export default function AppLayout() {
    const location = useLocation()
    const navigate = useNavigate()

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
                <div style={{ fontSize: 20, fontWeight: 700, color: '#1f1f1f' }}>
                    AIGC 智能穿搭系统
                </div>

                <Menu
                    mode="horizontal"
                    selectedKeys={[location.pathname]}
                    items={menuItems}
                    onClick={({ key }) => navigate(key)}
                    style={{ flex: 1, minWidth: 0, marginLeft: 32, borderBottom: 'none' }}
                />

                <Button type="primary" onClick={() => navigate('/tryon')}>
                    开始体验
                </Button>
            </Header>

            <Content style={{ padding: '24px' }}>
                <Outlet />
            </Content>
        </Layout>
    )
}