---
title: "项目概览"
sidebarTitle: "简介"
---

## AIGC-TryOn: 虚拟试衣全栈系统

本项目已在 GitHub 开源：[paperX1023/AIGC-TryOn](https://github.com/paperX1023/AIGC-TryOn)

### 📂 仓库目录解析

根据我们的 [GitHub 仓库结构](https://github.com/paperX1023/AIGC-TryOn)，项目分为以下核心模块：

* **`aigc-tryon-web/`**: 采用 React 开发的前端交互系统。
* **`backend/`**: 基于 FastAPI 的中转后端，处理逻辑与图片存储。
* **`cloud_inference/`**: 部署在 AutoDL GPU 上的推理引擎，核心模型为 IDM-VTON。
* **`scripts/`**: 用于一键准备环境和权重的自动化脚本。