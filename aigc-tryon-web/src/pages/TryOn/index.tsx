import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { App, Button, Card, Col, Empty, Image, Row, Space, Spin, Tag, Tooltip, Typography, Upload } from 'antd'
import {
    CheckCircleOutlined,
    CloudUploadOutlined,
    ReloadOutlined,
    SkinOutlined,
    UploadOutlined,
} from '@ant-design/icons'
import { createTryOn } from '../../features/tryon/api'
import type { TryOnResult } from '../../features/tryon/types'
import { listWardrobeItems, uploadWardrobeItem } from '../../features/wardrobe/api'
import type { WardrobeItem } from '../../features/wardrobe/types'
import PageContainer from '../../shared/components/PageContainer'
import { getApiErrorMessage } from '../../shared/api/errors'
import { resolveApiAssetUrl } from '../../shared/api/assets'
import { useAppStore } from '../../shared/store/useAppStore'

const { Text } = Typography

function getWardrobeSourceLabel(source: WardrobeItem['source']) {
    if (source === 'user') {
        return { color: 'green', label: '我的' }
    }
    if (source === 'uploaded') {
        return { color: 'blue', label: '临时' }
    }
    return { color: 'gold', label: '初始' }
}

function getUploadDisplayName(fileName: string) {
    return fileName.replace(/\.[^.]+$/, '').trim() || '上传服装'
}

