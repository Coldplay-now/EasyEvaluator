# easyEval2 - 语义相似度评估系统

基于DeepSeek API的智能对话质量评估工具，专为EasyChat项目设计的语义相似度评估系统。这是 [easyEval](../easyEval/) 项目的升级版本，提供更智能的AI驱动评估能力。

## 🎯 项目特点

- **智能评估**: 使用DeepSeek AI模型进行语义相似度分析
- **多维度评分**: 从相关性、准确性、完整性等5个维度评估
- **场景适配**: 支持通用、知识、创意、技术等多种评估场景
- **自动化流程**: 一键运行，自动获取回答并评估
- **详细报告**: 生成包含统计分析的详细评估报告
- **🆕 进度条显示**: 实时显示评估进度和时间估算
- **🆕 Markdown报告**: 自动生成易读的Markdown格式摘要报告
- **🆕 本地API支持**: 支持本地API模式，降低成本

## 📁 项目结构

```
easyEval2/
├── config/
│   ├── config.py          # 配置管理
│   └── prompts.py         # 系统提示词管理
├── src/
│   ├── deepseek_client.py # DeepSeek API客户端
│   ├── local_api_client.py # 本地API客户端
│   └── semantic_eval.py   # 核心评估引擎
├── tests/
│   └── test_cases.json    # 测试用例（50+个用例）
├── results/               # 评估结果输出
│   ├── *.json            # 详细评估结果
│   └── *.md              # Markdown摘要报告
├── logs/                  # 日志文件
├── main.py               # 主程序入口
├── .env                  # 环境配置
├── requirements.txt      # 依赖包
├── LOCAL_API_USAGE.md    # 本地API使用说明
└── README.md            # 项目说明
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目（如果需要）
cd easyEval2

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑 `.env` 文件，添加您的DeepSeek API密钥：

```bash
# DeepSeek API 配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

### 3. 运行评估

```bash
# 使用默认设置运行评估
python main.py

# 使用本地API模式（推荐，成本更低）
python main.py --use-local-api

# 限制测试用例数量
python main.py --limit 10

# 使用DeepSeek API模式
python main.py --use-deepseek-api

# 组合使用
python main.py --use-local-api --limit 5
```

## 📊 评估维度

系统从以下5个维度评估对话质量：

| 维度 | 权重 | 说明 |
|------|------|------|
| **相关性** | 30% | 回答是否直接回应了问题 |
| **准确性** | 25% | 回答内容是否正确 |
| **完整性** | 20% | 回答是否完整 |
| **有用性** | 15% | 回答是否对用户有帮助 |
| **表达质量** | 10% | 语言是否清晰流畅 |

### 评分标准

- **90-100分**: 优秀 - 完全符合预期
- **80-89分**: 良好 - 基本符合预期  
- **70-79分**: 一般 - 部分符合预期
- **60-69分**: 较差 - 勉强相关
- **0-59分**: 很差 - 不相关或错误

## 🎭 评估场景

系统支持多种评估场景，每种场景有不同的评估重点：

### 通用场景 (general)
- 适用于一般性对话
- 平衡各个评估维度

### 知识问答 (knowledge)
- 更注重准确性
- 要求回答基于事实
- 避免主观臆测

### 创意内容 (creative)
- 更注重表达质量和有用性
- 鼓励创意和个性化
- 准确性要求适当放宽

### 技术问题 (technical)
- 更注重准确性和完整性
- 要求具体技术细节
- 代码示例语法正确

## 📝 测试用例格式

```json
{
  "id": "test_001",
  "question": "用户问题",
  "category": "问题分类",
  "scenario": "评估场景",
  "expected_aspects": ["期望要点1", "期望要点2"],
  "priority": "high|medium|low"
}
```

### 字段说明

- `id`: 测试用例唯一标识
- `question`: 要测试的问题
- `category`: 问题分类（用于统计）
- `scenario`: 评估场景（general/knowledge/creative/technical）
- `expected_aspects`: 期望回答包含的要点
- `priority`: 优先级（high/medium/low）

## 📈 评估报告

系统自动生成两种格式的评估报告：

### 1. JSON详细报告 (evaluation_YYYYMMDD_HHMMSS.json)
包含完整的评估数据和统计信息：
```json
{
  "test_id": "test_001",
  "question": "用户问题",
  "answer": "AI回答",
  "semantic_score": 85,
  "evaluation_reason": "评估理由",
  "dimension_scores": {
    "relevance": 26,
    "accuracy": 22,
    "completeness": 18,
    "usefulness": 13,
    "expression": 8
  },
  "scenario": "general",
  "timestamp": "2024-01-15T10:30:00"
}
```

### 2. Markdown摘要报告 (evaluation_YYYYMMDD_HHMMSS.md)
易读的摘要报告，包含：
- 📊 总体统计信息
- 📈 分数分布图表
- 🎭 场景统计分析
- ⚡ 性能指标
- 📝 详细结果列表

### 统计摘要
- 平均分数、最高分、最低分
- 分数分布（优秀/良好/一般/较差/很差）
- 场景统计（各场景的测试数量和平均分）
- 性能指标（成功率、API响应时间等）

## ⚙️ 配置选项

### 环境变量配置

