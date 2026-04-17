import gradio as gr

from llm_lab.controller import ChatController
from llm_lab.state import (
    clear_multimodal,
    clear_text,
    ensure_sessions,
    initial_sessions,
    session_choices,
)

MAX_HISTORY_ITEMS = 24


def build_history_slot_updates(sessions, active_session_id):
    sessions = ensure_sessions(sessions)
    updates = []
    for index in range(MAX_HISTORY_ITEMS):
        if index < len(sessions):
            session = sessions[index]
            is_active = session["id"] == active_session_id
            title = session["title"]
            updates.extend(
                [
                    gr.update(
                        value=title,
                        variant="secondary",
                    ),
                    gr.update(),
                    session["id"],
                    gr.update(visible=True, elem_classes=["history-item-wrap", "active"] if is_active else ["history-item-wrap"]),
                ]
            )
        else:
            updates.extend(
                [
                    gr.update(value="", variant="secondary"),
                    gr.update(),
                    "",
                    gr.update(visible=False, elem_classes=["history-item-wrap"]),
                ]
            )
    return updates


def build_demo(controller: ChatController | None = None):
    controller = controller or ChatController()
    sessions, active_session_id = initial_sessions()

    with gr.Blocks(
        title="LLM Multi-Model Lab",
        fill_width=True,
        fill_height=True,
    ) as demo:
        gr.Markdown("# 🤖 大模型交互实验平台")

        def dummy():
            return None

        demo.load(
            fn=dummy,
            inputs=None,
            outputs=None,
            js="""
            () => {
                setTimeout(() => {
                    const fileInputs = document.querySelectorAll('.multimodal-textbox input[type="file"]');
                    fileInputs.forEach(input => {
                        input.addEventListener('click', (e) => {
                            const isCompareMode = !!input.closest('#compare-input-row');
                            if (isCompareMode) {
                                e.preventDefault();
                                e.stopPropagation();
                                gradioApp().notify('对比模式仅支持文本输入。', duration=3000);
                                return false;
                            }
                            const modelSelect = document.querySelector('#standard-model-row select');
                            const currentModel = modelSelect ? modelSelect.value : '';
                            const nonMultimodal = ['DeepSeek-R1', 'Qwen3-Max'];
                            if (nonMultimodal.includes(currentModel)) {
                                e.preventDefault();
                                e.stopPropagation();
                                gradioApp().notify('当前模型不支持图片输入，请切换到 Qwen3.5-Plus。', duration=3000);
                                return false;
                            }
                        }, true);
                    });
                }, 1500);
            }
            """,
        )

        sessions_state = gr.State(sessions)
        active_session_id_state = gr.State(active_session_id)
        active_mode_state = gr.State("single")

        with gr.Row(equal_height=True, elem_id="app-shell"):
            with gr.Column(scale=1, min_width=280, elem_id="sidebar-shell"):
                gr.Markdown("<div class='sidebar-title'>最近对话</div>", elem_classes=["sidebar-title-md"])
                new_session_btn = gr.Button(
                    "＋ 新建对话",
                    elem_classes=["new-chat-btn"],
                )
                with gr.Column(elem_id="history-scroll"):
                    session_list = gr.Radio(
                        choices=session_choices(sessions),
                        value=active_session_id,
                        visible=False,
                    )
                    history_select_buttons = []
                    history_delete_buttons = []
                    history_id_boxes = []
                    history_rows = []
                    for index in range(MAX_HISTORY_ITEMS):
                        row = gr.Row(visible=index < len(sessions), elem_classes=["history-item-wrap", "active"] if index < len(sessions) and sessions[index]["id"] == active_session_id else ["history-item-wrap"])
                        with row:
                            select_btn = gr.Button(
                                value=sessions[index]["title"] if index < len(sessions) else "",
                                variant="secondary",
                                elem_classes=["history-item-button"],
                            )
                            delete_btn = gr.Button(
                                "🗑️",
                                elem_classes=["history-delete"],
                            )
                            id_box = gr.Textbox(
                                value=sessions[index]["id"] if index < len(sessions) else "",
                                visible=False,
                            )
                        history_rows.append(row)
                        history_select_buttons.append(select_btn)
                        history_delete_buttons.append(delete_btn)
                        history_id_boxes.append(id_box)

                with gr.Column(elem_classes=["sidebar-bottom"]):
                    with gr.Row(elem_id="history-actions-row"):
                        clear_session_btn = gr.Button(
                            "清空当前",
                            elem_classes=["clear-chat-btn"],
                        )
                    temp_slider = gr.Slider(
                        0,
                        2,
                        value=0.8,
                        step=0.1,
                        label="Temperature",
                        elem_classes=["compact-slider"],
                    )
                    token_html = gr.HTML(
                        controller.build_token_html(sessions[0], "single"),
                        elem_classes=["metrics-html"],
                    )
                    context_html = gr.HTML(
                        controller.build_context_html(sessions[0], "single"),
                        elem_classes=["metrics-html"],
                    )

            with gr.Column(scale=4, elem_id="main-shell"):
                with gr.Tabs(selected="single") as tabs:
                    with gr.Tab("标准模式", id="single") as single_tab:
                        with gr.Row(elem_id="standard-model-row"):
                            single_model_select = gr.Dropdown(
                                choices=list(controller.provider.model_info.keys()),
                                value="DeepSeek-R1",
                                label="当前模型（图片需切换到 Qwen3.5-Plus）",
                                scale=1,
                            )

                        single_chatbot = gr.Chatbot(
                            show_label=False,
                            height=350,
                            elem_classes=["chat-panel"],
                        )

                        single_input = gr.MultimodalTextbox(
                            placeholder="请输入文本或图片",
                            file_types=["image"],
                            lines=1,
                            max_lines=4,
                            show_label=False,
                            container=False,
                            submit_btn=True,
                            scale=10,
                        )

                    with gr.Tab("对比模式", id="compare") as compare_tab:
                        with gr.Row(elem_id="compare-model-row"):
                            m1_select = gr.Dropdown(
                                choices=list(controller.provider.model_info.keys()),
                                value="DeepSeek-R1",
                                label="模型 A",
                            )
                            m2_select = gr.Dropdown(
                                choices=list(controller.provider.model_info.keys()),
                                value="Qwen3-Max",
                                label="模型 B",
                            )

                        with gr.Row(elem_id="compare-chat-row"):
                            chatbot_a = gr.Chatbot(
                                show_label=False,
                                height=350,
                                elem_classes=["chat-panel"],
                            )
                            chatbot_b = gr.Chatbot(
                                show_label=False,
                                height=350,
                                elem_classes=["chat-panel"],
                            )

                        with gr.Row(elem_id="compare-input-row"):
                            compare_input = gr.MultimodalTextbox(
                                placeholder="输入同一个问题，对比两侧模型回答（对比模式仅支持文本）",
                                file_types=["image"],
                                lines=1,
                                max_lines=4,
                                show_label=False,
                                container=False,
                                submit_btn=True,
                                scale=10,
                            )

        common_outputs = [
            sessions_state,
            active_session_id_state,
            session_list,
            single_chatbot,
            chatbot_a,
            chatbot_b,
            single_model_select,
            m1_select,
            m2_select,
            temp_slider,
            token_html,
            context_html,
        ]
        history_outputs = []
        for select_btn, delete_btn, id_box, row in zip(
            history_select_buttons, history_delete_buttons, history_id_boxes, history_rows
        ):
            history_outputs.extend([select_btn, delete_btn, id_box, row])

        single_submit_event = single_input.submit(
            fn=controller.single_chat_submit,
            inputs=[
                single_input,
                sessions_state,
                active_session_id_state,
                single_model_select,
                temp_slider,
            ],
            outputs=[single_input, single_chatbot, token_html, context_html, sessions_state],
        )
        single_submit_event.then(
            fn=build_history_slot_updates,
            inputs=[sessions_state, active_session_id_state],
            outputs=history_outputs,
        )

        compare_submit_event = compare_input.submit(
            fn=controller.compare_chat_submit,
            inputs=[
                compare_input,
                sessions_state,
                active_session_id_state,
                m1_select,
                m2_select,
                temp_slider,
            ],
            outputs=[compare_input, chatbot_a, chatbot_b, token_html, context_html, sessions_state],
        )
        compare_submit_event.then(
            fn=build_history_slot_updates,
            inputs=[sessions_state, active_session_id_state],
            outputs=history_outputs,
        )

        for select_btn, delete_btn, id_box in zip(
            history_select_buttons, history_delete_buttons, history_id_boxes
        ):
            select_btn.click(
                fn=controller.on_select_session,
                inputs=[id_box, sessions_state, active_mode_state],
                outputs=common_outputs,
                cancels=[single_submit_event, compare_submit_event],
            ).then(
                fn=build_history_slot_updates,
                inputs=[sessions_state, active_session_id_state],
                outputs=history_outputs,
            )
            delete_btn.click(
                fn=controller.on_delete_session_by_id,
                inputs=[id_box, sessions_state, active_session_id_state, active_mode_state],
                outputs=common_outputs,
                cancels=[single_submit_event, compare_submit_event],
            ).then(
                fn=build_history_slot_updates,
                inputs=[sessions_state, active_session_id_state],
                outputs=history_outputs,
            )

        new_session_btn.click(
            fn=controller.on_new_session,
            inputs=[sessions_state, active_mode_state],
            outputs=common_outputs,
            cancels=[single_submit_event, compare_submit_event],
        ).then(
            fn=build_history_slot_updates,
            inputs=[sessions_state, active_session_id_state],
            outputs=history_outputs,
        )

        clear_session_btn.click(
            fn=controller.on_clear_active_session,
            inputs=[sessions_state, active_session_id_state, active_mode_state],
            outputs=common_outputs,
            cancels=[single_submit_event, compare_submit_event],
        ).then(
            fn=build_history_slot_updates,
            inputs=[sessions_state, active_session_id_state],
            outputs=history_outputs,
        )

        single_model_select.change(
            fn=controller.on_update_single_model,
            inputs=[
                single_model_select,
                sessions_state,
                active_session_id_state,
                active_mode_state,
            ],
            outputs=[
                sessions_state,
                token_html,
                context_html,
            ],
        )

        m1_select.change(
            fn=controller.on_update_compare_models,
            inputs=[
                m1_select,
                m2_select,
                sessions_state,
                active_session_id_state,
                active_mode_state,
            ],
            outputs=[sessions_state, token_html, context_html],
        )

        m2_select.change(
            fn=controller.on_update_compare_models,
            inputs=[
                m1_select,
                m2_select,
                sessions_state,
                active_session_id_state,
                active_mode_state,
            ],
            outputs=[sessions_state, token_html, context_html],
        )

        temp_slider.change(
            fn=controller.on_update_temperature,
            inputs=[temp_slider, sessions_state, active_session_id_state],
            outputs=[sessions_state],
        )

        def on_mode_change_wrapper(active_mode, sessions, active_session_id):
            res = controller.on_mode_change(active_mode, sessions, active_session_id)
            return (*res, active_mode)

        single_tab.select(
            fn=on_mode_change_wrapper,
            inputs=[gr.State("single"), sessions_state, active_session_id_state],
            outputs=common_outputs + [active_mode_state],
            cancels=[single_submit_event, compare_submit_event],
        ).then(
            fn=build_history_slot_updates,
            inputs=[sessions_state, active_session_id_state],
            outputs=history_outputs,
        )

        compare_tab.select(
            fn=on_mode_change_wrapper,
            inputs=[gr.State("compare"), sessions_state, active_session_id_state],
            outputs=common_outputs + [active_mode_state],
            cancels=[single_submit_event, compare_submit_event],
        ).then(
            fn=build_history_slot_updates,
            inputs=[sessions_state, active_session_id_state],
            outputs=history_outputs,
        )

        demo.load(
            fn=build_history_slot_updates,
            inputs=[sessions_state, active_session_id_state],
            outputs=history_outputs,
        )

    return demo
