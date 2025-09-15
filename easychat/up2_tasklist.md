# EasyChat 2.0 升级任务清单

基于简化的PRD2文档，以下是具体的开发任务清单：

## 核心开发任务

### 1. 环境准备
- [ ] 安装Flask依赖包
- [ ] 更新requirements.txt文件
- [ ] 验证现有.env配置文件

### 2. API服务器开发
- [x] 在main.py中添加Flask应用初始化
- [x] 实现POST /chat端点
  - [x] 接收JSON格式的message参数
  - [x] 调用现有的DeepSeek API逻辑
  - [x] 返回JSON格式的response
  - [x] 添加基本错误处理
- [x] 实现GET /health端点
  - [x] 返回简单的状态信息
- [x] 添加命令行参数解析
  - [x] 支持--api参数启动API模式
  - [x] 保持默认CLI模式不变

### 3. 代码重构
- [x] 提取聊天逻辑为独立函数
- [x] 确保CLI和API模式共享相同的核心逻辑
- [x] 添加简单的日志输出

### 4. 测试验证
- [x] 测试CLI模式功能完整性
- [x] 测试API服务器启动
- [x] 测试POST /chat端点
  - [x] 正常请求响应
  - [x] 错误请求处理
- [x] 测试GET /health端点
- [x] 使用curl命令验证API接口

### 5. 集成测试
- [ ] 确认easyEval2能够调用新的API接口
- [ ] 验证完整的评估流程
- [ ] 测试错误场景处理

### 6. 文档更新
- [ ] 更新README.md
  - [ ] 添加API模式使用说明
  - [ ] 更新安装和运行指南
- [ ] 添加API接口文档
- [ ] 更新示例用法

## 技术要点

### API设计规范
```json
// POST /chat 请求格式
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

// GET /health 响应格式
{
  "status": "ok"
}
```

### 启动命令
```bash
# CLI模式（默认）
python main.py

# API模式
python main.py --api
```

### 依赖包要求
- flask
- python-dotenv
- openai

## 验收标准

- [ ] API服务器能够在8000端口启动
- [ ] /chat接口正确处理POST请求
- [ ] /health接口返回状态信息
- [ ] CLI模式保持原有功能
- [ ] easyEval2能够成功调用API
- [ ] 基本错误处理机制工作正常

## 注意事项

1. **保持简单**：避免引入复杂的架构设计
2. **向下兼容**：确保原有CLI功能完全不受影响
3. **学习导向**：代码结构清晰，易于理解
4. **满足需求**：专注于easyEval2的集成需求

---

**任务完成标记说明**：
- [ ] 待完成
- [x] 已完成

每个任务完成后，请在任务前添加[x]标记，并确认后继续下一个任务。