import gradio as gr
import time

def generate():
    for i in range(10):
        time.sleep(1)
        yield f"Step {i}"

def new_chat():
    return "New Chat"

with gr.Blocks() as demo:
    out = gr.Textbox()
    btn = gr.Button("Generate")
    gen_event = btn.click(generate, outputs=out)
    
    new_btn = gr.Button("New Chat")
    new_btn.click(new_chat, outputs=out, cancels=[gen_event])

demo.launch()