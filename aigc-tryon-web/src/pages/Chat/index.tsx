import { useState } from 'react'
import { Button, Card, Col, Input, Row, Space, Tag, message } from 'antd'
import PageContainer from '../../shared/components/PageContainer'
import { useAppStore } from '../../shared/store/useAppStore'
import { sendChatMessage } from '../../features/chat/api'
import type { ChatMessage, ParsedStyleResult, RecommendResult } from '../../features/chat/types'

export default function ChatPage() {
    const bodyAnalysis = useAppStore((state) => state.bodyAnalysis)

    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [sessionId, setSessionId] = useState<string>('')
    const [parsedResult, setParsedResult] = useState<ParsedStyleResult | null>(null)
    const [recommendResult, setRecommendResult] = useState<RecommendResult | null>(null)
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            id: 'init',
            role: 'assistant',
            content: '你好，我可以根据你的体型分析结果，为你推荐更适合的穿搭方向。',
        },
    ])

    const handleSend = async () => {
        const text = input.trim()
        if (!text) {
            message.warning('请输入你的问题')
            return
        }

        const userMessage: ChatMessage = {
            id: `${Date.now()}-user`,
            role: 'user',
            content: text,
        }

        setMessages((prev) => [...prev, userMessage])
        setInput('')

        try {
            setLoading(true)

            const res = await sendChatMessage({
                text: text,
                session_id: sessionId || undefined,
                body_context: bodyAnalysis
                    ? {
                        gender: bodyAnalysis.gender,
                        body_shape: bodyAnalysis.body_shape,
                        shoulder_type: bodyAnalysis.shoulder_type,
                        waist_type: bodyAnalysis.waist_type,
                        leg_ratio: bodyAnalysis.leg_ratio,
                        analysis_summary: bodyAnalysis.analysis_summary,
                    }
                    : null,
            })

            setSessionId(res.session_id)
            setParsedResult(res.parsed_result)
            setRecommendResult(res.recommend_result ?? null)

            const assistantMessage: ChatMessage = {
                id: `${Date.now()}-assistant`,
                role: 'assistant',
                content: res.reply,
            }

            setMessages((prev) => [...prev, assistantMessage])
        } catch (error) {
            console.error(error)
            message.error('发送失败，请检查聊天接口')
        } finally {
            setLoading(false)
        }
    }

    return (
        <PageContainer
            title="智能推荐"
            subtitle="通过自然语言对话获取个性化穿搭建议。"
        >
            <Row gutter={[24, 24]}>
                <Col xs={24} lg={16}>
                    <Card title="智能穿搭助手" style={{ borderRadius: 16 }}>
                        <div
                            style={{
                                height: 420,
                                borderRadius: 12,
                                background: '#fafafa',
                                padding: 16,
                                marginBottom: 16,
                                overflow: 'auto',
                                display: 'flex',
                                flexDirection: 'column',
                                gap: 12,
                            }}
                        >
                            {messages.map((item) => (
                                <div
                                    key={item.id}
                                    style={{
                                        alignSelf: item.role === 'user' ? 'flex-end' : 'flex-start',
                                        maxWidth: '78%',
                                        padding: '12px 14px',
                                        borderRadius: 14,
                                        background: item.role === 'user' ? '#1677ff' : '#ffffff',
                                        color: item.role === 'user' ? '#ffffff' : '#1f1f1f',
                                        border: item.role === 'assistant' ? '1px solid #f0f0f0' : 'none',
                                        whiteSpace: 'pre-wrap',
                                        lineHeight: 1.7,
                                    }}
                                >
                                    {item.content}
                                </div>
                            ))}
                        </div>

                        <Space.Compact style={{ width: '100%' }}>
                            <Input
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onPressEnter={handleSend}
                                placeholder="请输入你的穿搭需求，例如：我想显高一点，适合什么搭配？"
                            />
                            <Button type="primary" loading={loading} onClick={handleSend}>
                                发送
                            </Button>
                        </Space.Compact>
                    </Card>
                </Col>

                <Col xs={24} lg={8}>
                    <Space direction="vertical" size={16} style={{ width: '100%' }}>
                        <Card title="用户体型摘要" style={{ borderRadius: 16 }}>
                            {bodyAnalysis ? (
                                <Space wrap>
                                    <Tag color="magenta">{bodyAnalysis.gender}</Tag>
                                    <Tag color="purple">{bodyAnalysis.body_shape}</Tag>
                                    <Tag>{bodyAnalysis.shoulder_type}肩</Tag>
                                    <Tag>{bodyAnalysis.waist_type}腰型</Tag>
                                    <Tag>{bodyAnalysis.leg_ratio}</Tag>
                                </Space>
                            ) : (
                                '暂无体型分析结果，建议先前往“体型分析”页面完成分析。'
                            )}
                        </Card>

                        <Card title="当前推荐关键词" style={{ borderRadius: 16 }}>
                            {parsedResult ? (
                                <Space wrap>
                                    {parsedResult.styles.map((item) => (
                                        <Tag key={item}>{item}</Tag>
                                    ))}
                                    <Tag color="blue">{parsedResult.scene}</Tag>
                                    {parsedResult.goals.map((item) => (
                                        <Tag color="green" key={item}>
                                            {item}
                                        </Tag>
                                    ))}
                                </Space>
                            ) : (
                                '发送消息后，这里会展示本轮识别到的风格、场景与目标。'
                            )}
                        </Card>

                        <Card title="推荐摘要" style={{ borderRadius: 16 }}>
                            {recommendResult ? (
                                <Space direction="vertical" size={8} style={{ width: '100%' }}>
                                    <Tag color="gold">{recommendResult.recommended_style_direction}</Tag>
                                    {recommendResult.categorized_items.map((item) => (
                                        <div key={`${item.category}-${item.name}`}>
                                            {item.category}：{item.name}（{item.target_gender}）
                                        </div>
                                    ))}
                                </Space>
                            ) : (
                                '暂无推荐摘要；若未完成人体分析，系统会先返回需求解析结果。'
                            )}
                        </Card>

                        <Card title="会话信息" style={{ borderRadius: 16 }}>
                            {sessionId || '当前为新会话，发送消息后将记录 session_id。'}
                        </Card>
                    </Space>
                </Col>
            </Row>
        </PageContainer>
    )
}
