import gradio as gr
import os
from llm_lab import build_demo
from llm_lab.styles import APP_CSS

os.environ.setdefault("NO_PROXY", "127.0.0.1,localhost")
os.environ.setdefault("no_proxy", "127.0.0.1,localhost")

demo = build_demo()

if __name__ == "__main__":
    demo.queue().launch(
        theme=gr.themes.Soft(),
        server_name="127.0.0.1",
        css=APP_CSS,
    )
