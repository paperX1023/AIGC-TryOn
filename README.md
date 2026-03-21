# AIGC Try-On

基于 AIGC 的智能穿搭推荐与虚拟试穿系统。

## 项目结构

- `aigc-tryon-web`: React + TypeScript + Vite 前端
- `backend`: FastAPI 后端，包含体型分析、性别识别、穿搭推荐和虚拟试穿接口

## 当前能力

- 上传人物照片进行体型分析
- 基于图片进行性别识别
- 根据体型、性别、场景和目标生成分类穿搭推荐
- 聊天式推荐接口
- 虚拟试穿上传链路和结果展示

## 前端启动

```bash
cd aigc-tryon-web
npm install
npm run dev
```

## 后端启动

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

## 环境变量

后端环境变量见 `backend/.env.example`。

## 说明

- `backend/models/pose_landmarker_lite.task` 需要保留，体型分析依赖这个模型文件。
- 未配置远程试穿服务时，试穿接口会返回占位结果。
