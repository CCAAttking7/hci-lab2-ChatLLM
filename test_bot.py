import gradio as gr
def test():
    return [{"role": "user", "content": [{"type": "text", "text": "hello"}, {"type": "image_url", "image_url": {"url": "app.py"}}]}]

with gr.Blocks() as demo:
    cb = gr.Chatbot()
    btn = gr.Button()
    btn.click(test, outputs=cb)
demo.launch(server_port=7865)