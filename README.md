# AIGC-TryOn

基于 AIGC 的智能穿搭推荐与虚拟试穿系统。项目面向毕业设计场景，提供从用户画像、体型分析、衣橱管理、对话式穿搭推荐到虚拟试穿结果保存的完整链路。

仓库地址：[paperX1023/AIGC-TryOn](https://github.com/paperX1023/AIGC-TryOn)

## 系统能力

- 用户注册、登录、个人资料维护与用户仪表盘
- 上传人物照片，结合 MediaPipe 姿态关键点进行体型分析
- 基于性别、体型、风格、场景和目标生成穿搭推荐
- 聊天式推荐接口，支持普通响应与流式响应
- 衣橱图片上传、分类识别与用户衣物管理
- 虚拟试穿上传链路，支持远程推理服务和本地占位结果
- MySQL 持久化，记录用户、体型分析、聊天、推荐、衣橱和试穿历史

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 前端 | React 19、TypeScript、Vite、Ant Design、Zustand、Axios |
| 后端 | FastAPI、Pydantic、SQLAlchemy、PyMySQL、MediaPipe、OpenCV |
| 数据库 | MySQL 8.x |
| AI 能力 | OpenAI API、MediaPipe Pose、IDM-VTON 云端推理适配 |
| 工程化 | ESLint、Pytest、GitHub |

## 目录结构

```text
AIGC-TryOn/
|-- aigc-tryon-web/          # React + TypeScript 前端应用
|-- backend/                 # FastAPI 后端服务
|   |-- app/                 # API、服务、Schema、数据库模型
|   |-- models/              # 轻量模型文件，例如 pose_landmarker_lite.task
|   |-- sql/                 # MySQL 初始化脚本
|   `-- tests/               # 后端测试
|-- cloud_inference/         # 云端虚拟试穿推理代码与部署入口
|-- docs/                    # 项目介绍、快速开始、架构图和流程图
|-- scripts/                 # 环境与模型准备脚本
|-- .gitignore
`-- README.md
```

## 快速开始

### 1. 启动后端

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

后端默认地址为 `http://127.0.0.1:8000`，接口文档地址为 `http://127.0.0.1:8000/docs`。

### 2. 启动前端

```bash
cd aigc-tryon-web
npm install
npm run dev
```

前端默认地址为 `http://127.0.0.1:5173`。

### 3. 配置数据库

创建 MySQL 数据库有两种方式：

```bash
mysql -u root -p < backend/sql/mysql_init.sql
```

或在 `backend/.env` 中开启自动建表：

```env
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/aigc_tryon?charset=utf8mb4
DATABASE_AUTO_CREATE_TABLES=true
```

## 环境变量

后端环境变量模板位于 [backend/.env.example](backend/.env.example)。

| 变量 | 说明 |
| --- | --- |
| `OPENAI_API_KEY` | OpenAI API Key，用于风格解析和推荐生成 |
| `OPENAI_MODEL` | 文本推荐模型 |
| `OPENAI_VISION_MODEL` | 可选视觉模型 |
| `POSE_MODEL_PATH` | MediaPipe 姿态模型路径 |
| `DATABASE_URL` | MySQL 完整连接串 |
| `DATABASE_AUTO_CREATE_TABLES` | 是否启动时自动建表 |
| `AUTH_SECRET_KEY` | 登录令牌签名密钥 |
| `TRYON_API_BASE_URL` | 云端虚拟试穿服务地址 |
| `TRYON_API_KEY` | 云端虚拟试穿服务鉴权密钥 |

## 核心接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/api/v1/health` | 健康检查 |
| `POST` | `/api/v1/auth/register` | 用户注册 |
| `POST` | `/api/v1/auth/login` | 用户登录 |
| `GET` | `/api/v1/auth/me` | 获取当前登录用户 |
| `POST` | `/api/v1/body/analyze` | 体型分析 |
| `POST` | `/api/v1/style/parse` | 风格语义解析 |
| `POST` | `/api/v1/recommend` | 结构化穿搭推荐 |
| `POST` | `/api/v1/chat/recommend` | 聊天式穿搭推荐 |
| `POST` | `/api/v1/chat/recommend/stream` | 流式聊天推荐 |
| `GET` | `/api/v1/wardrobe` | 衣橱列表 |
| `POST` | `/api/v1/wardrobe/upload` | 上传衣物 |
| `POST` | `/api/v1/tryon` | 虚拟试穿 |
| `GET` | `/api/v1/users/{user_id}/dashboard` | 用户仪表盘 |

## 文档与图示

- [项目概览](docs/introduction.md)
- [快速开始](docs/quickstart.md)
- [系统功能模块图](docs/system_function_module_diagram.svg)
- [数据库 ER 图](docs/database_er_core_diagram_plain.svg)
- [图片上传流程图](docs/image_upload_flowchart_plain.svg)
- [虚拟试穿流程图](docs/virtual_tryon_flowchart_plain.svg)

## 运行测试

```bash
cd backend
python -m pytest
```

```bash
cd aigc-tryon-web
npm run build
```

## 模型与大文件说明

仓库会保留必要的轻量运行文件，例如 `backend/models/pose_landmarker_lite.task`。大型权重、运行日志、上传图片、构建产物和本地环境文件不会提交到 GitHub，相关规则见 [.gitignore](.gitignore)。

`cloud_inference/` 中包含虚拟试穿云端推理适配代码。若部署真实试穿能力，需要按模型来源准备 IDM-VTON、DensePose、Human Parsing、OpenPose 等权重，并配置 `TRYON_API_BASE_URL`。

## 致谢

虚拟试穿能力参考 IDM-VTON 相关工作：

- [IDM-VTON 项目主页](https://idm-vton.github.io)
- [Improving Diffusion Models for Authentic Virtual Try-on in the Wild](https://arxiv.org/abs/2403.05139)
- [yisol/IDM-VTON](https://github.com/yisol/IDM-VTON)

本仓库在其基础上扩展了毕业设计所需的前端系统、后端 API、用户数据管理、推荐链路、数据库持久化和工程文档。
