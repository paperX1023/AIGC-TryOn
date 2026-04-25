import React from 'react'
import ReactDOM from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { App as AntdApp, ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import router from './app/router'
import './styles/global.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <ConfigProvider
            locale={zhCN}
            theme={{
                token: {
                    colorPrimary: '#2f6b3f',
                    borderRadius: 12,
                    fontFamily: 'Inter, "PingFang SC", "Microsoft YaHei", sans-serif',
                },
                components: {
                    Card: {
                        borderRadiusLG: 18,
                    },
                    Button: {
                        controlHeightLG: 44,
                    },
                    Input: {
                        controlHeightLG: 44,
                    },
                },
            }}
        >
            <AntdApp>
                <RouterProvider router={router} />
            </AntdApp>
        </ConfigProvider>
    </React.StrictMode>,
)
