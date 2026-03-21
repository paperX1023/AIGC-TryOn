import { Button, Card, Col, Row, Space } from 'antd'
import { useNavigate } from 'react-router-dom'
import PageContainer from '../../shared/components/PageContainer'

export default function HomePage() {
    const navigate = useNavigate()

    return (
        <PageContainer
            title="基于 AIGC 的智能穿搭推荐与虚拟试穿系统"
            subtitle="结合体型分析、智能对话推荐与虚拟试穿，为用户提供完整的个性化穿搭体验。"
        >
            <Card style={{ borderRadius: 20, marginBottom: 24 }}>
                <Row gutter={[24, 24]} align="middle">
                    <Col xs={24} md={14}>
                        <Space direction="vertical" size={16}>
                            <h2 style={{ margin: 0, fontSize: 36, lineHeight: 1.3 }}>
                                让 AI 先理解你，再为你推荐穿搭并完成试穿
                            </h2>
                            <p style={{ margin: 0, color: '#666', fontSize: 16, lineHeight: 1.8 }}>
                                用户可先上传个人照片完成体型分析，再通过智能聊天获取风格建议，最后进入虚拟试穿模块查看生成结果。
                            </p>
                            <Space>
                                <Button type="primary" size="large" onClick={() => navigate('/analyze')}>
                                    开始智能体验
                                </Button>
                                <Button size="large" onClick={() => navigate('/tryon')}>
                                    快速试穿
                                </Button>
                            </Space>
                        </Space>
                    </Col>

                    <Col xs={24} md={10}>
                        <div
                            style={{
                                height: 320,
                                borderRadius: 20,
                                background: 'linear-gradient(135deg, #eef3ff 0%, #f7f9fc 100%)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: '#6b7280',
                                fontSize: 16,
                            }}
                        >
                            这里后续可放系统效果图 / 流程示意图
                        </div>
                    </Col>
                </Row>
            </Card>

            <Row gutter={[16, 16]}>
                <Col xs={24} md={8}>
                    <Card title="体型分析" style={{ borderRadius: 16 }}>
                        上传用户照片，识别体型特征，生成适合的穿搭方向与建议。
                    </Card>
                </Col>
                <Col xs={24} md={8}>
                    <Card title="智能推荐" style={{ borderRadius: 16 }}>
                        通过多轮聊天交互，根据用户需求生成个性化风格建议与服装推荐。
                    </Card>
                </Col>
                <Col xs={24} md={8}>
                    <Card title="虚拟试穿" style={{ borderRadius: 16 }}>
                        支持上传服装图片或选择推荐服装，一键生成试穿效果图。
                    </Card>
                </Col>
            </Row>
        </PageContainer>
    )
}