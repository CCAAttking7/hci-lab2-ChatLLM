APP_CSS = """
:root {
  --bg-main: #f3f4f8;
  --bg-panel: rgba(255, 255, 255, 0.62);
  --bg-panel-strong: rgba(255, 255, 255, 0.82);
  --bg-hover: rgba(255, 255, 255, 0.92);
  --text-main: #1f2937;
  --text-soft: #667085;
  --text-faint: #98a2b3;
  --line-soft: rgba(15, 23, 42, 0.08);
  --line-strong: rgba(15, 23, 42, 0.12);
  --accent: #6e7bf2;
  --accent-soft: rgba(110, 123, 242, 0.12);
  --danger: #dd5d5d;
  --shadow-soft: 0 16px 40px rgba(15, 23, 42, 0.08);
}

html, body, .gradio-container {
  height: 100%;
  overflow: hidden !important;
  background:
    radial-gradient(circle at top left, rgba(120, 138, 255, 0.12), transparent 28%),
    radial-gradient(circle at top right, rgba(91, 182, 255, 0.10), transparent 24%),
    linear-gradient(180deg, #f6f7fb 0%, #eef1f6 100%);
  color: var(--text-main);
}

.gradio-container {
  padding: 12px !important;
}

.gradio-container > .main {
  height: 100%;
}

#app-shell {
  height: 100%;
  max-height: calc(100vh - 30px);
  gap: 12px;
  align-items: stretch !important;
}

#sidebar-shell,
#main-shell {
  height: 100%;
  border: 1px solid var(--line-soft);
  border-radius: 24px;
  background: var(--bg-panel);
  box-shadow: var(--shadow-soft);
  backdrop-filter: blur(22px);
  -webkit-backdrop-filter: blur(22px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

#main-shell > div {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

#sidebar-shell {
  padding: 14px 12px 12px;
  gap: 8px;
  background:
    linear-gradient(180deg, rgba(255,255,255,0.78), rgba(246,247,251,0.58)),
    rgba(255,255,255,0.55);
}

#main-shell {
  padding: 14px 16px;
}

#standard-model-row,
#compare-model-row {
  align-items: flex-start !important;
  flex: 0 0 auto !important;
  gap: 10px;
  margin-bottom: 0 !important;
}
#standard-model-row > div,
#compare-model-row > div {
  margin-bottom: 0 !important;
  padding-bottom: 0 !important;
}
#standard-model-row .wrap,
#compare-model-row .wrap {
  box-shadow: none !important;
}

#history-header-row,
#history-actions-row,
#standard-text-row,
#standard-multimodal-row,
#compare-input-row,
#compare-chat-row {
  gap: 10px;
}

#history-scroll {
  flex: 1 1 0% !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  padding-right: 4px;
  min-height: 0 !important;
  display: block !important;
}

.sidebar-title-md {
  flex: 0 0 auto !important;
  margin-bottom: 0 !important;
  padding-bottom: 0 !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
.sidebar-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-soft);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin: 2px 2px 4px;
}

#history-scroll::-webkit-scrollbar,
.chatbot-container::-webkit-scrollbar {
  width: 8px;
}

#history-scroll::-webkit-scrollbar-thumb,
.chatbot-container::-webkit-scrollbar-thumb {
  background: rgba(152, 162, 179, 0.5);
  border-radius: 999px;
}

.history-item-wrap {
  display: flex;
  align-items: center;
  position: relative;
  margin-bottom: 2px;
  background: transparent;
  border-radius: 8px;
  border: none;
  transition: background 0.15s ease;
}

.history-item-wrap:hover {
  background: rgba(0, 0, 0, 0.04);
}

.new-chat-btn {
  flex: 0 0 auto !important;
  margin-top: 0 !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}
.new-chat-btn button {
  background: transparent !important;
  color: var(--text-main) !important;
  font-weight: 500 !important;
  font-size: 14px !important;
  padding: 8px 12px !important;
  border-radius: 8px !important;
  border: 1px solid rgba(0,0,0,0.1) !important;
  box-shadow: none !important;
  min-height: 36px !important;
  max-height: 36px !important;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  flex: 0 0 auto !important;
}
.new-chat-btn button:hover {
  background: rgba(0,0,0,0.03) !important;
}

.clear-chat-btn,
.send-soft-btn {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}
.clear-chat-btn button,
.send-soft-btn button {
  border-radius: 16px !important;
  border: 1px solid var(--line-soft) !important;
  background: rgba(255, 255, 255, 0.55) !important;
  box-shadow: none !important;
}

.history-item-wrap:last-child {
  margin-bottom: 0;
}

.history-item-button {
  flex: 1 !important;
  min-width: 0 !important;
}

.history-item-button button {
  justify-content: flex-start !important;
  text-align: left !important;
  width: 100%;
  padding: 8px 36px 8px 12px !important;
  color: var(--text-main) !important;
  font-size: 13px !important;
  font-weight: 400 !important;
  min-height: 36px !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-item-wrap.active {
  background: rgba(0, 0, 0, 0.08) !important;
}

.history-item-wrap.active .history-item-button button {
  color: #111 !important;
  font-weight: 600 !important;
}

.history-delete {
  position: absolute !important;
  right: 4px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  width: auto !important;
  min-width: 0 !important;
}

.history-delete button {
  min-width: 28px !important;
  width: 28px !important;
  height: 28px !important;
  padding: 0 !important;
  border-radius: 8px !important;
  border: none !important;
  background: transparent !important;
  color: rgba(31, 41, 55, 0.35) !important;
  font-size: 16px !important;
  font-weight: 400 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  opacity: 0;
  transition: opacity 0.2s ease, background 0.2s ease, color 0.2s ease !important;
}

.history-item-wrap:hover .history-delete button {
  opacity: 1;
}

.history-delete button:hover {
  color: var(--danger) !important;
  background: rgba(221, 93, 93, 0.12) !important;
}

.clear-chat-btn button {
  min-height: 34px !important;
  padding: 6px 10px !important;
  color: var(--text-soft) !important;
  background: rgba(255,255,255,0.4) !important;
}

.sidebar-bottom {
  border-top: 1px solid var(--line-soft);
  padding-top: 10px;
  gap: 6px;
  flex: 0 0 auto !important;
  margin-top: 2px;
  display: flex;
  flex-direction: column;
}

.metrics-html {
  min-height: 0;
  margin-top: -4px;
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
}
.metrics-html:empty {
  display: none;
}

.metric-card {
  border-radius: 12px;
  border: 1px solid var(--line-soft);
  background: rgba(255, 255, 255, 0.78);
  padding: 8px 10px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.45);
}

.metric-title {
  color: var(--text-soft);
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 4px;
}

.metric-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 12px;
  line-height: 1.4;
}

.metric-label {
  color: var(--text-soft);
  flex: 1;
}

.metric-value {
  color: var(--text-main);
  font-weight: 600;
  white-space: nowrap;
}

.compact-slider {
  margin-top: 0;
  margin-bottom: 0;
  background: transparent !important;
  border: none !important;
  padding: 0 4px !important;
  box-shadow: none !important;
}

.model-tip {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  color: var(--text-faint);
  font-size: 11px;
  white-space: nowrap;
  justify-content: flex-end;
  text-align: right;
}

.model-tip-active {
  color: #5e69d5;
}

.input-shell {
  border-radius: 18px !important;
  border: 1px solid var(--line-soft) !important;
  background: rgba(255, 255, 255, 0.72) !important;
  box-shadow: none !important;
  padding: 2px 4px !important;
}

.input-shell:focus-within,
#standard-multimodal-row:focus-within {
  border-color: rgba(110, 123, 242, 0.22) !important;
  box-shadow: 0 0 0 4px rgba(110, 123, 242, 0.06) !important;
}

#standard-text-inner {
  gap: 4px;
  align-items: center !important;
}

.upload-fake-btn button {
  min-width: 34px !important;
  width: 34px !important;
  height: 34px !important;
  color: rgba(31, 41, 55, 0.26) !important;
  font-size: 13px !important;
  font-weight: 400 !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}

.upload-fake-btn button:hover {
  background: rgba(110, 123, 242, 0.06) !important;
  color: rgba(31, 41, 55, 0.40) !important;
}

.send-soft-btn button {
  background: linear-gradient(180deg, #7481f5, #6873ea) !important;
  color: white !important;
  border: none !important;
  font-weight: 600 !important;
  min-height: 44px !important;
}

.chat-panel,
.chat-panel > div {
  height: 100%;
  min-height: 0;
}

.chat-panel .message-wrap,
.chat-panel .bubble-wrap {
  max-width: 92%;
}

.chatbot-container {
  overflow: auto !important;
}

.thinking-block {
  margin-bottom: 10px;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(148, 163, 184, 0.10);
  border: 1px solid rgba(148, 163, 184, 0.14);
}

.thinking-label {
  font-size: 12px;
  color: var(--text-faint);
  margin-bottom: 6px;
}

.thinking-content {
  font-size: 13px;
  color: rgba(31, 41, 55, 0.58);
  line-height: 1.65;
}

.answer-block {
  color: var(--text-main);
}

.compact-slider .wrap {
  padding-top: 0 !important;
}

.compact-slider .svelte-1gfkn6j {
  min-height: 34px !important;
}

#standard-model-row,
#compare-model-row {
  flex: 0 0 auto;
}

#standard-multimodal-row,
#standard-text-row,
#compare-input-row {
  align-items: end !important;
  padding-top: 4px;
}

#standard-text-row {
  gap: 8px;
}

#standard-model-row {
  margin-bottom: 4px;
}

#compare-model-row {
  margin-bottom: 6px;
}

#standard-multimodal-row {
  border-radius: 18px;
  border: 1px solid var(--line-soft);
  background: rgba(255, 255, 255, 0.72);
  padding: 2px 2px 2px 6px;
}

#main-shell .chat-panel .message-wrap {
  max-width: 88%;
}

#standard-text-shell textarea,
#standard-text-shell input,
#compare-input-row textarea,
#compare-input-row input,
#standard-multimodal-row textarea,
#standard-multimodal-row input {
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
}

#standard-multimodal-row button[aria-label*="Upload"],
#standard-multimodal-row button[title*="Upload"],
#standard-multimodal-row button[aria-label*="upload"],
#standard-multimodal-row button[title*="upload"] {
  opacity: 0.58 !important;
}

#standard-multimodal-row .submit-button,
#standard-multimodal-row button[aria-label*="Submit"],
#standard-multimodal-row button[title*="Submit"] {
  display: none !important;
}
"""
