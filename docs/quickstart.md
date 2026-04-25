---
title: "快速开始"
sidebarTitle: "Quickstart"
---

## 本地启动

### 1. 前端

```bash
cd aigc-tryon-web
npm install
npm run dev
```

### 2. 后端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload
```

## MySQL 初始化

项目已经补好 MySQL 结构，初始化有两种方式：

1. 自动建表：在 `backend/.env` 中配置 `DATABASE_URL`，并保持 `DATABASE_AUTO_CREATE_TABLES=true`。
2. 手动建表：执行 [backend/sql/mysql_init.sql](/d:/AIGC-毕设/backend/sql/mysql_init.sql)。

推荐的连接串格式：

```env
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/aigc_tryon?charset=utf8mb4
DATABASE_AUTO_CREATE_TABLES=true
```

## 数据库结构

当前 MySQL 结构围绕“用户全链路行为”设计，核心表如下：

1. `users`
用户基础资料，包含用户名、昵称、邮箱、手机号、身高体重、风格偏好等。

2. `body_analysis_records`
保存每次体型分析结果，包含识别出的性别、体型、肩型、腰型、腿型和分析摘要。

3. `chat_sessions`
保存聊天会话主表，用 `session_code` 串起同一次推荐对话，并关联最近一次体型分析。

4. `chat_messages`
保存每条聊天消息，包括用户输入、助手回复，以及解析出的风格标签和推荐结果。

5. `recommendation_records`
保存结构化推荐结果，便于后续做“推荐历史”“推荐效果分析”或答辩演示。

6. `tryon_records`
保存试穿记录，包含人物图、服装图、结果图、来源类型（`remote` / `mock`）和状态信息。

## 云端试穿结果图

后端已经兼容云端返回的相对路径结果：

- 如果云端返回完整 `http/https` 图片地址，后端会直接使用。
- 如果云端返回 `/results/xxx.jpg` 这类相对路径，后端会自动拼成完整云端地址。
- 后端会优先把云端结果图下载到本地 `uploads/tryon/result`，前端最终拿到的是本地可访问的 `/uploads/...` 地址。

相关环境变量：

```env
TRYON_API_BASE_URL=http://your-remote-host:6006
TRYON_API_KEY=
```

## 新增用户接口

后端新增了基础用户接口，便于把体型分析、聊天和试穿记录关联到同一个用户：

1. `POST /api/v1/users`
创建用户。

2. `GET /api/v1/users`
查看用户列表。

3. `GET /api/v1/users/{user_id}`
查看单个用户信息。

4. `PATCH /api/v1/users/{user_id}`
更新用户资料。

5. `GET /api/v1/users/{user_id}/dashboard`
获取用户仪表盘数据，包括最近体型分析、聊天会话、推荐记录和试穿记录。

## 现有接口如何入库

以下接口已支持可选 `user_id` 关联：

1. `POST /api/v1/body/analyze`
表单中增加 `user_id` 后，会把体型分析结果写入 `body_analysis_records`。

2. `POST /api/v1/chat/recommend`
JSON 中增加 `user_id` 后，会把聊天内容、推荐结果和会话信息写入 `chat_sessions`、`chat_messages`、`recommendation_records`。

3. `POST /api/v1/tryon`
表单中增加 `user_id` 与可选 `session_id` 后，会把试穿记录写入 `tryon_records`。
