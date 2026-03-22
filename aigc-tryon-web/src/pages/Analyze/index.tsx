import { useState } from 'react'
import { Button, Card, Col, Descriptions, Row, Space, Tag, Upload, message } from 'antd'
import { UploadOutlined } from '@ant-design/icons'
import PageContainer from '../../shared/components/PageContainer'
import { analyzeBody } from '../../features/analyze/api'
import type { BodyAnalysisResult } from '../../features/analyze/types'
import { useAppStore } from '../../shared/store/useAppStore'

export default function AnalyzePage() {
    const [file, setFile] = useState<File | null>(null)
    const [previewUrl, setPreviewUrl] = useState('')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<BodyAnalysisResult | null>(null)
    const setBodyAnalysis = useAppStore((state) => state.setBodyAnalysis)

    const handleSelectFile = (selectedFile: File) => {
        setFile(selectedFile)
        setResult(null)

        const localUrl = URL.createObjectURL(selectedFile)
        setPreviewUrl(localUrl)

        return false
    }

    const handleAnalyze = async () => {
        if (!file) {
            message.warning('请先上传照片')
            return
        }

        try {
            setLoading(true)
            const data = await analyzeBody(file)
            setResult(data)
            setBodyAnalysis(data)
            message.success('体型分析完成')
        } catch (error) {
            console.error(error)
            message.error('体型分析失败，请检查接口或稍后重试')
        } finally {
            setLoading(false)
        }
    }

    return (
        <PageContainer
            title="体型分析"
            subtitle="上传个人照片，获取体型特征与综合分析结果。"
        >
            <Row gutter={[24, 24]}>
                <Col xs={24} lg={10}>
                    <Card title="上传用户照片" style={{ borderRadius: 16 }}>
                        <Space direction="vertical" size={16} style={{ width: '100%' }}>
                            <div
                                style={{
                                    height: 360,
                                    border: '1px dashed #d9d9d9',
                                    borderRadius: 12,
                                    overflow: 'hidden',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    background: '#fafafa',
                                }}
                            >
                                {previewUrl ? (
                                    <img
                                        src={previewUrl}
                                        alt="用户照片预览"
                                        style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                                    />
                                ) : (
                                    <span style={{ color: '#999' }}>上传后显示用户照片预览</span>
                                )}
                            </div>

                            <Upload showUploadList={false} beforeUpload={handleSelectFile} accept="image/*">
                                <Button icon={<UploadOutlined />}>上传照片</Button>
                            </Upload>

                            <Button type="primary" loading={loading} onClick={handleAnalyze}>
                                开始分析
                            </Button>
                        </Space>
                    </Card>
                </Col>

                <Col xs={24} lg={14}>
                    <Card title="分析结果" style={{ borderRadius: 16 }}>
                        {result ? (
                            <Space direction="vertical" size={16} style={{ width: '100%' }}>
                                <div>
                                    <div style={{ marginBottom: 8, fontWeight: 600 }}>体型类型</div>
                                    <Tag color="blue">{result.body_shape}</Tag>
                                    <Tag color="magenta" style={{ marginLeft: 8 }}>
                                        {result.gender}
                                    </Tag>
                                </div>

                                <Descriptions bordered column={1} size="middle">
                                    <Descriptions.Item label="性别识别">
                                        {result.gender}
                                    </Descriptions.Item>
                                    <Descriptions.Item label="肩型">
                                        {result.shoulder_type}
                                    </Descriptions.Item>
                                    <Descriptions.Item label="腰型">
                                        {result.waist_type}
                                    </Descriptions.Item>
                                    <Descriptions.Item label="腿部比例">
                                        {result.leg_ratio}
                                    </Descriptions.Item>
                                    <Descriptions.Item label="综合分析">
                                        {result.analysis_summary}
                                    </Descriptions.Item>
                                </Descriptions>
                            </Space>
                        ) : (
                            <Card size="small">上传照片并点击“开始分析”后，这里展示体型分析结果。</Card>
                        )}
                    </Card>
                </Col>
            </Row>
        </PageContainer>
    )
}
