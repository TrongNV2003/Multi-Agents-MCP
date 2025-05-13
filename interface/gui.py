import re
import time
import json
import streamlit as st
from loguru import logger

from multi_agents.pipeline import pipeline


st.set_page_config(
    page_title="Agento",
    page_icon="🧊",
    initial_sidebar_state="auto",
)

# Custom CSS
st.markdown("""
    <style>
        .chat-container {
            max-width: 1000px;
            margin: 0 auto;
        }
        .user-message, .bot-message {
            border-radius: 1.5rem;
            padding: .625rem 1.25rem;
            margin: 5px 0;
            display: inline-block;
            max-width: 80%;
        }
        .user-message {
            background-color: rgba(50, 50, 50, .85);
            text-align: right;
            color: white;
            font-size: 18px;
            align-self: flex-end;
        }
        .bot-message {
            background-color: transparent;
            color: white;
            font-size: 18px;
            align-self: flex-start;
        }
        .thinking-step {
            background-color: rgba(80, 80, 80, 0.5);
            padding: 10px;
            border-radius: 1.5rem;
            margin: 5px 0;
            opacity: 0.7;
            max-width: 70%;
        }
        .order-details {
            background-color: rgba(0, 100, 0, 0.5);
            padding: 10px;
            border-radius: 1.5rem;
            margin: 5px 0;
            max-width: 70%;
            color: white;
        }
        .error-step {
            background-color: rgba(255, 0, 0, 0.5);
            padding: 10px;
            border-radius: 1.5rem;
            margin: 5px 0;
            max-width: 70%;
        }
        .chat {
            display: flex;
            flex-direction: column;
        }
        .suggestion-card {
            display: inline-block;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 10px 15px;
            margin: 5px;
            cursor: pointer;
            transition: background-color 0.2s;
            font-size: 14px;
            color: white;
        }
        .suggestion-card:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("# :rainbow[Agento v2]")
st.sidebar.header("Cài đặt")

st.sidebar.subheader("Thông tin khách hàng")
conversation_id = st.sidebar.text_input("Session ID", value="130")
customer_name = st.sidebar.text_input("Tên khách hàng", value="Nguyễn Văn Trọng")
previous_interactions = st.sidebar.text_area("Lịch sử tương tác", value="Đã từng hỏi về iPad Air.")

# show_thoughts = st.sidebar.checkbox("Hiển thị suy luận của agents", value=True)

SUGGESTIONS = [
    "Tư vấn giá iPhone 15 Pro Max cho tôi",
    "iPhone 14 Pro còn hàng không? Giá bao nhiêu?",
    "MacBook Air M2 có những màu nào?",
    "Tôi muốn đặt mua iPhone 15 Pro Max"
]

def strip_ansi(text):
    """Loại bỏ mã ANSI escape từ chuỗi."""
    ansi_regex = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_regex.sub('', text)

def query_processing(query_text, container, context_data):
    steps = []
    final_answer = ""
    order_details = None

    def step_callback(step):
        nonlocal steps, final_answer, order_details
        if step["type"] == "thinking":
            clean_content = strip_ansi(step["content"])
            step["content"] = clean_content
            steps.append(step)
            html_content = ""
            for s in steps:
                if s["type"] == "thinking":
                    agent_name = s.get("agent", "Unknown")
                    html_content += f'<div class="thinking-step">Agent {agent_name}: Suy nghĩ - {s["content"]}</div>'
            # if show_thoughts:
            #     container.markdown(html_content, unsafe_allow_html=True)
            #     time.sleep(0.5)

        elif step["type"] == "final_answer":
            final_answer = strip_ansi(step["content"])
            if step.get("agent") == "Lên đơn hàng":
                try:
                    final_json = json.loads(final_answer) if isinstance(final_answer, str) else final_answer
                    if "order_created" in final_json and final_json["order_created"] and "order_details" in final_json:
                        order_details = final_json["order_details"]
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse final_answer as JSON: {final_answer}")

        elif step["type"] == "error":
            steps.append(step)
            html_content = f'<div class="error-step">Lỗi: {strip_ansi(step["content"])}</div>'
            container.markdown(html_content, unsafe_allow_html=True)
            time.sleep(0.5)

    with st.spinner("Đang xử lý..."):
        result = pipeline(query_text, initial_context_data=context_data, step_callback=step_callback)

    final_answer = strip_ansi(result.get("customer_response", "Không có phản hồi cuối cùng."))
    task3_output = result.get("task3_output", "{}")
    try:
        task3_json = json.loads(task3_output) if isinstance(task3_output, str) else task3_output
        if "order_created" in task3_json and task3_json["order_created"] and "order_details" in task3_json:
            order_details = task3_json["order_details"]
    except json.JSONDecodeError:
        logger.error(f"Failed to parse task3_output as JSON: {task3_output}")

    return final_answer, order_details

def display_order_details(order_details):
    if order_details:
        order_html = (
            f'<div class="order-details">'
            f'<strong>Đơn hàng đã được tạo:</strong><br>'
            f'Mã đơn hàng: {order_details.get("order_id", "N/A")}<br>'
            f'Sản phẩm: {order_details.get("product", "Unknown")}<br>'
            f'Màu sắc: {order_details.get("color", "Unknown")}<br>'
            f'Bộ nhớ: {order_details.get("storage", "Unknown")}<br>'
            f'Số lượng: {order_details.get("quantity", 1)}<br>'
            f'Tổng giá: {order_details.get("total_price", 0):,.0f} VNĐ<br>'
            f'Khách hàng: {order_details.get("customer_info", {}).get("customer_name", "Guest")}<br>'
            f'</div>'
        )
        st.markdown(f'<div class="chat-container"><div class="chat">{order_html}</div></div>', unsafe_allow_html=True)

def main():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        initial_bot_message = "Xin chào! Tôi là Agento. Hôm nay tôi có thể giúp gì cho bạn?"
        st.session_state.chat_history.append({"role": "assistant", "content": initial_bot_message})

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f'<div class="chat"><div class="user-message">{message["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat"><div class="bot-message">{message["content"]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    query_text = st.chat_input("Hỏi Agento điều gì đó...")
    if query_text:
        initial_context = {
            "conversation_id": conversation_id,
            "customer_name": customer_name,
            "previous_interactions": previous_interactions
        }
        st.session_state.chat_history.append({"role": "user", "content": query_text})
        st.markdown(f'<div class="chat-container"><div class="chat"><div class="user-message">{query_text}</div></div></div>', unsafe_allow_html=True)
        
        response_container = st.empty()
        
        final_answer, order_details = query_processing(query_text, response_container, initial_context)

        if order_details:
            display_order_details(order_details)

        if final_answer:
            st.session_state.chat_history.append({"role": "assistant", "content": final_answer})
            st.markdown(
                f'<div class="chat-container"><div class="chat"><div class="bot-message">{final_answer}</div></div></div>',
                unsafe_allow_html=True
            )

def health_check():
    st.sidebar.markdown("---")
    st.sidebar.header("Kiểm tra trạng thái")
    if st.sidebar.button("Kiểm tra trạng thái"):
        st.sidebar.text("Tôi ổn! 👍🏻")

if __name__ == "__main__":
    main()
    health_check()
    
# python -m streamlit run multi_agents/interface/gui.py