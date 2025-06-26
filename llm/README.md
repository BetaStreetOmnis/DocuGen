# LLM 模块

本模块提供了统一的大语言模型接口，支持本地模型和第三方API接口调用。配置通过环境变量管理。

## 配置

在项目根目录的`.env`文件中配置以下环境变量：

```
# 默认模型类型: local 或 third_party
DEFAULT_LLM_TYPE=local

# 本地模型配置
LOCAL_LLM_BASE_URL=http://localhost:8000
LOCAL_LLM_API_KEY=your_local_api_key_if_needed
LOCAL_LLM_DEFAULT_MODEL=deepseek-coder
LOCAL_LLM_DEFAULT_TEMPERATURE=0.7
LOCAL_LLM_DEFAULT_MAX_TOKENS=1000

# 第三方模型配置（如OpenAI）
THIRD_PARTY_LLM_BASE_URL=https://api.openai.com
THIRD_PARTY_LLM_API_KEY=your_openai_api_key
THIRD_PARTY_LLM_DEFAULT_MODEL=gpt-3.5-turbo
THIRD_PARTY_LLM_DEFAULT_TEMPERATURE=0.7
THIRD_PARTY_LLM_DEFAULT_MAX_TOKENS=1000
THIRD_PARTY_LLM_ORGANIZATION_ID=your_organization_id_if_needed
```

可以通过复制`.env.example`到`.env`然后修改来快速开始。

## 使用示例

### 使用统一接口类（推荐）

```python
from llm import LLMClient

# 创建统一客户端（使用环境变量中的默认设置）
client = LLMClient()

# 或者指定使用本地模型
client = LLMClient("local")

# 或者指定使用第三方模型
client = LLMClient("third_party")

# 准备消息
messages = [
    {"role": "system", "content": "你是一个有用的AI助手。"},
    {"role": "user", "content": "请简要介绍一下Python语言。"}
]

# 普通调用（使用默认参数）
response = client.chat(messages=messages)
print(response)

# 普通调用（自定义参数）
response = client.chat(
    messages=messages,
    model="gpt-4",  # 覆盖默认模型
    temperature=0.5,  # 覆盖默认温度
    max_tokens=800   # 覆盖默认最大token数
)
print(response)

# 流式调用
for chunk in client.stream_chat(messages=messages):
    print(chunk)

# 动态切换模型类型
client.switch_model_type("third_party")  # 从本地模型切换到第三方模型
response = client.chat(messages=messages)
```

### 使用工厂类创建客户端

```python
from llm import LLMFactory

# 使用默认配置创建客户端（根据DEFAULT_LLM_TYPE环境变量决定类型）
llm_client = LLMFactory.create_client()

# 指定使用本地模型
local_client = LLMFactory.create_client("local")

# 指定使用第三方模型
third_party_client = LLMFactory.create_client("third_party")
```

### 直接调用模型

```python
# 准备消息
messages = [
    {"role": "system", "content": "你是一个有用的AI助手。"},
    {"role": "user", "content": "请简要介绍一下Python语言。"}
]

# 普通调用
response = llm_client.chat_completion(
    messages=messages,
    temperature=0.7,
    max_tokens=500
)
print(response)

# 流式调用
for chunk in llm_client.stream_chat_completion(
    messages=messages,
    temperature=0.7,
    max_tokens=500
):
    print(chunk)
```

### 直接使用特定客户端

```python
from llm import LocalLLMClient, ThirdPartyLLMClient, LLMConfig

# 获取配置
local_config = LLMConfig.get_local_model_config()
third_party_config = LLMConfig.get_third_party_model_config()

# 创建本地模型客户端
local_client = LocalLLMClient(
    base_url=local_config["base_url"],
    api_key=local_config["api_key"]
)

# 创建第三方模型客户端
third_party_client = ThirdPartyLLMClient(
    base_url=third_party_config["base_url"],
    api_key=third_party_config["api_key"],
    organization_id=third_party_config["organization_id"]
)
```

## 依赖

- python-dotenv：用于加载环境变量
- requests：用于HTTP请求 