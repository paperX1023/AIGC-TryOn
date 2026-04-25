import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    App,
    Button,
    Card,
    Col,
    Descriptions,
    Empty,
    Form,
    Input,
    InputNumber,
    List,
    Row,
    Select,
    Space,
    Statistic,
    Tag,
    Typography,
} from 'antd'
import PageContainer from '../../shared/components/PageContainer'
import { getMyDashboard, updateUser } from '../../features/user/api'
import type { UpdateUserPayload, UserDashboard, UserProfile } from '../../features/user/types'
import { getApiErrorMessage } from '../../shared/api/errors'
import { useAppStore } from '../../shared/store/useAppStore'
import type { BodyAnalysisResult } from '../../features/analyze/types'
import { resolveApiAssetUrl } from '../../shared/api/assets'

interface ProfileFormValues {
    nickname?: string
    email?: string
    phone?: string
    gender?: string
    height_cm?: number
    weight_kg?: number
    preferred_styles?: string[]
    bio?: string
}

const STYLE_OPTIONS = ['韩系', '简约', '通勤', '甜美', '休闲', '中国风']
const GENDER_OPTIONS = ['男', '女', '中性', '未知']

type ProfileFormInstance = ReturnType<typeof Form.useForm<ProfileFormValues>>[0]

function toBodyAnalysisResult(
    latestBodyAnalysis: UserDashboard['latest_body_analysis'],
): BodyAnalysisResult | null {
    if (!latestBodyAnalysis) {
        return null
    }

    return {
        record_id: latestBodyAnalysis.id,
        gender: latestBodyAnalysis.gender,
        body_shape: latestBodyAnalysis.body_shape,
        shoulder_type: latestBodyAnalysis.shoulder_type,
        waist_type: latestBodyAnalysis.waist_type,
        leg_ratio: latestBodyAnalysis.leg_ratio,
        analysis_summary: latestBodyAnalysis.analysis_summary,
        image_path: latestBodyAnalysis.image_path,
        image_url: latestBodyAnalysis.image_url,
    }
}

function applyUserToForm(form: ProfileFormInstance, user: UserProfile) {
    form.setFieldsValue({
        nickname: user.nickname || undefined,
        email: user.email || undefined,
        phone: user.phone || undefined,
        gender: user.gender || undefined,
        height_cm: user.height_cm ?? undefined,
        weight_kg: user.weight_kg ?? undefined,
        preferred_styles: user.preferred_styles || [],
        bio: user.bio || undefined,
    })
}

function toUpdatePayload(values: ProfileFormValues): UpdateUserPayload {
    return {
        nickname: values.nickname?.trim() || undefined,
        email: values.email?.trim() || undefined,
        phone: values.phone?.trim() || undefined,
        gender: values.gender || undefined,
        height_cm: values.height_cm ?? undefined,
        weight_kg: values.weight_kg ?? undefined,
        preferred_styles: values.preferred_styles || [],
        bio: values.bio?.trim() || undefined,
    }
}

