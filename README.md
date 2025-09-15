# AI对话系统评估项目集合 v0.1

一个完整的AI对话系统开发、部署和评估解决方案，包含对话系统本体和两套互补的评估工具。

## 项目意图

本项目旨在构建一个完整的AI对话系统生态，包括：

1. **智能对话系统**：基于DeepSeek API的高质量对话服务
2. **快速评估工具**：基于关键词匹配的轻量级评估方案
3. **深度评估工具**：基于AI语义分析的高精度评估系统

通过这三个组件的协同工作，实现从开发、测试到生产的完整AI对话系统解决方案。

## 项目结构

```
trae0915_eval01/
├── easychat/           # AI对话系统
│   ├── main.py         # 主程序（CLI + API模式）
│   ├── requirements.txt
│   └── README.md
├── easyEval/           # 快速评估工具
│   ├── src/eval.py     # 关键词匹配评估
│   ├── tests/test_cases.json
│   └── README.md
├── easyEval2/          # 智能评估工具
│   ├── main.py         # AI语义评估
│   ├── src/semantic_eval.py
│   └── README.md
└── README.md           # 项目总览（本文件）
```

## 子项目关联关系

### 核心架构图

```mermaid
graph LR
    %% 核心组件
    EC["EasyChat<br/>对话系统"]
    E1["easyEval<br/>快速评估"]
    E2["easyEval2<br/>智能评估"]
    TC["测试用例库<br/>test_cases.json"]
    
    %% EasyChat 功能
    CLI["CLI交互模式"]
    API["API服务模式"]
    STREAM["流式响应"]
    
    %% easyEval 功能
    KW["关键词匹配"]
    COMP["完成率统计"]
    FAST["快速验证"]
    
    %% easyEval2 功能
    SEM["AI语义分析"]
    SCORE["5维度评分"]
    REPORT["详细报告"]
    
    %% 测试场景
    CHAT["通用对话"]
    QA["知识问答"]
    WRITE["创意写作"]
    TECH["技术支持"]
    
    %% 连接关系
    EC --> CLI
    EC --> API
    EC --> STREAM
    
    E1 --> KW
    E1 --> COMP
    E1 --> FAST
    
    E2 --> SEM
    E2 --> SCORE
    E2 --> REPORT
    
    TC --> CHAT
    TC --> QA
    TC --> WRITE
    TC --> TECH
    
    %% 评估流程
    EC -."对话输出".-> E1
    EC -."对话输出".-> E2
    TC -."测试用例".-> E1
    TC -."测试用例".-> E2
    
    %% 样式定义
    classDef systemBox fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef evalBox fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef dataBox fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    
    class EC systemBox
    class E1,E2 evalBox
    class TC dataBox
    
    %% 样式定义
    classDef systemBox fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef evalBox fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef dataBox fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    
    class EC systemBox
    class E1,E2 evalBox
    class TC dataBox
```

### 工作流程

1. **开发阶段**：使用 EasyChat CLI模式进行功能开发和调试
2. **快速验证**：使用 easyEval 进行基础功能完整性检查
3. **深度评估**：使用 easyEval2 进行语义质量分析
4. **生产部署**：EasyChat API模式提供服务，定期使用评估工具监控质量

## 快速开始

### 一键启动（推荐）

我们提供了统一的启动脚本，让您轻松使用所有功能：

```bash
# 交互式模式 - 菜单选择功能
python start.py

# 直接启动模式
python start.py easychat              # CLI对话模式
python start.py easychat -- --api     # API服务模式
python start.py easyeval              # 快速评估
python start.py easyeval2             # 智能评估
python start.py easyeval2 -- --dry-run # 配置验证
```

### 环境准备

```bash
# 1. 克隆项目
git clone <repository-url>
cd trae0915_eval01

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装各子项目依赖
cd easychat && pip install -r requirements.txt && cd ..
cd easyEval2 && pip install -r requirements.txt && cd ..
```

### 配置API密钥

在每个子项目目录下创建 `.env` 文件：

```bash
# DeepSeek API配置
DEEPSEEK_API_KEY=your_api_key_here
API_BASE_URL=https://api.deepseek.com/v1

# 本地API配置（可选，用于easyEval2）
LOCAL_API_BASE_URL=http://localhost:11434
LOCAL_API_MODEL=qwen2.5:7b
```

