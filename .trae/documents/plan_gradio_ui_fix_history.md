## 总结

本计划，新增 1 个进阶功能：历史记录管面向你当前的 Gradio LLM 项目，先修复你反馈的 4 个网页问题（重复渲染、上传无效、对比面板重复、排版不好看），并在不改变现有“至少两家模型 API（DeepSeek + Qwen）”能力前提下理（会话列表，可切换继续聊），同时把整体排版调整为更接近 Codex/ChatGPT 的“左侧会话栏 + 右侧主聊天区”。

## 当前现状分析（基于仓库实际代码）

- Gradio 入口： [app.py](file:///d:/Dev_w/Courses/Human-Computer%20Interaction/hci-lab2-llm/app.py)
- 模型封装： [model\_provider.py](file:///d:/Dev_w/Courses/Human-Computer%20Interaction/hci-lab2-llm/model_provider.py)
- 依赖： [pyproject.toml](file:///d:/Dev_w/Courses/Human-Computer%20Interaction/hci-lab2-llm/pyproject.toml)（gradio>=6.10.0, openai>=2.30.0, python-dotenv）
- README：当前为空文件（0 行），不满足交付要求

已定位到与问题高度相关的代码点：

1. 页面/面板重复（高概率）

- `with gr.Blocks(...) as demo:` 后又写了 `with demo:`（事件绑定在二次上下文中），在热重载/queue 场景下可能导致组件树/事件重复挂载或触发两次。
  - 位置： [app.py:L161-L239](file:///d:/Dev_w/Courses/Human-Computer%20Interaction/hci-lab2-llm/app.py#L161-L239)

1. 上传图片/输入提交不生效（明确 bug + 兼容性风险）

- `MultimodalTextbox` 的 `message["files"][0]` 不一定是字符串路径，常见是 dict/对象；当前直接把 `files[0]` 传给 `open()` 会报错或导致提交失败。
  - 取文件： [app.py:L13-L17](file:///d:/Dev_w/Courses/Human-Computer%20Interaction/hci-lab2-llm/app.py#L13-L17)
  - 读文件： [model\_provider.py:L51-L55](file:///d:/Dev_w/Courses/Human-Computer%20Interaction/hci-lab2-llm/model_provider.py#L51-L55)
- `token_bar` 是 Textbox，但回调输出的是 `usage/limit` 的 float（且 label 写百分比），容易造成组件更新异常。
  - 位置： [app.py:L172-L174](file:///d:/Dev_w/Courses/Human-Computer%20Interaction/hci-lab2-llm/app.py#L172-L174)、[app.py:L46-L60](file:///d:/Dev_w/Courses/Human-Computer%20Interaction/hci-lab2-llm/app.py#L46-L60)

1. “单个 + 对比版本面板重复”

- 与 (1) 的重复挂载/重复事件绑定同源，且目前对比模式的输入/输出组件布局缺少统一容器与清晰的状态管理，容易在渲染时产生“看起来像重复区域”的效果。

1. 排版不好看

- 当前为“左侧参数栏 + 右侧 Tabs”，但缺少会话/历史信息，交互操作不集中（没有明显的发送/清空/新会话），并排对比区高度/标签也较粗糙。

## 需求与决策（根据你的补充偏好）

- 进阶功能选择：历史记录管理（会话列表，可切换继续聊）
- 布局风格：左侧会话栏
- 对比模式：并排两列（A/B）

## 拟议改动（按文件逐项说明：做什么 / 为什么 / 怎么做）

### 1) [app.py](file:///d:/Dev_w/Courses/Human-Computer%20Interaction/hci-lab2-llm/app.py)

#### 1.1 修复重复渲染/重复事件绑定

- 做什么：移除 `with demo:` 的二次 Blocks 上下文，事件绑定直接写在 Blocks 定义作用域内；同时梳理组件创建与绑定顺序，保证每个组件只创建一次、每个事件只绑定一次。
- 为什么：避免在 queue/热重载下重复挂载组件树或重复注册回调导致“上下页面重复/面板重复”。
- 怎么做：
  - 删除 `with demo:` 包裹层，将 submit 事件绑定代码左移一层。
  - 若仍存在重复现象，补充 `if __name__ == "__main__":` 之外不做任何 `.launch()` 或 side effects（当前已符合）。

#### 1.2 修复 MultimodalTextbox 上传对象兼容性 + 模型能力一致性

- 做什么：
  - 将上传文件项标准化为真实文件路径（兼容 str / dict(path) / 有 path 属性对象）。
  - 当用户上传图片但所选模型不支持多模态时：在 UI 输出中给出明确提示，并且不把图片计入 token 估算、不把图片传给模型。
- 为什么：解决“上传后提交失败/无法上传/无效”的根因，且避免“明明不支持图片却静默丢弃”的误导。
- 怎么做：
  - 在 `single_chat_logic` 中增加 `normalize_image_path()`（或内联逻辑）：
    - `files = message.get("files") or []`
    - 支持 `str`、`{"path": ...}`、`obj.path`
  - 结合 `provider.model_info[model_key]["multimodal"]` 判断是否允许图片：
    - 若不允许，构造一个用户可见的提示消息，并将 `image_path=None`、`has_image=False`。

#### 1.3 修复 Token 监控输出类型，统一显示逻辑

- 做什么：把 `token_bar` 从 Textbox 调整为更贴合的组件（例如 `gr.Slider(0, 1, ...)` 或 `gr.Progress` 风格的替代），或者保持 Textbox 但输出百分比字符串。
- 为什么：避免输出类型不匹配引发的 UI 更新异常，间接影响“提交没反应”的体验。
- 怎么做（定案）：
  - 采用 `gr.Slider(0, 1, value=0, step=0.01, interactive=False)` 显示占用比例（0\~1），同时 `token_info` 显示 `Token: {usage}/{limit}`。
  - 所有 `yield` 分支保证输出类型一致。

#### 1.4 重新布局为“左侧会话栏 + 右侧主区”，并优化对比模式并排显示

- 做什么：
  - 左侧：会话列表（历史记录管理）、新建会话、删除会话、清空当前会话。
  - 右侧：Tabs（标准模式 / 对比模式），顶部小工具区（模型选择、温度、状态）。
  - 对比模式输出固定为两列，并统一高度、标题与间距。
- 为什么：匹配你希望参考的 Codex 风格，解决“排版不好看”，同时提供可用的历史记录管理。
- 怎么做（核心组件设计）：
  - 使用 `gr.State` 持有会话数据结构（内存态）：
    - `sessions: list[dict]`，每个 session 至少包含：
      - `id`（字符串或递增序号）
      - `title`（例如“会话 1 / 会话 2”）
      - `single_history`（Chatbot value）
      - `compare_history_a` / `compare_history_b`
      - `single_model_key`、`compare_model_a_key`、`compare_model_b_key`、`temperature`（可选，便于切换时恢复）
    - `active_session_id`
  - 左侧会话列表使用 `gr.Radio` 或 `gr.Dropdown` 展示（默认 Radio 更像侧边栏列表）。
  - 会话切换事件：
    - 选择会话 -> 将对应 history 回填到右侧 Chatbot（标准/对比两个都回填）。
  - 新建会话事件：
    - 追加一个空 history 的 session，并切换为 active。
  - 删除会话事件：
    - 删除当前会话；若仅剩 1 个则重置为空会话。
  - 清空当前会话事件：
    - 将 active session 的 history 置空，并更新右侧 Chatbot。

#### 1.5 统一“标准模式”与“对比模式”的提交行为与状态更新

- 做什么：
  - 标准模式：提交后将当前轮次追加到 active session 的 `single_history`，并持续流式更新；结束后保持状态一致。
  - 对比模式：提交后将同一输入分别追加到 A/B history，并持续并行更新；结束后写回 session。
  - 为两种模式补充显式“发送”按钮（同时保留 Enter 提交），以及“停止生成”（利用 queue 的取消能力或提供 stop 按钮）——若 Gradio 版本支持则做，否则先只做发送/清空。
- 为什么：减少“看不出是否提交成功”的困扰，增强交互可控性；同时保证历史记录功能可靠。
- 怎么做（实现策略）：
  - 将会话状态读写抽成纯函数：
    - `get_active_session(sessions, active_id)`
    - `update_active_session_history(...)`
  - 回调签名尽量只输入/输出必要组件与 state，避免把 Chatbot 既当输入又当输出造成隐性状态混乱。

### 2) [model\_provider.py](file:///d:/Dev_w/Courses/Human-Computer%20Interaction/hci-lab2-llm/model_provider.py)

#### 2.1 让 encode\_image 更健壮（可选但推荐）

- 做什么：在读取图片时对不存在路径/权限错误给出更清晰的异常信息；必要时限制文件大小（防止误传超大文件）。
- 为什么：上传链路问题定位更清晰，减少“提交失败但不知道原因”。
- 怎么做：
  - 在 `encode_image` 中捕获 `FileNotFoundError` / `OSError`，抛出更友好的异常文本（由上层捕获显示）。
  - 保持不记录任何 API Key/敏感信息。

### 3) [README.md](file:///d:/Dev_w/Courses/Human-Computer%20Interaction/hci-lab2-llm/README.md)

- 做什么：补齐交付要求的运行说明与环境变量配置说明。
- 为什么：课程要求必须提供 README 指导运行；当前 README 为空。
- 怎么做（内容要点）：
  - 项目简介：Gradio 可视化 + 两家模型（DeepSeek + Qwen）API 调用
  - 环境准备：Python 版本、安装依赖（uv 或 pip 两种方式择一，优先与仓库当前一致）
  - 配置 `.env`：
    - `DEEPSEEK_API_KEY=...`
    - `QWEN_API_KEY=...`
  - 启动方式：`python app.py`
  - 功能说明：标准模式（含图片仅 Qwen3.5-Plus）、对比模式、历史记录管理
  - 常见问题：上传图片无效的原因与解决（切换到多模态模型）

## 假设与边界

- 会话历史记录管理默认做“本次运行内存态”，不做跨重启持久化（除非你额外要求写入本地文件）。
- 不新增第三家模型；保持“至少两家”并稳定可用（DeepSeek + Qwen）。
- 不引入新的第三方 UI 框架；仅使用当前依赖（Gradio / OpenAI SDK / dotenv）。

## 验证方式（实现后需要逐条检查）

1. 启动应用后页面不出现上下重复区域；标准/对比两个 Tab 各只有一套组件。
2. 标准模式：
   - 仅文字输入可正常提交并流式输出。
   - 上传图片时：
     - 选择 Qwen3.5-Plus 能正常调用（模型返回后端不报错）。
     - 选择非多模态模型会出现明确提示，不会卡死/报错。
3. 对比模式：
   - 同一输入触发 A/B 两列同时更新；不出现重复输出面板。
4. 历史记录管理：
   - 新建会话后聊天记录独立；
   - 切换会话能正确回填历史并可继续聊；
   - 清空/删除行为符合预期。
5. Token 监控：
   - 显示值与组件类型匹配，不因输出类型不一致导致提交无响应。
6. README：
   - 从零开始按 README 步骤可以跑起来（仅需填入 API Key）。

