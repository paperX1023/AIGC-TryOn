# AIGC-TryOn Backend

这是 AIGC-TryOn 的 FastAPI 后端服务，负责用户认证、体型分析、风格解析、穿搭推荐、衣橱管理、虚拟试穿转发和 MySQL 持久化。

## 技术栈

- FastAPI
- Pydantic Settings
- SQLAlchemy
- PyMySQL
- MediaPipe
- OpenCV
- OpenAI API
- Pytest

## 本地启动

```bash
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload
```

默认服务地址：

```text
http://127.0.0.1:8000
```

接口文档地址：

```text
http://127.0.0.1:8000/docs
```

## 环境变量

环境变量模板见 [.env.example](.env.example)。

| 变量 | 说明 |
| --- | --- |
| `OPENAI_API_KEY` | OpenAI API Key |
| `OPENAI_MODEL` | 文本推荐模型 |
| `OPENAI_VISION_MODEL` | 可选视觉模型 |
| `POSE_MODEL_PATH` | MediaPipe 姿态模型路径 |
| `DATABASE_URL` | MySQL 完整连接串 |
| `DATABASE_AUTO_CREATE_TABLES` | 是否启动时自动建表 |
| `AUTH_SECRET_KEY` | 登录令牌签名密钥 |
| `AUTH_TOKEN_EXPIRE_MINUTES` | 登录令牌有效期 |
| `TRYON_API_BASE_URL` | 云端虚拟试穿服务地址 |
| `TRYON_API_KEY` | 云端虚拟试穿服务密钥 |

## 数据库

初始化脚本位于 [sql/mysql_init.sql](sql/mysql_init.sql)。

```bash
mysql -u root -p < sql/mysql_init.sql
```

核心数据表：

- `users`
- `body_analysis_records`
- `chat_sessions`
- `chat_messages`
- `recommendation_records`
- `tryon_records`
- `wardrobe_items`

## API 模块

| 模块 | 路径示例 | 说明 |
| --- | --- | --- |
| 健康检查 | `GET /api/v1/health` | 服务可用性检查 |
| 认证与用户 | `/api/v1/auth/*`、`/api/v1/users/*` | 注册、登录、用户资料、仪表盘 |
| 体型分析 | `POST /api/v1/body/analyze` | 上传人物图并返回体型特征 |
| 风格解析 | `POST /api/v1/style/parse` | 将自然语言需求解析为结构化标签 |
| 穿搭推荐 | `POST /api/v1/recommend` | 生成结构化穿搭建议 |
| 聊天推荐 | `POST /api/v1/chat/recommend` | 对话式推荐 |
| 流式聊天 | `POST /api/v1/chat/recommend/stream` | SSE 流式推荐输出 |
| 衣橱管理 | `GET /api/v1/wardrobe`、`POST /api/v1/wardrobe/upload` | 上传和查询衣物 |
| 虚拟试穿 | `POST /api/v1/tryon` | 调用云端试穿或返回占位结果 |

## 测试

```bash
python -m pytest
```

## 文件与模型说明

- `models/pose_landmarker_lite.task` 是体型分析依赖的轻量模型文件，需要保留。
- `uploads/` 是运行时上传目录，不提交到 GitHub。
- `.env` 包含本地密钥和数据库配置，不提交到 GitHub。
