# EasyChat 2.0 - 产品需求文档 (PRD2)

## 项目概述

EasyChat 2.0 是对原有命令行聊天程序的简单升级，在保持原有CLI功能的基础上，新增轻量级HTTP API功能，满足easyEval2语义评估系统的调用需求。本版本专注于学习目标，采用最简单的技术方案实现API服务。

## 版本升级目标

### 核心升级点
1. **简单API服务**：提供基础的HTTP接口供easyEval2调用
2. **保持兼容**：完全保持原有CLI功能不变
3. **学习导向**：技术栈简单，便于理解和维护

### 学习价值
- 🔗 **API基础**：学习HTTP API的基本实现
- 📊 **系统集成**：理解不同系统间的接口对接
- 🎯 **实用性**：满足语义评估的实际需求

## 功能需求规格

### 1. HTTP API服务器功能

#### 1.1 简单服务器
- **框架选择**：Flask（最简单的Python Web框架）
- **运行模式**：单线程，满足评估需求即可
- **端口配置**：固定8000端口
- **数据格式**：JSON请求和响应

#### 1.2 基础API接口

**主要端点：POST /chat**
```json
// 请求格式
{
  "message": "用户问题内容"
}

// 成功响应格式
{
  "response": "AI回答内容"
}

// 错误响应格式
{
  "error": "错误描述"
}
```

**健康检查端点：GET /health**
```json
{
  "status": "ok"
}
```

#### 1.3 简单处理
- **无状态设计**：每次请求独立处理，不保存会话状态
- **单次对话**：专注于单轮问答，满足评估需求

### 2. 简单双模式运行

#### 2.1 CLI模式（默认）
```bash
# 默认CLI模式
python main.py
```

#### 2.2 API服务器模式
```bash
# API服务器模式
python main.py --api
```

### 3. easyEval2系统集成

#### 3.1 基本兼容
- **接口匹配**：满足easyEval2的基本调用需求
- **JSON格式**：简单的JSON请求和响应
- **错误处理**：基本的错误信息返回

#### 3.2 评估支持
- **顺序处理**：逐个处理评估请求
- **简单日志**：基本的调用记录

## 简单技术架构

### 基本架构
```
easyEval2 ──HTTP──> EasyChat API服务器 ──> DeepSeek API
用户CLI ──直接调用──> EasyChat主程序 ──> DeepSeek API
```

### 简单模块设计

#### 1. 主程序 (main.py)
- **模式选择**：CLI模式或API模式
- **基本配置**：读取.env文件

#### 2. API服务器 (简单Flask应用)
- **单个路由**：处理/chat请求
- **基本错误处理**：返回错误信息

### 简单文件结构
```
easychat/
├── main.py                 # 主程序（包含CLI和API功能）
├── .env                    # 环境配置文件
├── systemprompt.md         # 系统提示词文件
├── requirements.txt        # 依赖文件（添加Flask）
├── prd.md                  # 原版PRD文档
├── prd2.md                 # 本文档
└── README.md               # 使用说明
```

## 简单配置

### .env文件
```env
# DeepSeek API配置
DEEPSEEK_API_KEY=your_api_key_here
```

## 简单测试方案

### 基本验证

#### 1. 手动测试
- **CLI功能**：确保原有命令行功能正常
- **API接口**：使用curl测试/chat接口
- **集成测试**：运行easyEval2验证对接

### 测试命令
```bash
# 测试API接口
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'

# 测试健康检查
curl http://localhost:8000/health
```

## 简单部署

### 本地运行
```bash
# 1. 安装依赖
pip install flask python-dotenv openai

# 2. 配置API密钥
# 编辑.env文件填入DEEPSEEK_API_KEY

# 3. 启动API服务器
python main.py --api

# 4. 验证服务
curl http://localhost:8000/health
```

## 主要风险

### 基本风险
1. **API调用失败**
   - 风险：DeepSeek API不可用
   - 缓解：返回明确的错误信息

2. **接口不匹配**
   - 风险：与easyEval2调用格式不符
   - 缓解：严格按照现有格式实现

## 成功标准

### 基本要求
- ✅ API服务器能够启动并监听8000端口
- ✅ /chat接口能够处理POST请求并返回AI回答
- ✅ /health接口能够返回状态信息
- ✅ CLI模式保持原有功能不变
- ✅ easyEval2能够成功调用EasyChat API
- ✅ 基本的错误处理机制

## 可能的改进

### 后续优化
- 添加简单的日志记录
- 支持更多配置选项
- 改进错误处理
- 添加基本的性能监控

---

## 附录

### A. API接口详细规范

#### POST /chat
**请求头**
```
Content-Type: application/json
Accept: application/json
```

**请求体参数**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| message | string | 是 | - | 用户输入的问题 |
| session_id | string | 否 | auto-generated | 会话标识符 |
| temperature | float | 否 | 0.7 | 回答随机性控制 |
| max_tokens | integer | 否 | 2000 | 最大回答长度 |
| stream | boolean | 否 | false | 是否流式返回 |

**响应状态码**
- 200: 成功
- 400: 请求参数错误
- 500: 服务器内部错误
- 503: 外部API不可用

#### GET /health
**响应体**
```json
{
  "status": "healthy|unhealthy",
  "version": "2.0.0",
  "uptime": 3600,
  "api_status": "connected|disconnected",
  "active_sessions": 5,
  "memory_usage": "256MB",
  "last_check": "2025-09-15T12:00:00Z"
}
```

### B. 错误代码对照表

| 错误代码 | HTTP状态码 | 说明 |
|----------|------------|------|
| INVALID_REQUEST | 400 | 请求格式错误 |
| MISSING_MESSAGE | 400 | 缺少message参数 |
| MESSAGE_TOO_LONG | 400 | 消息内容过长 |
| SESSION_NOT_FOUND | 404 | 会话不存在 |
| API_UNAVAILABLE | 503 | DeepSeek API不可用 |
| RATE_LIMITED | 429 | 请求频率过高 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

### C. 配置参数说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| API_SERVER_HOST | localhost | API服务器监听地址 |
| API_SERVER_PORT | 8000 | API服务器监听端口 |
| SESSION_TIMEOUT | 1800 | 会话超时时间（秒） |
| MAX_SESSIONS | 100 | 最大并发会话数 |
| REQUEST_TIMEOUT | 30 | API请求超时时间（秒） |
| MAX_TOKENS | 2000 | 最大回答长度 |
| DEFAULT_TEMPERATURE | 0.7 | 默认回答随机性 |

---

*本PRD文档版本：2.0*  
*最后更新：2025-09-15*  
*文档状态：待评审*