export default function ProfilePage() {
    const { message } = App.useApp()
    const [form] = Form.useForm<ProfileFormValues>()
    const navigate = useNavigate()
    const currentUser = useAppStore((state) => state.currentUser)
    const setCurrentUser = useAppStore((state) => state.setCurrentUser)
    const clearCurrentUser = useAppStore((state) => state.clearCurrentUser)
    const setBodyAnalysis = useAppStore((state) => state.setBodyAnalysis)
    const [dashboard, setDashboard] = useState<UserDashboard | null>(null)
    const [loadingDashboard, setLoadingDashboard] = useState(false)
    const [submitting, setSubmitting] = useState(false)

    useEffect(() => {
        if (currentUser) {
            applyUserToForm(form, currentUser)
        }
    }, [currentUser, form])

    useEffect(() => {
        const run = async () => {
            try {
                setLoadingDashboard(true)
                const data = await getMyDashboard()
                setDashboard(data)
                setCurrentUser(data.user)
                setBodyAnalysis(toBodyAnalysisResult(data.latest_body_analysis))
            } catch (error) {
                message.error(getApiErrorMessage(error, '获取个人中心数据失败'))
            } finally {
                setLoadingDashboard(false)
            }
        }

        void run()
    }, [message, setBodyAnalysis, setCurrentUser])

    const handleSave = async () => {
        if (!currentUser) {
            return
        }

        try {
            const values = await form.validateFields()
            setSubmitting(true)
            const updatedUser = await updateUser(currentUser.id, toUpdatePayload(values))
            setCurrentUser(updatedUser)
            setDashboard((prev) => (prev ? { ...prev, user: updatedUser } : prev))
            message.success('个人资料已保存')
        } catch (error) {
            if (typeof error === 'object' && error !== null && 'errorFields' in error) {
                return
            }

            message.error(getApiErrorMessage(error, '保存失败，请稍后重试'))
        } finally {
            setSubmitting(false)
        }
    }

    return (
        <PageContainer
            title="个人中心"
            subtitle="账号密码用于登录，身高体重、风格偏好等资料可在这里随时完善。"
        >
            <Space orientation="vertical" size={16} style={{ width: '100%' }}>
                <Row gutter={[24, 24]}>
                    <Col xs={24} xl={10}>
                        <Card title="资料设置" style={{ borderRadius: 18 }}>
                            <Form<ProfileFormValues> form={form} layout="vertical" requiredMark={false}>
                                <Row gutter={12}>
                                    <Col span={12}>
                                        <Form.Item label="昵称" name="nickname">
                                            <Input placeholder="例如：小王" />
                                        </Form.Item>
                                    </Col>
                                    <Col span={12}>
                                        <Form.Item label="性别" name="gender">
                                            <Select
                                                allowClear
                                                placeholder="选择性别"
                                                options={GENDER_OPTIONS.map((item) => ({ value: item, label: item }))}
                                            />
                                        </Form.Item>
                                    </Col>
                                </Row>

                                <Row gutter={12}>
                                    <Col span={12}>
                                        <Form.Item label="邮箱" name="email">
                                            <Input placeholder="可选" />
                                        </Form.Item>
                                    </Col>
                                    <Col span={12}>
                                        <Form.Item label="手机号" name="phone">
                                            <Input placeholder="可选" />
                                        </Form.Item>
                                    </Col>
                                </Row>

                                <Row gutter={12}>
                                    <Col span={12}>
                                        <Form.Item label="身高（cm）" name="height_cm">
                                            <InputNumber style={{ width: '100%' }} min={0} placeholder="可选" />
                                        </Form.Item>
                                    </Col>
                                    <Col span={12}>
                                        <Form.Item label="体重（kg）" name="weight_kg">
                                            <InputNumber style={{ width: '100%' }} min={0} placeholder="可选" />
                                        </Form.Item>
                                    </Col>
                                </Row>

                                <Form.Item label="风格偏好" name="preferred_styles">
                                    <Select
                                        mode="multiple"
                                        allowClear
                                        placeholder="选择偏好的穿搭风格"
                                        options={STYLE_OPTIONS.map((item) => ({ value: item, label: item }))}
                                    />
                                </Form.Item>

                                <Form.Item label="个人简介" name="bio">
                                    <Input.TextArea rows={4} placeholder="例如：偏爱通勤、简约、韩系日常穿搭" />
                                </Form.Item>

                                <Space>
                                    <Button type="primary" loading={submitting} onClick={handleSave}>
                                        保存资料
                                    </Button>
                                    <Button
                                        onClick={() => {
                                            clearCurrentUser()
                                            navigate('/', { replace: true })
                                        }}
                                    >
                                        退出登录
                                    </Button>
                                </Space>
                            </Form>
                        </Card>
                    </Col>

                    <Col xs={24} xl={14}>
                        <Space orientation="vertical" size={16} style={{ width: '100%' }}>
                            <Card title="账号信息" style={{ borderRadius: 18 }}>
                                {currentUser ? (
                                    <Descriptions bordered column={1} size="small">
                                        <Descriptions.Item label="用户 ID">{currentUser.id}</Descriptions.Item>
                                        <Descriptions.Item label="账号">{currentUser.username}</Descriptions.Item>
                                        <Descriptions.Item label="昵称">{currentUser.nickname || '未填写'}</Descriptions.Item>
                                        <Descriptions.Item label="身高">
                                            {currentUser.height_cm ? `${currentUser.height_cm} cm` : '未填写'}
                                        </Descriptions.Item>
                                        <Descriptions.Item label="体重">
                                            {currentUser.weight_kg ? `${currentUser.weight_kg} kg` : '未填写'}
                                        </Descriptions.Item>
                                        <Descriptions.Item label="偏好风格">
                                            {currentUser.preferred_styles.length > 0 ? (
                                                <Space wrap>
                                                    {currentUser.preferred_styles.map((item) => (
                                                        <Tag key={item}>{item}</Tag>
                                                    ))}
                                                </Space>
                                            ) : (
                                                '未填写'
                                            )}
                                        </Descriptions.Item>
                                    </Descriptions>
                                ) : (
                                    <Empty description="暂无登录用户" />
                                )}
                            </Card>

                            <Row gutter={[16, 16]}>
                                <Col xs={24} md={8}>
                                    <Card style={{ borderRadius: 18 }} loading={loadingDashboard}>
                                        <Statistic title="聊天会话" value={dashboard?.recent_chat_sessions.length || 0} />
                                    </Card>
                                </Col>
                                <Col xs={24} md={8}>
                                    <Card style={{ borderRadius: 18 }} loading={loadingDashboard}>
                                        <Statistic title="推荐记录" value={dashboard?.recent_recommendations.length || 0} />
                                    </Card>
                                </Col>
                                <Col xs={24} md={8}>
                                    <Card style={{ borderRadius: 18 }} loading={loadingDashboard}>
                                        <Statistic title="试穿记录" value={dashboard?.recent_tryons.length || 0} />
                                    </Card>
                                </Col>
                            </Row>
                        </Space>
                    </Col>
                </Row>

                <Row gutter={[24, 24]}>
                    <Col xs={24} xl={8}>
                        <Card title="最近体型分析" style={{ borderRadius: 18 }} loading={loadingDashboard}>
                            {dashboard?.latest_body_analysis ? (
                                <Space orientation="vertical" size={12} style={{ width: '100%' }}>
                                    <Space wrap>
                                        <Tag color="magenta">{dashboard.latest_body_analysis.gender}</Tag>
                                        <Tag color="purple">{dashboard.latest_body_analysis.body_shape}</Tag>
                                        <Tag>{dashboard.latest_body_analysis.shoulder_type}肩</Tag>
                                        <Tag>{dashboard.latest_body_analysis.waist_type}腰</Tag>
                                        <Tag>{dashboard.latest_body_analysis.leg_ratio}</Tag>
                                    </Space>
                                    <Typography.Paragraph style={{ marginBottom: 0 }}>
                                        {dashboard.latest_body_analysis.analysis_summary}
                                    </Typography.Paragraph>
                                </Space>
                            ) : (
                                <Empty description="还没有体型分析记录" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                            )}
                        </Card>
                    </Col>

                    <Col xs={24} xl={8}>
                        <Card title="最近聊天会话" style={{ borderRadius: 18 }} loading={loadingDashboard}>
                            {dashboard && dashboard.recent_chat_sessions.length > 0 ? (
                                <List
                                    dataSource={dashboard.recent_chat_sessions}
                                    renderItem={(item) => (
                                        <List.Item>
                                            <List.Item.Meta
                                                title={item.title || '未命名会话'}
                                                description={`消息数：${item.message_count}`}
                                            />
                                        </List.Item>
                                    )}
                                />
                            ) : (
                                <Empty description="还没有聊天会话" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                            )}
                        </Card>
                    </Col>

                    <Col xs={24} xl={8}>
                        <Card title="最近试穿记录" style={{ borderRadius: 18 }} loading={loadingDashboard}>
                            {dashboard && dashboard.recent_tryons.length > 0 ? (
                                <Space orientation="vertical" size={12} style={{ width: '100%' }}>
                                    {dashboard.recent_tryons.slice(0, 2).map((item) => (
                                        <Card key={item.id} size="small">
                                            <Space orientation="vertical" size={8} style={{ width: '100%' }}>
                                                <img
                                                    src={resolveApiAssetUrl(item.result_image_url)}
                                                    alt="试穿结果缩略图"
                                                    style={{
                                                        width: '100%',
                                                        height: 160,
                                                        objectFit: 'cover',
                                                        borderRadius: 10,
                                                    }}
                                                />
                                                <Space>
                                                    <Tag color={item.status === 'success' ? 'green' : 'orange'}>
                                                        {item.status}
                                                    </Tag>
                                                    <Typography.Text type="secondary">
                                                        {new Date(item.created_at).toLocaleString()}
                                                    </Typography.Text>
                                                </Space>
                                            </Space>
                                        </Card>
                                    ))}
                                </Space>
                            ) : (
                                <Empty description="还没有试穿记录" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                            )}
                        </Card>
                    </Col>
                </Row>
            </Space>
        </PageContainer>
    )
}
