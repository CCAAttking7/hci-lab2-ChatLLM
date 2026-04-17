import uuid


def default_single_stats():
    return {
        "model_key": "DeepSeek-R1",
        "usage": 0,
        "limit": 128000,
    }


def default_compare_stats():
    return {
        "model_a_key": "DeepSeek-R1",
        "usage_a": 0,
        "limit_a": 128000,
        "model_b_key": "Qwen3-Max",
        "usage_b": 0,
        "limit_b": 262144,
    }


def new_session(index: int):
    sid = str(uuid.uuid4())
    return {
        "id": sid,
        "title": "新对话",
        "single_history": [],
        "compare_history_a": [],
        "compare_history_b": [],
        "single_model_key": "DeepSeek-R1",
        "compare_model_a_key": "DeepSeek-R1",
        "compare_model_b_key": "Qwen3-Max",
        "temperature": 0.8,
        "active_mode": "single",
        "single_stats": default_single_stats(),
        "compare_stats": default_compare_stats(),
    }


def ensure_sessions(sessions):
    if not sessions:
        return [new_session(1)]
    return sessions


def session_choices(sessions):
    return [(session["title"], session["id"]) for session in sessions]


def find_session(sessions, session_id):
    for session in sessions:
        if session["id"] == session_id:
            return session
    return None


def replace_session(sessions, session_id, new_session_data):
    output = []
    for session in sessions:
        if session["id"] == session_id:
            output.append(new_session_data)
        else:
            output.append(session)
    return output


def normalize_image_path(message):
    if not isinstance(message, dict):
        return None
    files = message.get("files") or []
    if not files:
        return None
    file_item = files[0]
    if isinstance(file_item, str):
        return file_item
    if isinstance(file_item, dict) and "path" in file_item:
        return file_item["path"]
    if hasattr(file_item, "path"):
        return file_item.path
    return str(file_item)


def as_messages(history):
    if not history:
        return []
    output = []
    for item in history:
        if isinstance(item, dict) and "role" in item and "content" in item:
            output.append({"role": item["role"], "content": item["content"]})
            continue
        if isinstance(item, (list, tuple)) and len(item) == 2:
            user_text, assistant_text = item
            output.append({"role": "user", "content": user_text})
            output.append({"role": "assistant", "content": assistant_text})
    return output


def token_status(usage: int, limit: int):
    ratio = min(max(usage / limit, 0.0), 1.0) if limit else 0.0
    return f"Token: {usage}/{limit}", ratio


def build_title_from_prompt(prompt: str):
    compact = " ".join((prompt or "").split())
    if not compact:
        return "新对话"
    return compact[:14] + ("…" if len(compact) > 14 else "")


def maybe_update_session_title(session, prompt: str):
    if as_messages(session.get("single_history")) or as_messages(
        session.get("compare_history_a")
    ):
        return session
    return {**session, "title": build_title_from_prompt(prompt)}


def clear_multimodal():
    return {"text": "", "files": []}


def clear_text():
    return ""


def initial_sessions():
    sessions = [new_session(1)]
    return sessions, sessions[0]["id"]
