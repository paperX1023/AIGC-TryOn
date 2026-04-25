import { useState } from 'react'
import { Alert, App, Button, Card, Col, Form, Input, Row, Segmented, Space, Typography } from 'antd'
import {
    ArrowRightOutlined,
    CameraOutlined,
    CheckCircleOutlined,
    HistoryOutlined,
    MessageOutlined,
    SafetyCertificateOutlined,
    SkinOutlined,
} from '@ant-design/icons'
import { useLocation, useNavigate } from 'react-router-dom'
import { loginUser, registerUser } from '../../features/user/api'
import { getApiErrorMessage } from '../../shared/api/errors'
import { useAppStore } from '../../shared/store/useAppStore'

type AuthMode = 'login' | 'register'

interface AuthFormValues {
    account: string
    password: string
    confirmPassword?: string
}

const { Paragraph, Text, Title } = Typography

const ACCOUNT_PATTERN = /^[a-zA-Z0-9_-]{2,64}$/

export default function HomePage() {
    const { message } = App.useApp()
    const [form] = Form.useForm<AuthFormValues>()
    const location = useLocation()
    const navigate = useNavigate()
    const currentUser = useAppStore((state) => state.currentUser)
    const authToken = useAppStore((state) => state.authToken)
    const setAuthSession = useAppStore((state) => state.setAuthSession)
    const [mode, setMode] = useState<AuthMode>('login')
    const [submitting, setSubmitting] = useState(false)
    const locationState = location.state as { authRequired?: boolean; redirectTo?: string } | null
    const redirectTo = locationState?.redirectTo && locationState.redirectTo !== '/'
        ? locationState.redirectTo
        : '/analyze'
    const featureCards = [
        {
            title: '体型分析',
            description: '上传照片，获取体型特征与穿搭方向。',
            path: '/analyze',
            icon: <CameraOutlined />,
        },
        {
            title: '智能推荐',
            description: '通过对话生成更适合你的搭配建议。',
            path: '/chat',
            icon: <MessageOutlined />,
        },
        {
            title: '虚拟试穿',
            description: '上传人物图和服装图，查看试穿效果。',
            path: '/tryon',
            icon: <SkinOutlined />,
        },
        {
            title: '历史记录',
            description: '回看已生成的试穿结果和使用记录。',
            path: '/history',
            icon: <HistoryOutlined />,
        },
    ]

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields()
            const account = values.account.trim()

            setSubmitting(true)
            const auth = mode === 'register'
                ? await registerUser({ username: account, password: values.password })
                : await loginUser({ account, password: values.password })

            setAuthSession(auth.user, auth.access_token)
            message.success(mode === 'register' ? '注册成功' : '登录成功')
            navigate(redirectTo, { replace: true })
        } catch (error) {
            if (typeof error === 'object' && error !== null && 'errorFields' in error) {
                return
            }

            message.error(getApiErrorMessage(
                error,
                mode === 'register' ? '注册失败，请检查账号是否已存在' : '登录失败，请检查账号或密码',
            ))
        } finally {
            setSubmitting(false)
        }
    }

    if (currentUser && authToken) {
        return (
            <div style={{ maxWidth: 1120, margin: '0 auto', padding: '28px 0' }}>
                <Card
                    style={{
                        borderRadius: 28,
                        marginBottom: 20,
                        border: '1px solid #edf0ea',
                        background: 'linear-gradient(135deg, #ffffff 0%, #f4f8ef 100%)',
                    }}
                    styles={{ body: { padding: '40px 36px' } }}
                >
                    <Row gutter={[24, 24]} align="middle">
                        <Col xs={24} md={16}>
                            <Space orientation="vertical" size={14}>
                                <Text type="secondary">工作台</Text>
                                <Title level={1} style={{ margin: 0, fontSize: 40 }}>
                                    开始你的智能穿搭流程
                                </Title>
                                <Paragraph style={{ margin: 0, color: '#667085', fontSize: 16, lineHeight: 1.8 }}>
                                    从体型分析到智能推荐，再到虚拟试穿，所有核心功能都在这里进入。
                                </Paragraph>
                            </Space>
                        </Col>
                        <Col xs={24} md={8} style={{ textAlign: 'right' }}>
                            <Button type="primary" size="large" onClick={() => navigate('/analyze')}>
                                开始体型分析
                            </Button>
                        </Col>
                    </Row>
                </Card>

                <Row gutter={[18, 18]}>
                    {featureCards.map((item) => (
                        <Col xs={24} md={12} xl={6} key={item.path}>
                            <Card
                                hoverable
                                onClick={() => navigate(item.path)}
                                style={{ height: '100%', borderRadius: 22, border: '1px solid #edf0ea' }}
                                styles={{ body: { minHeight: 210, display: 'flex', flexDirection: 'column' } }}
                            >
                                <Space orientation="vertical" size={16} style={{ height: '100%' }}>
                                    <div
                                        style={{
                                            width: 48,
                                            height: 48,
                                            borderRadius: 16,
                                            display: 'grid',
                                            placeItems: 'center',
                                            color: '#2f6b3f',
                                            background: '#eef6e9',
                                            fontSize: 24,
                                        }}
                                    >
                                        {item.icon}
                                    </div>
                                    <Title level={4} style={{ margin: 0 }}>
                                        {item.title}
                                    </Title>
                                    <Paragraph style={{ margin: 0, color: '#667085', lineHeight: 1.7 }}>
                                        {item.description}
                                    </Paragraph>
                                    <Button type="link" style={{ padding: 0, marginTop: 'auto' }}>
                                        进入功能 <ArrowRightOutlined />
                                    </Button>
                                </Space>
                            </Card>
                        </Col>
                    ))}
                </Row>
            </div>
        )
    }

    return (
        <div
            style={{
                minHeight: 'calc(100vh - 112px)',
                display: 'grid',
                placeItems: 'center',
            }}
        >
            <Card
                style={{
                    width: 'min(440px, 100%)',
                    borderRadius: 28,
                    border: '1px solid #edf0ea',
                    boxShadow: '0 24px 70px rgba(23, 42, 18, 0.08)',
                }}
                styles={{ body: { padding: 32 } }}
            >
                <Space orientation="vertical" size={24} style={{ width: '100%' }}>
                    <Space orientation="vertical" size={8} style={{ width: '100%', textAlign: 'center' }}>
                        <SafetyCertificateOutlined style={{ color: '#2f6b3f', fontSize: 28 }} />
                        <Text type="secondary">AIGC Try-On</Text>
                        <Title level={2} style={{ margin: 0 }}>登录后开始穿搭体验</Title>
                        <Paragraph style={{ margin: 0, color: '#667085' }}>
                            一个账号保存你的体型分析、推荐记录和试穿结果。
                        </Paragraph>
                    </Space>

                    {locationState?.authRequired ? (
                        <Alert type="warning" showIcon title="请先登录或注册后继续使用" />
                    ) : null}

                    <Segmented<AuthMode>
                        block
                        value={mode}
                        onChange={(value) => {
                            setMode(value)
                            form.resetFields()
                        }}
                        options={[
                            { label: '登录', value: 'login' },
                            { label: '注册', value: 'register' },
                        ]}
                    />

                    <Form<AuthFormValues> form={form} layout="vertical" requiredMark={false}>
                        <Form.Item
                            label={mode === 'register' ? '账号' : '账号 / 邮箱 / 手机号'}
                            name="account"
                            normalize={(value: string) => value?.trim()}
                            rules={[
                                { required: true, message: '请输入账号' },
                                {
                                    max: mode === 'register' ? 64 : 128,
                                    message: mode === 'register' ? '账号不能超过 64 位' : '登录账号不能超过 128 位',
                                },
                                {
                                    validator: (_, value?: string) => {
                                        if (mode === 'login' || !value || ACCOUNT_PATTERN.test(value)) {
                                            return Promise.resolve()
                                        }

                                        return Promise.reject(new Error('账号仅支持 2-64 位字母、数字、下划线或短横线'))
                                    },
                                },
                            ]}
                        >
                            <Input
                                size="large"
                                placeholder={mode === 'register' ? '请输入账号' : '请输入账号、邮箱或手机号'}
                                autoComplete="username"
                                maxLength={mode === 'register' ? 64 : 128}
                            />
                        </Form.Item>

                        <Form.Item
                            label="密码"
                            name="password"
                            rules={[
                                { required: true, message: '请输入密码' },
                                { min: mode === 'register' ? 6 : 1, message: '密码至少 6 位' },
                                {
                                    validator: (_, value?: string) => {
                                        if (!value || !/\s/.test(value)) {
                                            return Promise.resolve()
                                        }

                                        return Promise.reject(new Error('密码不能包含空格'))
                                    },
                                },
                            ]}
                        >
                            <Input.Password
                                size="large"
                                placeholder={mode === 'register' ? '至少 6 位密码' : '请输入密码'}
                                autoComplete={mode === 'register' ? 'new-password' : 'current-password'}
                                onPressEnter={handleSubmit}
                            />
                        </Form.Item>

                        {mode === 'register' ? (
                            <>
                                <Form.Item
                                    label="确认密码"
                                    name="confirmPassword"
                                    dependencies={['password']}
                                    rules={[
                                        { required: true, message: '请再次输入密码' },
                                        ({ getFieldValue }) => ({
                                            validator: (_, value?: string) => {
                                                if (!value || getFieldValue('password') === value) {
                                                    return Promise.resolve()
                                                }

                                                return Promise.reject(new Error('两次输入的密码不一致'))
                                            },
                                        }),
                                    ]}
                                >
                                    <Input.Password
                                        size="large"
                                        placeholder="请再次输入密码"
                                        autoComplete="new-password"
                                        onPressEnter={handleSubmit}
                                    />
                                </Form.Item>

                                <Alert
                                    type="info"
                                    showIcon
                                    icon={<CheckCircleOutlined />}
                                    title="密码用于保护你的个人资料与试穿记录"
                                    description="建议使用至少 6 位字符，不要包含空格，也不要与其他网站共用密码。"
                                />
                            </>
                        ) : null}

                        <Button
                            block
                            type="primary"
                            size="large"
                            loading={submitting}
                            onClick={handleSubmit}
                        >
                            {mode === 'register' ? '注册并登录' : '登录'}
                        </Button>
                    </Form>
                </Space>
            </Card>
        </div>
    )
}
