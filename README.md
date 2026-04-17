## HCI Lab2：LLM Gradio 交互平台

本项目使用 Gradio 构建可视化页面，通过 API 调用至少两家不同公司的大模型（DeepSeek + 通义千问 Qwen），支持：

- 标准模式：单模型对话（支持流式输出；图片仅 Qwen3.5-Plus 支持）
- 对比模式：同一输入并排对比两个模型输出
- 历史记录管理：左侧会话列表，可新建/删除/清空会话并切换继续聊天

## 环境要求

- Python >= 3.12
- 已获取 API Key（DeepSeek + Qwen）

## 安装依赖

方式 A（推荐，若你使用 uv）：

```bash
uv sync
```

方式 B（使用 pip）：

```bash
pip install --upgrade gradio openai python-dotenv
```

## 配置环境变量

在项目根目录创建 `.env` 文件，内容示例：

```bash
DEEPSEEK_API_KEY=你的_deepseek_key
QWEN_API_KEY=你的_qwen_key
```

## 运行

```bash
python app.py
```

启动后终端会输出本地访问地址（例如 http://127.0.0.1:7860）。

## 使用说明

- 标准模式：选择模型后输入问题即可；如需上传图片，请切换到 `Qwen3.5-Plus`
- 对比模式：选择模型 A / 模型 B，在输入框输入问题后发送
- 会话管理：左侧可新建会话、删除会话或清空当前会话

## 常见问题

- 上传了图片但没生效：请确认当前模型为 `Qwen3.5-Plus`，其他模型会自动忽略图片并提示切换模型
