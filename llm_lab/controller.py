import html

import gradio as gr

from llm_lab.state import (
    as_messages,
    build_title_from_prompt,
    default_compare_stats,
    default_single_stats,
    ensure_sessions,
    find_session,
    maybe_update_session_title,
    new_session,
    normalize_image_path,
    replace_session,
    session_choices,
)
from .model_provider import ModelProvider


class ChatController:
    def __init__(self, provider: ModelProvider | None = None):
        self.provider = provider or ModelProvider()

    def model_display(self, model_key):
        return self.provider.model_info[model_key]["display"]

    def estimate_usage(self, history, has_image=False):
        return self.provider.estimate_usage(as_messages(history), has_image=has_image)

    def build_token_html(self, session, active_mode):
        if active_mode == "compare":
            stats = session.get("compare_stats") or default_compare_stats()
            rows = [
                (
                    self.model_display(stats["model_a_key"]),
                    str(stats["usage_a"]),
                ),
                (
                    self.model_display(stats["model_b_key"]),
                    str(stats["usage_b"]),
                ),
            ]
        else:
            stats = session.get("single_stats") or default_single_stats()
            rows = [
                (
                    self.model_display(stats["model_key"]),
                    str(stats["usage"]),
                )
            ]
        return self._build_metric_html("Token 使用量", rows)

    def build_context_html(self, session, active_mode):
        if active_mode == "compare":
            stats = session.get("compare_stats") or default_compare_stats()
            def fmt(u, l):
                pct = (u / l * 100) if l else 0
                return f"{u}/{l} ({pct:.1f}%)"
            rows = [
                (
                    self.model_display(stats["model_a_key"]),
                    fmt(stats["usage_a"], stats["limit_a"]),
                ),
                (
                    self.model_display(stats["model_b_key"]),
                    fmt(stats["usage_b"], stats["limit_b"]),
                ),
            ]
        else:
            stats = session.get("single_stats") or default_single_stats()
            pct = (stats["usage"] / stats["limit"] * 100) if stats["limit"] else 0
            rows = [
                (
                    self.model_display(stats["model_key"]),
                    f'{stats["usage"]}/{stats["limit"]} ({pct:.1f}%)',
                )
            ]
        return self._build_metric_html("上下文占用", rows)

    def _build_metric_html(self, title, rows):
        parts = [f"<div class='metric-title'>{title}</div>"]
        for label, value in rows:
            parts.append(
                "<div class='metric-row'>"
                f"<span class='metric-label'>{html.escape(label)}</span>"
                f"<span class='metric-value'>{html.escape(value)}</span>"
                "</div>"
            )
        return "<div class='metric-card'>" + "".join(parts) + "</div>"

    def build_standard_input_updates(self, model_key):
        multimodal = model_key == "Qwen3.5-Plus"
        return (
            gr.update(visible=multimodal),
            gr.update(visible=not multimodal),
            gr.update(
                placeholder=(
                    "请输入文本或者图片"
                    if multimodal
                    else "请输入文本（图片请切换到 Qwen3.5-Plus）"
                )
            ),
        )

    def _render_session_payload(self, sessions, session, active_mode):
        return (
            sessions,
            session["id"],
            gr.update(choices=session_choices(sessions), value=session["id"]),
            as_messages(session["single_history"]),
            as_messages(session["compare_history_a"]),
            as_messages(session["compare_history_b"]),
            session["single_model_key"],
            session["compare_model_a_key"],
            session["compare_model_b_key"],
            session["temperature"],
            self.build_token_html(session, active_mode),
            self.build_context_html(session, active_mode),
        )

    def on_select_session(self, session_id, sessions, active_mode):
        sessions = ensure_sessions(sessions)
        session = find_session(sessions, session_id) or sessions[0]
        return self._render_session_payload(sessions, session, active_mode)

    def on_new_session(self, sessions, active_mode):
        sessions = ensure_sessions(sessions)
        session = new_session(len(sessions) + 1)
        session["active_mode"] = active_mode
        sessions = [session] + sessions
        return self._render_session_payload(sessions, session, active_mode)

    def on_delete_session_by_id(self, target_session_id, sessions, active_session_id, active_mode):
        sessions = ensure_sessions(sessions)
        if len(sessions) <= 1:
            session = sessions[0]
            session = new_session(1)
            session["id"] = sessions[0]["id"]
            sessions = [session]
            return self._render_session_payload(sessions, session, active_mode)

        sessions = [session for session in sessions if session["id"] != target_session_id]
        next_id = active_session_id
        if target_session_id == active_session_id:
            next_id = sessions[0]["id"]
        session = find_session(sessions, next_id) or sessions[0]
        return self._render_session_payload(sessions, session, active_mode)

    def on_clear_active_session(self, sessions, active_session_id, active_mode):
        sessions = ensure_sessions(sessions)
        session = find_session(sessions, active_session_id) or sessions[0]
        cleared = {
            **session,
            "title": "新对话",
            "single_history": [],
            "compare_history_a": [],
            "compare_history_b": [],
            "single_stats": {
                "model_key": session["single_model_key"],
                "usage": 0,
                "limit": self.provider.model_info[session["single_model_key"]]["context"],
            },
            "compare_stats": {
                "model_a_key": session["compare_model_a_key"],
                "usage_a": 0,
                "limit_a": self.provider.model_info[session["compare_model_a_key"]]["context"],
                "model_b_key": session["compare_model_b_key"],
                "usage_b": 0,
                "limit_b": self.provider.model_info[session["compare_model_b_key"]]["context"],
            },
        }
        sessions = replace_session(sessions, session["id"], cleared)
        return self._render_session_payload(sessions, cleared, active_mode)

    def on_update_single_model(self, model_key, sessions, active_session_id, active_mode):
        sessions = ensure_sessions(sessions)
        session = find_session(sessions, active_session_id) or sessions[0]
        usage = self.estimate_usage(session.get("single_history"))
        updated = {
            **session,
            "single_model_key": model_key,
            "single_stats": {
                "model_key": model_key,
                "usage": usage,
                "limit": self.provider.model_info[model_key]["context"],
            },
        }
        sessions = replace_session(sessions, session["id"], updated)
        return (
            sessions,
            self.build_token_html(updated, active_mode),
            self.build_context_html(updated, active_mode),
        )

    def on_update_compare_models(
        self, model_a_key, model_b_key, sessions, active_session_id, active_mode
    ):
        sessions = ensure_sessions(sessions)
        session = find_session(sessions, active_session_id) or sessions[0]
        usage_a = self.estimate_usage(session.get("compare_history_a"))
        usage_b = self.estimate_usage(session.get("compare_history_b"))
        updated = {
            **session,
            "compare_model_a_key": model_a_key,
            "compare_model_b_key": model_b_key,
            "compare_stats": {
                "model_a_key": model_a_key,
                "usage_a": usage_a,
                "limit_a": self.provider.model_info[model_a_key]["context"],
                "model_b_key": model_b_key,
                "usage_b": usage_b,
                "limit_b": self.provider.model_info[model_b_key]["context"],
            },
        }
        sessions = replace_session(sessions, session["id"], updated)
        return (
            sessions,
            self.build_token_html(updated, active_mode),
            self.build_context_html(updated, active_mode),
        )

    def on_update_temperature(self, temperature, sessions, active_session_id):
        sessions = ensure_sessions(sessions)
        session = find_session(sessions, active_session_id) or sessions[0]
        updated = {**session, "temperature": temperature}
        return replace_session(sessions, session["id"], updated)

    def on_mode_change(self, active_mode, sessions, active_session_id):
        sessions = ensure_sessions(sessions)
        target_session = None

        # Find the most recent session that matches the mode, or is empty
        for s in sessions:
            has_single = len(s.get("single_history", [])) > 0
            has_compare = len(s.get("compare_history_a", [])) > 0
            
            if active_mode == "single" and not has_compare:
                target_session = s
                break
            if active_mode == "compare" and not has_single:
                target_session = s
                break

        if not target_session:
            target_session = new_session(len(sessions) + 1)
            target_session["active_mode"] = active_mode
            sessions = [target_session] + sessions
        else:
            target_session["active_mode"] = active_mode
            sessions = replace_session(sessions, target_session["id"], target_session)

        return self._render_session_payload(sessions, target_session, active_mode)

    def on_disabled_upload_click(self):
        gr.Info("当前模型仅支持文本输入，切换到 Qwen3.5-Plus 后可上传图片。")

    def single_text_submit(self, text, sessions, active_session_id, model_key, temperature):
        message = {"text": text, "files": []}
        yield from self.single_chat_submit(
            message, sessions, active_session_id, model_key, temperature
        )

    def _format_response(self, thinking_text, answer_text, notice=""):
        output = notice
        if thinking_text:
            thinking_block = (
                "<div class='thinking-block'>"
                "<div class='thinking-label'>思考过程</div>"
                f"<div class='thinking-content'>{html.escape(thinking_text).replace(chr(10), '<br>')}</div>"
                "</div>"
            )
            output += thinking_block
        if answer_text:
            output += (
                "<div class='answer-block'>"
                f"{answer_text}"
                "</div>"
            )
        return output

    def single_chat_submit(
        self, message, sessions, active_session_id, model_key, temperature
    ):
        sessions = ensure_sessions(sessions)
        session = find_session(sessions, active_session_id) or sessions[0]
        history = as_messages(session.get("single_history"))

        prompt = ""
        if isinstance(message, dict):
            prompt = (message.get("text") or "").strip()
        image_path = normalize_image_path(message)

        if not prompt and image_path:
            prompt = "请描述这张图片。"

        if not prompt:
            yield (
                gr.update(value={"text": "", "files": []}),
                history,
                self.build_token_html(session, "single"),
                self.build_context_html(session, "single"),
                sessions,
            )
            return

        session = maybe_update_session_title(session, prompt)
        model_info = self.provider.model_info[model_key]
        supports_image = bool(image_path) and bool(model_info.get("multimodal"))
        notice = ""
        if image_path and not supports_image:
            gr.Info("当前模型不支持图片输入，已忽略图片，请切换到 Qwen3.5-Plus。")
            notice = "提示：当前模型不支持图片，已忽略上传图片。请切换到 Qwen3.5-Plus。\n\n"
            image_path = None

        api_messages = history + [
            {
                "role": "user",
                "content": (
                    [
                        {"type": "text", "text": prompt},
                        {"type": "file", "file": {"path": image_path}},
                    ]
                    if supports_image and image_path
                    else prompt
                ),
            }
        ]
        usage = self.provider.estimate_usage(api_messages, has_image=bool(image_path))
        base_history = api_messages + [{"role": "assistant", "content": ""}]

        updated_session = {
            **session,
            "active_mode": "single",
            "single_model_key": model_key,
            "temperature": temperature,
            "single_stats": {
                "model_key": model_key,
                "usage": usage,
                "limit": model_info["context"],
            },
        }
        sessions = replace_session(sessions, session["id"], updated_session)
        token_html = self.build_token_html(updated_session, "single")
        context_html = self.build_context_html(updated_session, "single")
        
        yield (
            gr.update(value={"text": "", "files": []}),
            base_history,
            token_html,
            context_html,
            sessions,
        )

        thinking_text = ""
        answer_text = ""

        try:
            response_gen, _ = self.provider.chat(
                model_key, api_messages, temperature, image_path
            )
            for chunk in response_gen:
                delta = chunk.choices[0].delta
                if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                    thinking_text += delta.reasoning_content
                    current = base_history[:-1] + [
                        {
                            "role": "assistant",
                            "content": self._format_response(
                                thinking_text, answer_text, notice
                            ),
                        }
                    ]
                    updated_session = {**updated_session, "single_history": current}
                    # Update usage estimation
                    updated_session["single_stats"]["usage"] = self.provider.estimate_usage(current)
                    new_token_html = self.build_token_html(updated_session, "single")
                    new_context_html = self.build_context_html(updated_session, "single")
                    sessions = replace_session(
                        sessions, updated_session["id"], updated_session
                    )
                    yield gr.update(), current, new_token_html, new_context_html, sessions
                    continue

                if hasattr(delta, "content") and delta.content:
                    answer_text += delta.content
                    current = base_history[:-1] + [
                        {
                            "role": "assistant",
                            "content": self._format_response(
                                thinking_text, answer_text, notice
                            ),
                        }
                    ]
                    updated_session = {**updated_session, "single_history": current}
                    # Update usage estimation
                    updated_session["single_stats"]["usage"] = self.provider.estimate_usage(current)
                    new_token_html = self.build_token_html(updated_session, "single")
                    new_context_html = self.build_context_html(updated_session, "single")
                    sessions = replace_session(
                        sessions, updated_session["id"], updated_session
                    )
                    yield gr.update(), current, new_token_html, new_context_html, sessions

            final_history = base_history[:-1] + [
                {
                    "role": "assistant",
                    "content": self._format_response(
                        thinking_text, answer_text, notice
                    ),
                }
            ]
            updated_session = {**updated_session, "single_history": final_history}
            updated_session["single_stats"]["usage"] = self.provider.estimate_usage(final_history)
            new_token_html = self.build_token_html(updated_session, "single")
            new_context_html = self.build_context_html(updated_session, "single")
            sessions = replace_session(sessions, updated_session["id"], updated_session)
            yield gr.update(), final_history, new_token_html, new_context_html, sessions

        except Exception as error:
            error_msg = str(error).lower()
            if any(kw in error_msg for kw in ["cancel", "abort", "disconnect", "close", "read"]):
                # If Gradio canceled the generator, ignore and return silently
                return
            error_history = api_messages + [
                {"role": "assistant", "content": f"❌ 发生错误: {str(error)}"}
            ]
            updated_session = {**updated_session, "single_history": error_history}
            sessions = replace_session(sessions, updated_session["id"], updated_session)
            yield gr.update(), error_history, token_html, context_html, sessions

    def compare_chat_submit(
        self, message, sessions, active_session_id, model1_key, model2_key, temperature
    ):
        sessions = ensure_sessions(sessions)
        session = find_session(sessions, active_session_id) or sessions[0]

        text = ""
        if isinstance(message, dict):
            text = (message.get("text") or "").strip()
        else:
            text = (message or "").strip()
            
        if not text:
            yield (
                gr.update(value={"text": "", "files": []}),
                as_messages(session.get("compare_history_a")),
                as_messages(session.get("compare_history_b")),
                self.build_token_html(session, "compare"),
                self.build_context_html(session, "compare"),
                sessions,
            )
            return

        session = maybe_update_session_title(session, text)
        history1 = as_messages(session.get("compare_history_a"))
        history2 = as_messages(session.get("compare_history_b"))
        messages1 = history1 + [{"role": "user", "content": text}]
        messages2 = history2 + [{"role": "user", "content": text}]
        usage_a = self.provider.estimate_usage(messages1)
        usage_b = self.provider.estimate_usage(messages2)

        updated_session = {
            **session,
            "active_mode": "compare",
            "compare_model_a_key": model1_key,
            "compare_model_b_key": model2_key,
            "temperature": temperature,
            "compare_stats": {
                "model_a_key": model1_key,
                "usage_a": usage_a,
                "limit_a": self.provider.model_info[model1_key]["context"],
                "model_b_key": model2_key,
                "usage_b": usage_b,
                "limit_b": self.provider.model_info[model2_key]["context"],
            },
        }
        sessions = replace_session(sessions, session["id"], updated_session)
        token_html = self.build_token_html(updated_session, "compare")
        context_html = self.build_context_html(updated_session, "compare")

        yield (
            gr.update(value={"text": "", "files": []}),
            messages1 + [{"role": "assistant", "content": ""}],
            messages2 + [{"role": "assistant", "content": ""}],
            token_html,
            context_html,
            sessions,
        )

        answer1, answer2 = "", ""
        thinking1, thinking2 = "", ""
        done1, done2 = False, False

        try:
            gen1, _ = self.provider.chat(model1_key, messages1, temperature)
            gen2, _ = self.provider.chat(model2_key, messages2, temperature)

            while not (done1 and done2):
                if not done1:
                    try:
                        chunk1 = next(gen1)
                        delta1 = chunk1.choices[0].delta
                        if hasattr(delta1, "reasoning_content") and delta1.reasoning_content:
                            thinking1 += delta1.reasoning_content
                        elif hasattr(delta1, "content") and delta1.content:
                            answer1 += delta1.content
                    except StopIteration:
                        done1 = True

                if not done2:
                    try:
                        chunk2 = next(gen2)
                        delta2 = chunk2.choices[0].delta
                        if hasattr(delta2, "reasoning_content") and delta2.reasoning_content:
                            thinking2 += delta2.reasoning_content
                        elif hasattr(delta2, "content") and delta2.content:
                            answer2 += delta2.content
                    except StopIteration:
                        done2 = True

                out1 = messages1 + [
                    {
                        "role": "assistant",
                        "content": self._format_response(thinking1, answer1),
                    }
                ]
                out2 = messages2 + [
                    {
                        "role": "assistant",
                        "content": self._format_response(thinking2, answer2),
                    }
                ]
                updated_session = {
                    **updated_session,
                    "compare_history_a": out1,
                    "compare_history_b": out2,
                }
                updated_session["compare_stats"]["usage_a"] = self.provider.estimate_usage(out1)
                updated_session["compare_stats"]["usage_b"] = self.provider.estimate_usage(out2)
                new_token_html = self.build_token_html(updated_session, "compare")
                new_context_html = self.build_context_html(updated_session, "compare")
                sessions = replace_session(sessions, updated_session["id"], updated_session)
                yield gr.update(), out1, out2, new_token_html, new_context_html, sessions

            yield gr.update(), out1, out2, new_token_html, new_context_html, sessions

        except Exception as error:
            error_msg = str(error).lower()
            if any(kw in error_msg for kw in ["cancel", "abort", "disconnect", "close", "read"]):
                return
            error1 = messages1 + [
                {"role": "assistant", "content": f"❌ 模型 A 发生错误: {str(error)}"}
            ]
            error2 = messages2 + [
                {"role": "assistant", "content": f"❌ 模型 B 发生错误: {str(error)}"}
            ]
            updated_session = {
                **updated_session,
                "compare_history_a": error1,
                "compare_history_b": error2,
            }
            sessions = replace_session(sessions, updated_session["id"], updated_session)
            yield gr.update(), error1, error2, token_html, context_html, sessions
