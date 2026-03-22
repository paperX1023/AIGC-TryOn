import { Button, Card, Col, Empty, Image, Row, Space, Tag } from 'antd'
import PageContainer from '../../shared/components/PageContainer'
import { useAppStore } from '../../shared/store/useAppStore'

export default function HistoryPage() {
    const tryOnHistory = useAppStore((state) => state.tryOnHistory)
    const clearTryOnHistory = useAppStore((state) => state.clearTryOnHistory)

    return (
        <PageContainer
            title="历史记录"
            subtitle="查看过往试穿结果与生成记录。"
        >
            <Space direction="vertical" size={16} style={{ width: '100%' }}>
                <Button danger onClick={clearTryOnHistory} disabled={tryOnHistory.length === 0}>
                    清空试穿记录
                </Button>

                {tryOnHistory.length === 0 ? (
                    <Card style={{ borderRadius: 16 }}>
                        <Empty description="还没有试穿记录，先去虚拟试穿页生成一条结果。" />
                    </Card>
                ) : (
                    <Row gutter={[16, 16]}>
                        {tryOnHistory.map((item) => (
                            <Col xs={24} md={12} xl={8} key={item.id}>
                                <Card
                                    hoverable
                                    style={{ borderRadius: 16 }}
                                    cover={
                                        <Image
                                            src={item.resultImageUrl}
                                            alt="试穿结果"
                                            height={260}
                                            style={{ objectFit: 'cover' }}
                                            preview
                                        />
                                    }
                                >
                                    <Space direction="vertical" size={12} style={{ width: '100%' }}>
                                        <div>
                                            <Tag color={item.status === 'success' ? 'green' : 'orange'}>
                                                {item.status}
                                            </Tag>
                                            <span>{new Date(item.createdAt).toLocaleString()}</span>
                                        </div>
                                        <div>{item.message}</div>
                                        <Space size={12}>
                                            <Image src={item.personImageUrl} alt="人物图" width={72} height={96} />
                                            <Image src={item.clothImageUrl} alt="服装图" width={72} height={96} />
                                        </Space>
                                    </Space>
                                </Card>
                            </Col>
                        ))}
                    </Row>
                )}
            </Space>
        </PageContainer>
    )
}
