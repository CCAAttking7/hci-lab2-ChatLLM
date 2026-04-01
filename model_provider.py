import os
import base64
from threading import current_thread
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class ModelProvider:
    def __init__(self):
        # 初始化两个客户端
        self.clients = {
            "DeepSeek": OpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com",
            ),
            "Qwen": OpenAI(
                api_key=os.getenv("QWEN_API_KEY"),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            ),
        }

        self.model_info = {
            "DeepSeek-R1": {
                "id": "deepseek-reasoner",
                "client": "DeepSeek",
                "display": "DeepSeek-V3.2 (Reasoner)",
                "context": 128000,  # 128K
                "max_out": 65536,  # 64K 输出
                "multimodal": False,
            },
            "Qwen3-Max": {
                "id": "qwen3-max",
                "client": "Qwen",
                "display": "Qwen3-Max (Thinking)",
                "context": 262144,  # 262K
                "max_out": 32768,
                "multimodal": False,
            },
            "Qwen3.5-Plus": {
                "id": "qwen3.5-plus",
                "client": "Qwen",
                "display": "Qwen3.5-Plus (VL/1M)",
                "context": 1000000,  # 1M 上下文
                "max_out": 65536,
                "multimodal": True,  # 支持图片/视频
            },
        }

    # 将图片转换为base64
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def chat(self, model_key, messages, temperature=0.8, image_path=None):
        info = self.model_info[model_key]
        client = self.clients[info["client"]]

        # 处理图片输入
        processed_messages = messages.copy()
        if image_path and info["multimodal"]:
            base64_image = self.encode_image(image_path)
            # 修改最后一轮用户输入的格式以包含图片
            last_msg = processed_messages.pop()
            processed_messages.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": last_msg["content"]},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            )

        # 流式请求
        response = client.chat.completions.create(
            model=info["id"], messages=messages, temperature=temperature, stream=True
        )
        return response, info

    # 上下文占有Token监控计数，利用加权的估计，不调用已有Tokenizer，防止增加开销
    def estimate_usage(self, messages, has_image=False):
        """
        计算逻辑说明：
        1. 文本：采用混合加权。中文由于编码特性，Token 密度高于英文。
        2. 图片：Qwen3.5-Plus 的多模态 Patch 消耗约为固定值。
        3. 目标：计算当前对话的“上下文占有量”，用于判断 128K/262K/1M 的限额。
        """
        total_text = ""
        # 提取所有的文本内容
        for m in messages:
            content = m["content"]
            if isinstance(content, str):
                total_text += content
            elif isinstance(content, list):
                for item in content:
                    if item["type"] == "text":
                        total_text += item["text"]

        # 统计中文和其他字符
        chinese_chars = len([c for c in total_text if "\u4e00" <= c <= "\u9fff"])
        other_chars = len(total_text) - chinese_chars

        # 中文：1字约 1.5 Token (保守估算)
        # 英文：1词约 1.3 Token (按4字符/词估算)
        # 综合安全系数：乘以 1.2 防止溢出
        text_tokens = (chinese_chars * 1.5 + (other_chars / 4) * 1.3) * 1.2

        # 图片Token补偿，多模态输入会有基础消耗和像素消耗，这里取1024个token作为720P的经验值
        image_tokens = 1024 if has_image else 0
        current_total = int(text_tokens + image_tokens)
        return current_total
