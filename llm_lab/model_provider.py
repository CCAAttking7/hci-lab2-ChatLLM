import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MAX_IMAGE_BYTES = 10 * 1024 * 1024


class ModelProvider:
    def __init__(self):
        # initialize two clients
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
                "context": 128000,  # 128K context window
                "max_out": 65536,  # 64K output tokens
                "multimodal": False,
            },
            "Qwen3-Max": {
                "id": "qwen3-max",
                "client": "Qwen",
                "display": "Qwen3-Max (Thinking)",
                "context": 262144,  # 262K context window
                "max_out": 32768,
                "multimodal": False,
            },
            "Qwen3.5-Plus": {
                "id": "qwen3.5-plus",
                "client": "Qwen",
                "display": "Qwen3.5-Plus (VL/1M)",
                "context": 1000000,  # 1M context window
                "max_out": 65536,
                "multimodal": True,  # supports image/video input
            },
        }

    # Convert image to base64 string
    def encode_image(self, image_path):
        if not image_path:
            raise ValueError("未获取到图片路径")
        try:
            size = os.path.getsize(image_path)
        except OSError as e:
            raise ValueError(f"无法读取图片文件: {str(e)}") from e
        if size > MAX_IMAGE_BYTES:
            raise ValueError("图片过大，请上传不超过 10MB 的图片")
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except OSError as e:
            raise ValueError(f"无法打开图片文件: {str(e)}") from e

    def chat(self, model_key, messages, temperature=0.8, image_path=None):
        info = self.model_info[model_key]
        client = self.clients[info["client"]]

        # handle image input
        import copy
        processed_messages = copy.deepcopy(messages)

        if info.get("multimodal"):
            for msg in processed_messages:
                if isinstance(msg.get("content"), list):
                    for item in msg["content"]:
                        # Convert Gradio's 'file' format to OpenAI's 'image_url' format
                        if item.get("type") == "file" and isinstance(item.get("file"), dict):
                            path = item["file"].get("path", "")
                            if path:
                                try:
                                    base64_image = self.encode_image(path)
                                    item["type"] = "image_url"
                                    item["image_url"] = {"url": f"data:image/jpeg;base64,{base64_image}"}
                                    del item["file"]
                                except Exception as e:
                                    print(f"Encode image failed for {path}: {e}")
                                    raise e
                        # Support existing 'image_url' format just in case
                        elif item.get("type") == "image_url" and isinstance(item.get("image_url"), dict):
                            url = item["image_url"].get("url", "")
                            if url and not url.startswith("http") and not url.startswith("data:"):
                                try:
                                    base64_image = self.encode_image(url)
                                    item["image_url"]["url"] = f"data:image/jpeg;base64,{base64_image}"
                                except Exception as e:
                                    print(f"Encode image failed for {url}: {e}")
                                    raise e

        # Sanitize for non-multimodal models to prevent crashes if history has images
        if not info.get("multimodal"):
            for msg in processed_messages:
                if isinstance(msg.get("content"), list):
                    text_parts = [str(item.get("text", "")) for item in msg["content"] if item.get("type") == "text"]
                    msg["content"] = "\n".join(text_parts)

        kwargs = {
            "model": info["id"],
            "messages": processed_messages,
            "temperature": temperature,
            "stream": True,
        }
        if temperature == 0:
            kwargs["seed"] = 42

        # Streaming request
        response = client.chat.completions.create(**kwargs)
        return response, info

    # Estimate token usage for context window, using a weighted estimation instead of tokenizer to avoid overhead
    def estimate_usage(self, messages, has_image=False):
        """
        Calculation logic:
        1. Text: Uses a mixed weighted estimation. Chinese has higher token density due to encoding characteristics.
        2. Image: Qwen3.5-Plus multimodal patch consumes a fixed amount of tokens.
        3. Purpose: Calculate the current conversation's "context usage" to check against 128K/262K/1M limits.
        """
        total_text = ""
        detected_image = False
        # Extract all text content
        for m in messages:
            content = m["content"]
            if isinstance(content, str):
                total_text += content
            elif isinstance(content, list):
                for item in content:
                    if item.get("type") == "text":
                        total_text += item.get("text", "")
                    elif item.get("type") == "image_url" or item.get("type") == "file":
                        detected_image = True

        # Count Chinese and other characters
        chinese_chars = len([c for c in total_text if "\u4e00" <= c <= "\u9fff"])
        other_chars = len(total_text) - chinese_chars

        # Chinese: about 1.5 tokens per character (conservative estimate)
        # English: about 1.3 tokens per word (assuming 4 chars/word)
        # Safety factor: multiply by 1.2 to prevent overflow
        text_tokens = (chinese_chars * 1.5 + (other_chars / 4) * 1.3) * 1.2

        # Image token compensation: multimodal input has a base and pixel cost, here using 1024 tokens as empirical value for 720P
        image_tokens = 1024 if (has_image or detected_image) else 0
        current_total = int(text_tokens + image_tokens)
        return current_total
