import type { ReactNode } from 'react'

interface Props {
    title: string
    subtitle?: string
    children: ReactNode
}

export default function PageContainer({ title, subtitle, children }: Props) {
    return (
        <div style={{ maxWidth: 1280, margin: '0 auto' }}>
            <div style={{ marginBottom: 20 }}>
                <h1 style={{ margin: 0, fontSize: 28, fontWeight: 700, color: '#1f1f1f' }}>
                    {title}
                </h1>
                {subtitle ? (
                    <p style={{ marginTop: 8, marginBottom: 0, color: '#666', fontSize: 15 }}>
                        {subtitle}
                    </p>
                ) : null}
            </div>
            {children}
        </div>
    )
}