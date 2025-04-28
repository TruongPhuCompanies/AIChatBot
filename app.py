import streamlit as st
from streamlit_chat import message
from config import get_odoo_connection, ODOO_DB, ODOO_PASSWORD 
from dao import get_last_week_revenue, get_this_month_revenue
import openai, os
from eda import plot_revenue_by_product

openai.api_key = "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"

common, uid, models = get_odoo_connection()

orders = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'sale.order', 'search_read',
    [[['state', '=', 'sale']]],
    {'fields': ['name', 'amount_total', 'date_order'], 'limit': 10}
)

lines = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'sale.order.line', 'search_read',
    [[['order_id', 'in', [o['id'] for o in orders]]]],
    {'fields': ['product_id', 'price_total', 'order_id']}
)

st.title("🧠 Trợ lý doanh thu (Chatbot)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    message(msg["content"], is_user=msg["role"] == "user")


st.sidebar.title("💡 Gợi ý câu hỏi")
st.sidebar.write(
    """
    - Doanh thu tuần trước là bao nhiêu?
    - Doanh thu tháng này là bao nhiêu?
    - Chiến lược kinh doanh cho tháng tới là gì?
    """
)

from langchain.prompts import PromptTemplate
from langchain.chat_models import init_chat_model

user_input = st.chat_input("Nhập câu hỏi về doanh thu...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    message(user_input, is_user=True)

    try:
        if "tuần trước" in user_input.lower():
            revenue = get_last_week_revenue(orders)
            
            plot = plot_revenue_by_product(lines)
            st.pyplot(plot)
            
            assistant_reply = f"✅ Doanh thu tuần trước là {revenue:,.0f} VND"
        
        elif "tháng này" in user_input.lower():
            revenue = get_this_month_revenue(orders)
            
            plot = plot_revenue_by_product(lines)
            st.pyplot(plot)
            
            assistant_reply = f"🧾 Doanh thu tháng này là {revenue:,.0f} VND"
        elif "chiến lược kinh doanh" in user_input.lower():
            revenue_last_week = get_last_week_revenue(orders)
            revenue_this_month = get_this_month_revenue(orders)
            
            strategy_prompt = PromptTemplate(
                input_variables=["revenue_last_week", "revenue_this_month"],
                template="""
                    Doanh thu tuần trước là {revenue_last_week} VND và doanh thu tháng này là {revenue_this_month} VND.
                    Tỉ lệ so sánh doanh thu.
                    Dựa trên số liệu này, hãy đưa ra chiến lược kinh doanh phù hợp để tăng trưởng doanh thu trong tháng tới.
                    Cung cấp các gợi ý về sản phẩm, kênh bán hàng, và các yếu tố cần tối ưu để đạt được mục tiêu tăng trưởng.
                """
            )

            llm = init_chat_model("gpt-4o-mini", model_provider="openai")
            
            chain = strategy_prompt | llm 
            
            strategy = chain.invoke(
                {"revenue_last_week": revenue_last_week, "revenue_this_month": revenue_this_month}
            )
            
            assistant_reply = f"📊 Chiến lược kinh doanh: \n{strategy.content}"
        else:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "Bạn là trợ lý doanh thu nội bộ, nói tiếng Việt."},
                          {"role": "user", "content": user_input}]
            )
            assistant_reply = response.choices[0].message["content"]

    except Exception as e:
        assistant_reply = f"Đã xảy ra lỗi khi xử lý yêu cầu: {e}"

    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    message(assistant_reply, is_user=False)
