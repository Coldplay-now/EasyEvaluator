# 本地API使用指南

## 概述

easyEval2 现在支持使用本地API进行语义评估，无需依赖外部的DeepSeek API服务。这对于离线环境或希望使用自己部署的AI模型的用户非常有用。

## 功能特性

- ✅ 支持本地API服务调用
- ✅ 兼容现有的评估流程
- ✅ 自动处理响应格式转换
- ✅ 完整的错误处理和重试机制
- ✅ 连接状态检测

## 使用方法

### 1. 启动本地API服务

首先确保你的本地API服务正在运行。例如，如果你使用的是EasyChat项目：

```bash
cd ../easychat
python main.py --api
```

默认情况下，服务会在 `http://localhost:8000` 启动。

### 2. 使用本地API进行评估

#### 基本用法

```bash
# 使用本地API进行评估
python main.py --use-local-api

# 指定自定义的本地API地址
python main.py --use-local-api --local-api-url http://localhost:9000

# 限制评估数量
python main.py --use-local-api --limit 5

# 干运行模式（仅测试连接）
python main.py --use-local-api --dry-run
```

#### 高级用法

```bash
# 详细模式输出
python main.py --use-local-api --verbose

# 指定输出文件
python main.py --use-local-api --output results/my_evaluation.json

# 过滤特定场景
python main.py --use-local-api --filter-scenario knowledge

# 跳过特定测试用例
python main.py --use-local-api --skip general_001,creative_002
```

## 命令行参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `--use-local-api` | 启用本地API模式 | False |
| `--local-api-url` | 本地API服务地址 | http://localhost:8000 |
| `--limit` | 限制评估的测试用例数量 | 无限制 |
| `--dry-run` | 干运行模式，仅测试连接 | False |
| `--verbose` | 详细输出模式 | False |
| `--output` | 指定输出文件路径 | 自动生成 |

## 配置说明

### 本地API客户端配置

本地API客户端支持以下配置选项：

```python
# 在 src/local_api_client.py 中可以调整这些参数
class LocalAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.max_retries = 3          # 最大重试次数
        self.request_timeout = 30     # 请求超时时间（秒）
        self.request_interval = 1     # 请求间隔时间（秒）
```

### 环境变量

你也可以通过环境变量配置本地API地址：

```bash
export LOCAL_API_URL=http://localhost:8000
python main.py --use-local-api
```

## 响应格式处理

本地API客户端能够智能处理不同格式的响应：

1. **JSON格式响应**：直接解析评估结果
2. **文本格式响应**：自动提取分数和评估理由
3. **备用处理**：如果无法提取有效分数，返回默认评估结果

## 故障排除

### 常见问题

1. **连接失败**
   ```
   错误：API连接失败
   解决：检查本地API服务是否正在运行，确认地址和端口正确
   ```

2. **响应格式错误**
   ```
   警告：无法从响应中提取有效分数
   解决：检查本地API返回的响应格式，确保包含评估信息
   ```

3. **超时错误**
   ```
   错误：请求超时
   解决：增加超时时间或检查网络连接
   ```

### 调试模式

启用详细日志输出：

```bash
python main.py --use-local-api --verbose
```

### 测试连接

使用干运行模式测试API连接：

```bash
python main.py --use-local-api --dry-run
```

## 性能对比

| 特性 | DeepSeek API | 本地API |
|------|-------------|----------|
| 网络依赖 | 需要 | 不需要 |
| 响应速度 | 取决于网络 | 通常更快 |
| 成本 | 按使用付费 | 免费 |
| 隐私性 | 数据上传到云端 | 数据本地处理 |
| 模型质量 | 高质量商业模型 | 取决于本地模型 |

## 示例输出

使用本地API的评估输出示例：

```
🚀 开始语义相似度评估...
⠋ ✓ 加载了 15 个测试用例
📋 将评估 3 个测试用例
💾 结果已保存到: results/evaluation_20250915_122554.json

==================================================
语义评估结果摘要
==================================================
总测试数: 3
平均分数: 76.3
最高分数: 92
最低分数: 65.0

分数分布:
  优秀 (90-100): 1 个
  良好 (80-89):  0 个
  一般 (70-79):  1 个
  较差 (60-69):  1 个
  很差 (0-59):   0 个

性能指标:
  成功率: 100.0%
  总API时间: 22.40 秒
  平均API时间: 7.47 秒
==================================================
🎉 评估完成！
```

## 扩展开发

如果你需要支持其他类型的本地API，可以参考 `src/local_api_client.py` 的实现，创建自己的客户端类。

主要需要实现的方法：
- `chat_completion()`: 聊天完成请求
- `evaluate_semantic_similarity()`: 语义相似度评估
- `test_connection()`: 连接测试

---

**注意**：本地API功能需要配合支持聊天API的本地服务使用，如EasyChat项目或其他兼容的AI服务。