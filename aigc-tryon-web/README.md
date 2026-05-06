# AIGC-TryOn Web

这是 AIGC-TryOn 的前端应用，基于 React、TypeScript、Vite 和 Ant Design 构建。前端负责用户登录、体型分析上传、聊天式穿搭推荐、衣橱管理、虚拟试穿和历史记录展示。

## 功能页面

| 路由 | 说明 |
| --- | --- |
| `/` | 首页与功能入口 |
| `/analyze` | 上传人物照片并查看体型分析结果 |
| `/chat` | 聊天式穿搭推荐 |
| `/tryon` | 上传人物图和服装图，生成试穿结果 |
| `/history` | 查看体型分析、推荐和试穿历史 |
| `/profile` | 用户资料与偏好维护 |

除首页外，其余页面会通过 `RequireUser` 要求当前用户已登录。

## 技术栈

- React 19
- TypeScript
- Vite
- Ant Design
- Zustand
- Axios
- React Router

## 本地启动

```bash
npm install
npm run dev
```

默认访问地址：

```text
http://127.0.0.1:5173
```

后端默认地址写在 [src/shared/api/client.ts](src/shared/api/client.ts)：

```ts
export const API_BASE_URL = 'http://127.0.0.1:8000/'
```

如需接入其他后端地址，可修改该常量或后续改造为 Vite 环境变量。

## 常用命令

```bash
npm run dev
npm run build
npm run lint
npm run preview
```

## 目录说明

```text
src/
|-- app/                 # 路由、应用根组件、登录守卫
|-- features/            # 业务 API 与类型定义
|-- pages/               # 页面级组件
|-- shared/              # 通用 API、状态和布局组件
`-- styles/              # 全局样式
```

## 与后端的接口关系

前端接口路径统一维护在 [src/shared/api/endpoints.ts](src/shared/api/endpoints.ts)，Axios 实例统一维护在 [src/shared/api/client.ts](src/shared/api/client.ts)。图片资源路径会通过 [src/shared/api/assets.ts](src/shared/api/assets.ts) 转成可访问 URL。
