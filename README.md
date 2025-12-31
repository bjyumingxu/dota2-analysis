# Dota2战绩分析网页

一个基于FastAPI和Vue 3的Dota2玩家战绩数据分析网页，用户输入Steam账号ID即可查看近20场战绩的详细分析。

## ✨ 功能特性

- 📊 **一句话点评**：根据KDA、胜率等数据生成犀利的点评
- 📈 **胜率曲线**：可视化展示近20场比赛的胜率变化趋势
- 👥 **最佳战友/最爱损友**：分析组队数据，找出最佳和最差队友
- 📋 **数据统计**：展示击杀、死亡、助攻、正补、英雄伤害等详细数据
- 🎨 **精美UI**：深色主题，参考wago.io风格，支持背景图片轮播
- 📱 **响应式设计**：支持桌面端和移动端访问

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- npm 或 yarn

### 本地开发

#### 后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

后端服务将在 http://localhost:8001 启动

#### 前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 启动

## 📁 项目结构

```
opendotaAI/
├── backend/                 # 后端代码
│   ├── src/
│   │   ├── api/           # API路由
│   │   ├── core/          # 核心配置
│   │   └── services/      # 业务逻辑
│   ├── requirements.txt    # Python依赖
│   └── railway.json       # Railway部署配置
│
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── pages/         # 页面组件
│   │   └── style.css      # 全局样式
│   ├── public/            # 静态资源
│   ├── package.json       # Node依赖
│   └── vercel.json        # Vercel部署配置
│
├── PRD.md                 # 产品需求文档
├── 开发计划.md            # 开发计划
└── 部署步骤详细版.md      # 部署指南
```

## 🌐 部署

### 推荐方案：Railway + Vercel

- **后端**：部署到 Railway（免费，配置简单）
- **前端**：部署到 Vercel（免费，自动部署）

详细部署步骤请参考：[部署步骤详细版.md](./部署步骤详细版.md)

## 🔧 配置

### 后端环境变量

创建 `backend/.env` 文件：

```env
OPENDOTA_API_BASE_URL=https://api.opendota.com/api
CORS_ORIGINS=*
```

### 前端环境变量

创建 `frontend/.env` 文件（生产环境）：

```env
VITE_API_BASE_URL=https://your-backend-url.railway.app
```

## 📚 API文档

后端启动后，访问 http://localhost:8001/docs 查看Swagger API文档。

## 🛠️ 技术栈

### 后端
- **框架**：FastAPI
- **语言**：Python 3.11+
- **HTTP客户端**：httpx（异步）
- **数据验证**：Pydantic

### 前端
- **框架**：Vue 3 + TypeScript
- **构建工具**：Vite
- **图表库**：ECharts
- **HTTP客户端**：Axios

## 📝 开发计划

详细开发计划请参考：[开发计划.md](./开发计划.md)

## 📄 许可证

本项目仅供学习和研究使用。

## 👤 作者

ydd

## 📞 支持

如有问题或建议，请提交Issue。

---

**版权归嘟嘟可大冒险公会所有**