export default function TryOnPage() {
    const { message } = App.useApp()
    const currentUser = useAppStore((state) => state.currentUser)
    const bodyAnalysis = useAppStore((state) => state.bodyAnalysis)
    const currentChatSessionId = useAppStore((state) => state.currentChatSessionId)
    const addTryOnHistory = useAppStore((state) => state.addTryOnHistory)
    const sessionClothFilesRef = useRef<Map<string, File>>(new Map())
    const [personFile, setPersonFile] = useState<File | null>(null)
    const [personPreview, setPersonPreview] = useState('')
    const [wardrobeItems, setWardrobeItems] = useState<WardrobeItem[]>([])
    const [selectedWardrobeItemId, setSelectedWardrobeItemId] = useState('')
    const [result, setResult] = useState<TryOnResult | null>(null)
    const [loading, setLoading] = useState(false)
    const [wardrobeLoading, setWardrobeLoading] = useState(false)
    const [uploadingWardrobe, setUploadingWardrobe] = useState(false)

    const selectedWardrobeItem = useMemo(
        () => wardrobeItems.find((item) => item.id === selectedWardrobeItemId) || null,
        [selectedWardrobeItemId, wardrobeItems],
    )

    const loadWardrobe = useCallback(async () => {
        try {
            setWardrobeLoading(true)
            const items = await listWardrobeItems({ userId: currentUser?.id })
            setWardrobeItems(items)
            setSelectedWardrobeItemId((prev) => (
                items.some((item) => item.id === prev) ? prev : items[0]?.id || ''
            ))
        } catch (error) {
            message.error(getApiErrorMessage(error, '获取服装库失败'))
        } finally {
            setWardrobeLoading(false)
        }
    }, [currentUser?.id, message])

    useEffect(() => {
        void loadWardrobe()
    }, [loadWardrobe])

    const handleSelectPerson = (file: File) => {
        if (personPreview) {
            URL.revokeObjectURL(personPreview)
        }
        setPersonFile(file)
        setPersonPreview(URL.createObjectURL(file))
        setResult(null)
        return false
    }

    const handleUploadWardrobe = async (file: File) => {
        try {
            setUploadingWardrobe(true)
            const item = await uploadWardrobeItem(file, {
                userId: currentUser?.id,
                name: getUploadDisplayName(file.name),
                category: '上衣',
            })
            if (item.source === 'uploaded') {
                sessionClothFilesRef.current.set(item.id, file)
            }
            setWardrobeItems((prev) => [item, ...prev.filter((prevItem) => prevItem.id !== item.id)])
            setSelectedWardrobeItemId(item.id)
            setResult(null)
            message.success(item.detection_result?.message || '已加入服装库')
        } catch (error) {
            message.error(getApiErrorMessage(error, '服装检测未通过，请上传清晰的单件服装图'))
        } finally {
            setUploadingWardrobe(false)
        }

        return false
    }

    const handleTryOn = async () => {
        if (!personFile) {
            message.warning('请先上传人物图')
            return
        }
        if (!selectedWardrobeItem) {
            message.warning('请先选择一件服装')
            return
        }

        const sessionClothFile = sessionClothFilesRef.current.get(selectedWardrobeItem.id) || null
        if (selectedWardrobeItem.source === 'uploaded' && !sessionClothFile) {
            message.warning('临时服装文件已失效，请重新上传')
            return
        }

        try {
            setLoading(true)
            const data = await createTryOn(personFile, sessionClothFile, {
                wardrobeItemId: sessionClothFile ? undefined : selectedWardrobeItem.id,
                userId: currentUser?.id,
                sessionId: currentChatSessionId || undefined,
            })
            setResult(data)
            addTryOnHistory({
                id: `${Date.now()}`,
                userId: currentUser?.id || null,
                createdAt: new Date().toISOString(),
                personImageUrl: resolveApiAssetUrl(data.person_image_url),
                clothImageUrl: resolveApiAssetUrl(data.cloth_image_url),
                resultImageUrl: resolveApiAssetUrl(data.result_image_url),
                status: data.status,
                message: data.message,
            })
            message.success(currentUser ? `${data.message}，已保存到你的试穿记录` : data.message)
        } catch (error) {
            message.error(getApiErrorMessage(error, '试穿失败，请检查试穿接口或图片格式'))
        } finally {
            setLoading(false)
        }
    }

    return (
        <PageContainer
            title="虚拟试穿"
            subtitle="上传人物图，从个性化服装库选择衣服，或上传新服装检测后加入衣橱。"
        >
            <Row gutter={[24, 24]}>
                <Col xs={24} xl={7}>
                    <Card title="输入区域" style={{ borderRadius: 16 }}>
                        <Space orientation="vertical" size={16} style={{ width: '100%' }}>
                            {bodyAnalysis && (
                                <Space wrap>
                                    <Tag color="magenta">{bodyAnalysis.gender}</Tag>
                                    <Tag color="purple">{bodyAnalysis.body_shape}</Tag>
                                </Space>
                            )}

                            <Upload showUploadList={false} beforeUpload={handleSelectPerson} accept="image/*">
                                <Button icon={<UploadOutlined />}>上传人物图</Button>
                            </Upload>

                            <div
                                style={{
                                    height: 240,
                                    borderRadius: 12,
                                    background: '#fafafa',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    color: '#999',
                                    overflow: 'hidden',
                                }}
                            >
                                {personPreview ? (
                                    <Image
                                        src={personPreview}
                                        alt="人物图预览"
                                        style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                                        preview={false}
                                    />
                                ) : (
                                    '人物图预览'
                                )}
                            </div>

                            <Card size="small" styles={{ body: { padding: 12 } }}>
                                {selectedWardrobeItem ? (
                                    <Space size={12} align="center" style={{ width: '100%' }}>
                                        <Image
                                            src={resolveApiAssetUrl(selectedWardrobeItem.image_url)}
                                            alt={selectedWardrobeItem.name}
                                            width={74}
                                            height={90}
                                            style={{ objectFit: 'contain', borderRadius: 8, background: '#fafafa' }}
                                            preview={false}
                                        />
                                        <Space orientation="vertical" size={6} style={{ minWidth: 0 }}>
                                            <Text strong ellipsis>{selectedWardrobeItem.name}</Text>
                                            <Space wrap size={6}>
                                                <Tag>{selectedWardrobeItem.category}</Tag>
                                                <Tag color={getWardrobeSourceLabel(selectedWardrobeItem.source).color}>
                                                    {getWardrobeSourceLabel(selectedWardrobeItem.source).label}
                                                </Tag>
                                            </Space>
                                        </Space>
                                    </Space>
                                ) : (
                                    <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无可选服装" />
                                )}
                            </Card>

                            <Button
                                type="primary"
                                icon={<SkinOutlined />}
                                loading={loading}
                                onClick={handleTryOn}
                            >
                                开始试穿
                            </Button>

                            {result && (
                                <Card size="small">
                                    <div style={{ lineHeight: 1.8 }}>
                                        <div>状态：{result.status}</div>
                                        <div>{result.message}</div>
                                    </div>
                                </Card>
                            )}
                        </Space>
                    </Card>
                </Col>

                <Col xs={24} xl={9}>
                    <Card
                        title="个性化服装库"
                        style={{ borderRadius: 16 }}
                        extra={(
                            <Space>
                                <Upload showUploadList={false} beforeUpload={handleUploadWardrobe} accept="image/*">
                                    <Button icon={<CloudUploadOutlined />} loading={uploadingWardrobe}>
                                        上传入库
                                    </Button>
                                </Upload>
                                <Tooltip title="刷新服装库">
                                    <Button
                                        aria-label="刷新服装库"
                                        icon={<ReloadOutlined />}
                                        onClick={() => void loadWardrobe()}
                                    />
                                </Tooltip>
                            </Space>
                        )}
                    >
                        {wardrobeLoading ? (
                            <div style={{ height: 420, display: 'grid', placeItems: 'center' }}>
                                <Spin />
                            </div>
                        ) : wardrobeItems.length > 0 ? (
                            <div
                                style={{
                                    display: 'grid',
                                    gridTemplateColumns: 'repeat(auto-fill, minmax(126px, 1fr))',
                                    gap: 12,
                                    maxHeight: 520,
                                    overflowY: 'auto',
                                    paddingRight: 4,
                                }}
                            >
                                {wardrobeItems.map((item) => {
                                    const source = getWardrobeSourceLabel(item.source)
                                    const selected = item.id === selectedWardrobeItemId

                                    return (
                                        <button
                                            type="button"
                                            key={item.id}
                                            onClick={() => {
                                                setSelectedWardrobeItemId(item.id)
                                                setResult(null)
                                            }}
                                            style={{
                                                appearance: 'none',
                                                border: selected ? '2px solid #2f6b3f' : '1px solid #edf0ea',
                                                borderRadius: 12,
                                                background: selected ? '#f3f8ef' : '#fff',
                                                padding: 10,
                                                cursor: 'pointer',
                                                textAlign: 'left',
                                                boxShadow: selected ? '0 8px 24px rgba(47, 107, 63, 0.12)' : 'none',
                                            }}
                                        >
                                            <div
                                                style={{
                                                    height: 132,
                                                    borderRadius: 10,
                                                    background: '#fafafa',
                                                    display: 'grid',
                                                    placeItems: 'center',
                                                    overflow: 'hidden',
                                                    marginBottom: 10,
                                                }}
                                            >
                                                <Image
                                                    src={resolveApiAssetUrl(item.image_url)}
                                                    alt={item.name}
                                                    style={{ width: '100%', height: 132, objectFit: 'contain' }}
                                                    preview={false}
                                                />
                                            </div>
                                            <Space orientation="vertical" size={6} style={{ width: '100%' }}>
                                                <Text strong ellipsis style={{ width: '100%' }}>
                                                    {item.name}
                                                </Text>
                                                <Space size={4} wrap>
                                                    <Tag style={{ marginInlineEnd: 0 }}>{item.category}</Tag>
                                                    <Tag color={source.color} style={{ marginInlineEnd: 0 }}>
                                                        {source.label}
                                                    </Tag>
                                                    {item.detection_result?.passed ? (
                                                        <Tooltip title={item.detection_result.message}>
                                                            <CheckCircleOutlined style={{ color: '#2f6b3f' }} />
                                                        </Tooltip>
                                                    ) : null}
                                                </Space>
                                            </Space>
                                        </button>
                                    )
                                })}
                            </div>
                        ) : (
                            <Empty description="暂无服装" />
                        )}
                    </Card>
                </Col>

                <Col xs={24} xl={8}>
                    <Card title="试穿结果" style={{ borderRadius: 16 }}>
                        <div
                            style={{
                                height: 520,
                                borderRadius: 12,
                                background: '#fafafa',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: '#999',
                                overflow: 'hidden',
                            }}
                        >
                            {result ? (
                                <Image
                                    src={resolveApiAssetUrl(result.result_image_url)}
                                    alt="试穿结果"
                                    style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                                />
                            ) : (
                                '试穿结果展示区'
                            )}
                        </div>
                    </Card>
                </Col>
            </Row>
        </PageContainer>
    )
}
