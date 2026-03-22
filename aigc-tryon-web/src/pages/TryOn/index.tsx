import { useState } from 'react'
import { Card, Col, Row, Button, Upload, Space, Image, message, Tag } from 'antd'
import { UploadOutlined } from '@ant-design/icons'
import { createTryOn } from '../../features/tryon/api'
import type { TryOnResult } from '../../features/tryon/types'
import PageContainer from '../../shared/components/PageContainer'
import { resolveApiAssetUrl } from '../../shared/api/assets'
import { useAppStore } from '../../shared/store/useAppStore'

export default function TryOnPage() {
    const bodyAnalysis = useAppStore((state) => state.bodyAnalysis)
    const addTryOnHistory = useAppStore((state) => state.addTryOnHistory)
    const [personFile, setPersonFile] = useState<File | null>(null)
    const [clothFile, setClothFile] = useState<File | null>(null)
    const [personPreview, setPersonPreview] = useState('')
    const [clothPreview, setClothPreview] = useState('')
    const [result, setResult] = useState<TryOnResult | null>(null)
    const [loading, setLoading] = useState(false)

    const handleSelectPerson = (file: File) => {
        setPersonFile(file)
        setPersonPreview(URL.createObjectURL(file))
        setResult(null)
        return false
    }

    const handleSelectCloth = (file: File) => {
        setClothFile(file)
        setClothPreview(URL.createObjectURL(file))
        setResult(null)
        return false
    }

    const handleTryOn = async () => {
        if (!personFile || !clothFile) {
            message.warning('请先上传人物图和服装图')
            return
        }

        try {
            setLoading(true)
            const data = await createTryOn(personFile, clothFile)
            setResult(data)
            addTryOnHistory({
                id: `${Date.now()}`,
                createdAt: new Date().toISOString(),
                personImageUrl: resolveApiAssetUrl(data.person_image_url),
                clothImageUrl: resolveApiAssetUrl(data.cloth_image_url),
                resultImageUrl: resolveApiAssetUrl(data.result_image_url),
                status: data.status,
                message: data.message,
            })
            message.success(data.message)
        } catch (error) {
            console.error(error)
            message.error('试穿失败，请检查试穿接口或图片格式')
        } finally {
            setLoading(false)
        }
    }

    return (
        <PageContainer
            title="虚拟试穿"
            subtitle="上传人物图与服装图，生成虚拟试穿效果。"
        >
            <Row gutter={[24, 24]}>
                <Col xs={24} lg={8}>
                    <Card title="输入区域" style={{ borderRadius: 16 }}>
                        <Space direction="vertical" size={16} style={{ width: '100%' }}>
                            {bodyAnalysis && (
                                <Space wrap>
                                    <Tag color="magenta">{bodyAnalysis.gender}</Tag>
                                    <Tag color="purple">{bodyAnalysis.body_shape}</Tag>
                                </Space>
                            )}

                            <Upload showUploadList={false} beforeUpload={handleSelectPerson} accept="image/*">
                                <Button icon={<UploadOutlined />}>上传人物图</Button>
                            </Upload>

                            <Upload showUploadList={false} beforeUpload={handleSelectCloth} accept="image/*">
                                <Button icon={<UploadOutlined />}>上传服装图</Button>
                            </Upload>

                            <Button type="primary" loading={loading} onClick={handleTryOn}>
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

                <Col xs={24} lg={8}>
                    <Card title="原始素材预览" style={{ borderRadius: 16 }}>
                        <Space direction="vertical" size={16} style={{ width: '100%' }}>
                            <div
                                style={{
                                    height: 220,
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
                            <div
                                style={{
                                    height: 220,
                                    borderRadius: 12,
                                    background: '#fafafa',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    color: '#999',
                                    overflow: 'hidden',
                                }}
                            >
                                {clothPreview ? (
                                    <Image
                                        src={clothPreview}
                                        alt="服装图预览"
                                        style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                                        preview={false}
                                    />
                                ) : (
                                    '服装图预览'
                                )}
                            </div>
                        </Space>
                    </Card>
                </Col>

                <Col xs={24} lg={8}>
                    <Card title="试穿结果" style={{ borderRadius: 16 }}>
                        <div
                            style={{
                                height: 460,
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
