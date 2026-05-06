---
title: "快速开始"
sidebarTitle: "Quickstart"
---

# 快速开始

本文档用于在本地启动 AIGC-TryOn 的前端、后端和 MySQL 数据库。

## 环境要求

- Node.js 18 或更高版本
- Python 3.10 或更高版本
- MySQL 8.x
- 可选：可访问 OpenAI API 的网络环境
- 可选：部署虚拟试穿所需的 GPU 推理环境

## 1. 准备数据库

手动初始化：

```bash
mysql -u root -p < backend/sql/mysql_init.sql
```

或使用后端自动建表。复制环境变量文件后，在 `backend/.env` 中配置：

```env
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/aigc_tryon?charset=utf8mb4
DATABASE_AUTO_CREATE_TABLES=true
```

核心数据表包括：

| 表名 | 用途 |
| --- | --- |
| `users` | 用户基础资料、登录信息和风格偏好 |
| `body_analysis_records` | 体型分析结果 |
| `chat_sessions` | 聊天会话 |
| `chat_messages` | 聊天消息与解析结果 |
| `recommendation_records` | 结构化推荐结果 |
| `tryon_records` | 虚拟试穿记录 |
| `wardrobe_items` | 用户衣橱图片与识别信息 |

## 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload
```

Windows PowerShell:

```powershell
cd backend
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload
```

启动后访问：

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
```

## 3. 启动前端

```bash
cd aigc-tryon-web
npm install
npm run dev
```

启动后访问：

```text
http://127.0.0.1:5173
```

前端默认后端地址为 `http://127.0.0.1:8000/`，配置位于 `aigc-tryon-web/src/shared/api/client.ts`。

## 4. 配置 AI 与试穿能力

后端环境变量见 `backend/.env.example`。

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5-mini
OPENAI_VISION_MODEL=

POSE_MODEL_PATH=models/pose_landmarker_lite.task

TRYON_API_BASE_URL=http://your-remote-host:6006
TRYON_API_KEY=
```

说明：

- 未配置 `OPENAI_API_KEY` 时，部分推荐能力会退化或不可用，具体取决于服务实现。
- `POSE_MODEL_PATH` 指向体型分析所需的 MediaPipe 模型文件。
- 未配置 `TRYON_API_BASE_URL` 时，虚拟试穿接口会返回本地占位结果，便于前后端联调。
- 若云端试穿返回 `/results/xxx.jpg` 这类相对路径，后端会拼接成完整远程地址，并优先下载到本地 `uploads/tryon/result`。

## 5. 常用接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/api/v1/health` | 健康检查 |
| `POST` | `/api/v1/auth/register` | 注册 |
| `POST` | `/api/v1/auth/login` | 登录 |
| `GET` | `/api/v1/auth/me` | 当前用户 |
| `POST` | `/api/v1/body/analyze` | 体型分析 |
| `POST` | `/api/v1/chat/recommend` | 聊天推荐 |
| `POST` | `/api/v1/chat/recommend/stream` | 流式聊天推荐 |
| `GET` | `/api/v1/wardrobe` | 衣橱列表 |
| `POST` | `/api/v1/wardrobe/upload` | 上传衣物 |
| `POST` | `/api/v1/tryon` | 虚拟试穿 |

## 6. 验证命令

后端测试：

```bash
cd backend
python -m pytest
```

前端构建：

```bash
cd aigc-tryon-web
npm run build
```
