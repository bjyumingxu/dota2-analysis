# Dota2战绩分析后端API

## 快速开始

### 1. 创建虚拟环境

```bash
python -m venv venv
```

### 2. 激活虚拟环境

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行服务

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问API文档

打开浏览器访问: http://localhost:8000/docs

## API端点

- `GET /api/v1/players/{account_id}/analysis` - 获取玩家战绩分析

## 环境变量

复制 `.env.example` 为 `.env` 并根据需要修改配置。