```bash
# DeepSeek API配置
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# 本地API配置（推荐）
LOCAL_API_BASE_URL=http://localhost:11434
LOCAL_API_MODEL=qwen2.5:7b

# 请求配置
MAX_RETRIES=3              # 最大重试次数
REQUEST_TIMEOUT=30         # 请求超时时间（秒）
REQUEST_INTERVAL=1         # 请求间隔（秒）

# EasyChat配置
EASYCHAT_URL=http://localhost:8000  # EasyChat服务地址
EASYCHAT_TIMEOUT=10        # EasyChat请求超时

# 日志配置
LOG_LEVEL=INFO             # 日志级别
LOG_FILE=logs/semantic_eval.log  # 日志文件
```

### 命令行参数

```bash
python main.py [选项]

选项:
  --use-local-api        使用本地API模式（推荐）
  --use-deepseek-api     使用DeepSeek API模式
  --limit N              限制测试用例数量
  -h, --help             显示帮助信息

示例:
  python main.py --use-local-api --limit 10
  python main.py --use-deepseek-api
```

## 🔧 开发指南

### 添加新的评估场景

1. 在 `config/prompts.py` 中添加新场景：

```python
'new_scenario': {
    'name': '新场景名称',
    'system_prompt': SYSTEM_PROMPT + """
特别注意：
- 新场景的特殊要求
- 评估重点调整
""",
    'description': '场景描述'
}
```

2. 在测试用例中使用新场景：

```json
{
  "scenario": "new_scenario",
  ...
}
```

### 自定义评估逻辑

继承 `SemanticEvaluator` 类并重写相关方法：

```python
class CustomEvaluator(SemanticEvaluator):
    def evaluate_single(self, test_case):
        # 自定义评估逻辑
        result = super().evaluate_single(test_case)
        # 添加自定义处理
        return result
```

### 集成其他AI服务

实现新的客户端类：

```python
class NewAIClient:
    def evaluate_semantic_similarity(self, question, answer, scenario):
        # 实现新的AI服务调用
        pass
```

## 🐛 故障排除

### 常见问题

**Q: API调用失败**
- 检查API密钥是否正确配置
- 确认网络连接正常
- 查看日志文件获取详细错误信息

**Q: EasyChat连接失败**
- 确认EasyChat服务正在运行
- 检查URL配置是否正确
- 系统会自动使用模拟回答进行测试

**Q: 评估结果不准确**
- 检查测试用例的场景设置
- 调整系统提示词
- 增加expected_aspects的详细程度

**Q: 性能问题**
- 调整REQUEST_INTERVAL增加请求间隔
- 减少并发请求数量
- 使用更小的测试用例集

### 调试模式

```bash
# 启用详细日志
python src/semantic_eval.py --verbose

# 测试API连接
python src/deepseek_client.py

# 验证配置
python config/config.py
```

## 📊 性能指标

### 基准性能
- 单次评估时间: < 10秒
- 批量评估支持: 20-50个测试用例
- API调用成功率: > 95%
- 内存使用: < 100MB
- 进度条实时更新，时间估算准确

### 性能对比

| 模式 | 成本 | 速度 | 准确性 | 推荐场景 |
|------|------|------|--------|----------|
| 本地API | 免费 | 快 | 高 | 日常开发测试 |
| DeepSeek API | 付费 | 中等 | 很高 | 生产环境评估 |

### 优化建议
- 优先使用本地API模式降低成本
- 合理设置请求间隔避免API限流
- 使用进度条监控评估进度
- 查看Markdown报告快速了解结果

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目链接: [https://github.com/your-username/easyEval2](https://github.com/your-username/easyEval2)
- 问题反馈: [Issues](https://github.com/your-username/easyEval2/issues)

## 🙏 致谢

- [DeepSeek](https://www.deepseek.com/) - 提供强大的AI模型支持
- [OpenAI Python SDK](https://github.com/openai/openai-python) - API客户端库
- EasyChat项目团队 - 目标评估系统

## 🔄 项目演进

### 与 easyEval 的关系

| 特性 | easyEval (v1) | easyEval2 (v2) |
|------|---------------|----------------|
| 评估方式 | 关键词匹配 | AI语义分析 |
| 评估维度 | 完成率 | 5维度评分 |
| 报告格式 | JSON + TXT | JSON + Markdown |
| 成本 | 免费 | 本地免费/云端付费 |
| 准确性 | 基础 | 高级 |
| 适用场景 | 快速验证 | 深度分析 |

### 使用建议

1. **开发阶段**: 使用 easyEval 进行快速功能验证
2. **测试阶段**: 使用 easyEval2 本地API模式进行详细评估
3. **生产阶段**: 使用 easyEval2 DeepSeek API模式获得最高准确性
4. **全面评估**: 两个工具结合使用，获得多维度评估结果

## 🆕 最新功能

### v2.1.0 更新内容
- ✅ **进度条显示**: 使用rich库实现美观的进度条
- ✅ **Markdown报告**: 自动生成易读的摘要报告
- ✅ **本地API支持**: 支持Ollama等本地API，降低成本
- ✅ **双模式运行**: 灵活选择本地或云端API
- ✅ **时间估算**: 实时显示剩余时间和完成进度
- ✅ **用户体验优化**: 更友好的界面和输出格式

---

**注意**: 这是一个学习型项目，专注于语义评估技术的探索和实践。使用前请确保已正确配置API密钥和相关服务。推荐优先使用本地API模式进行开发和测试。