### 使用方法

#### 1. 启动对话系统

```bash
cd easychat
pip install -r requirements.txt

# CLI交互模式
python main.py

# API服务模式（后台运行）
python main.py --api
```

#### 2. 快速评估（开发阶段推荐）

```bash
cd easyEval
pip install -r requirements.txt

# 运行快速评估
python src/eval.py
```

#### 3. 智能评估（生产阶段推荐）

```bash
cd easyEval2
pip install -r requirements.txt

# 使用本地API（免费）
python main.py --use-local-api --limit 10

# 使用DeepSeek API（高精度）
python main.py --use-deepseek-api --limit 5
```

## 评估对比

| 特性 | easyEval | easyEval2 |
|------|----------|----------|
| **评估方式** | 关键词匹配 | AI语义分析 |
| **评估维度** | 完成率 | 5维度评分 |
| **评估速度** | 极快 | 中等 |
| **评估精度** | 基础 | 高级 |
| **成本** | 免费 | 本地免费/云端付费 |
| **报告格式** | JSON + TXT | JSON + Markdown |
| **适用场景** | 开发调试 | 生产监控 |
| **推荐用途** | 快速验证 | 深度分析 |

## 技术栈

### 共同依赖
- **Python 3.8+**：主要开发语言
- **OpenAI SDK**：API客户端
- **python-dotenv**：环境配置管理
- **requests**：HTTP请求处理

### EasyChat 特有
- **Flask**：Web API框架
- **流式响应**：实时对话体验

### easyEval 特有
- **subprocess**：外部程序调用
- **tqdm**：进度条显示
- **关键词匹配**：快速评估算法

### easyEval2 特有
- **Rich**：美观的终端界面
- **Pydantic**：数据验证
- **AI语义分析**：深度评估算法

## 使用场景

### 开发阶段
1. 使用 **EasyChat CLI模式** 进行功能开发
2. 使用 **easyEval** 快速验证基础功能
3. 迭代优化对话逻辑

### 测试阶段
1. 启动 **EasyChat API服务**
2. 使用 **easyEval2 本地API模式** 进行详细评估
3. 分析评估报告，优化系统性能

### 生产阶段
1. 部署 **EasyChat API服务**
2. 定期使用 **easyEval2 DeepSeek API模式** 监控质量
3. 根据评估结果持续优化

### 全面评估
- 结合使用两套评估工具
- 获得多维度评估结果
- 确保系统质量和稳定性

## 配置说明

### API配置
- **DeepSeek API**：高质量对话和评估
- **本地API**：降低成本的评估方案
- **EasyChat API**：对话服务接口

### 测试用例
- **通用对话**：日常交流场景
- **知识问答**：专业知识查询
- **创意写作**：文本生成任务
- **技术支持**：问题解决场景

## 开发指南

### 添加新的测试用例
1. 编辑 `tests/test_cases.json`
2. 按照现有格式添加测试用例
3. 运行评估验证效果

### 自定义评估维度
1. 修改 `easyEval2/config/prompts.py`
2. 调整评估提示词
3. 更新评分逻辑

### 扩展API功能
1. 修改 `easychat/main.py`
2. 添加新的API端点
3. 更新文档说明

## 注意事项

1. **API密钥安全**：请妥善保管API密钥，不要提交到版本控制
2. **成本控制**：使用DeepSeek API时注意控制调用频率
3. **本地API**：推荐优先使用本地API进行开发和测试
4. **评估频率**：生产环境建议定期而非实时评估

## 许可证

MIT License - 详见各子项目的LICENSE文件

## 贡献

欢迎提交Issue和Pull Request来改进项目！

项目仓库：https://github.com/Coldplay-now/EasyEvaluator.git

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue：https://github.com/Coldplay-now/EasyEvaluator/issues
- 发送邮件至项目维护者

---

**项目状态**：活跃开发中 | **版本**：v0.1 | **最后更新**：2025年9月

**快速导航**：
- [EasyChat 对话系统](./easychat/README.md)
- [easyEval 快速评估](./easyEval/README.md)
- [easyEval2 智能评估](./easyEval2/README.md)