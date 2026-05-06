---
title: "项目概览"
sidebarTitle: "简介"
---

# AIGC-TryOn: 智能穿搭推荐与虚拟试穿系统

本项目是一个面向毕业设计的 AIGC 全栈应用，目标是把“用户照片分析、风格理解、穿搭推荐、衣橱管理、虚拟试穿、历史沉淀”串成一套可演示、可扩展、可落地的系统。

GitHub 仓库：[paperX1023/AIGC-TryOn](https://github.com/paperX1023/AIGC-TryOn)

## 业务流程

1. 用户注册或登录系统。
2. 用户上传人物照片，系统识别基础体型特征。
3. 用户通过表单或聊天输入穿搭场景、风格偏好和目标。
4. 后端结合用户画像、体型分析和风格标签生成推荐结果。
5. 用户上传服装图，系统调用云端虚拟试穿服务或返回本地占位结果。
6. 系统将体型分析、聊天、推荐、试穿和衣橱数据保存到 MySQL，供历史页和用户仪表盘展示。

## 核心模块

| 模块 | 说明 |
| --- | --- |
| `aigc-tryon-web/` | React + TypeScript 前端，提供登录、分析、推荐、试穿、历史和个人资料页面 |
| `backend/` | FastAPI 后端，承载 API、业务服务、数据库模型、上传文件管理和第三方 AI 能力调用 |
| `cloud_inference/` | 云端虚拟试穿推理代码，适配 IDM-VTON 相关模型能力 |
| `docs/` | 项目说明、快速开始、系统模块图、数据库 ER 图和业务流程图 |
| `scripts/` | 环境准备和模型准备脚本 |

## 系统图示

- [系统功能模块图](system_function_module_diagram.svg)
- [数据库 ER 图](database_er_core_diagram_plain.svg)
- [图片上传流程图](image_upload_flowchart_plain.svg)
- [虚拟试穿流程图](virtual_tryon_flowchart_plain.svg)

## 技术特点

- 前后端分离，前端用 React/Vite 构建交互界面，后端用 FastAPI 暴露 REST 与流式接口。
- 推荐链路可兼容 OpenAI API，便于从规则推荐扩展到生成式推荐。
- 数据库围绕用户全链路行为设计，方便展示历史记录、用户仪表盘和答辩数据闭环。
- 虚拟试穿接口同时支持远程推理和本地占位结果，便于在无 GPU 环境下进行系统演示。
