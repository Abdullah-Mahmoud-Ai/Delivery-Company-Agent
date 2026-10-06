import streamlit as st
from dotenv import load_dotenv

from agent import create_agent_deps, shipping_agent


load_dotenv()




st.set_page_config(
    page_title="مساعد شركة توصيل",
    page_icon="🚚",
    layout="wide",

)

st.markdown(

      """

<style>
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: "Tahoma", "Arial", sans-serif;
    }

    div[data-testid="stCaptionContainer"] {
        direction: rtl;
        text-align: right;
    }

    .stChatMessage {
        direction: rtl;
        text-align: right;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stChatInput textarea {
        direction: rtl;
        text-align: right;
    }

    section[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }

    div[data-testid="stMarkdownContainer"] {
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True,


)


st.title("🚚 مساعد عمليات شركة التوصيل")
st.caption("وكيل ذكي داخلي يساعد الإدارة على متابعة الشحنات، التأخير، المرتجعات، المدفوعات، وأداء الفروع.")

with st.sidebar:
    st.header("إعدادات الوكيل")

    st.divider()

    st.subheader("أمثلة جاهزة")
    example_questions = [
             "أعطني ملخصًا تنفيذيًا عن وضع الشركة.",
                     "كم عدد الشحنات المتأخرة؟ وما الإجراء المقترح؟",
                     "ما الفروع التي تحتاج متابعة تشغيلية؟",
                     "ما ملخص المدفوعات؟ وهل توجد مشكلة مالية؟",
                     "جهز رسالة متابعة للفرع الأكثر تأخيرًا.",

    ]


    selected_examples = st.radio(

        "اختر سؤالا للتجربة",
        options=example_questions,
        index=None
    )

    if st.button("استخدام السؤال"):
        if selected_examples:
            st.session_state.pending_question = selected_examples

if "messages" not in st.session_state:
    st.session_state.messages = []


if "pending_question" not in st.session_state:
    st.session_state.pending_question = None



def render_answer(output):
    st.markdown("### الإجابة ")
    st.write(output.answer)

    if output.key_metrics:
        st.markdown(" ### المؤشرات المهمة ")
        for metric in output.key_metrics:
            with st.container(border=True):
                st.markdown(f"**{metric.name}**")
                st.write(metric.value)
                st.caption(metric.meaning)



    if output.operational_insights:
        st.markdown("### التنبيهات التشغيلية")
        for insight in output.operational_insights:
            with st.container(border=True):
                st.markdown(f"**{insight.title}**")
                st.write(f"درجة الأهمية: `{insight.severity}`")
                st.write(f"الدليل: {insight.evidence}")
                st.write(f"السبب المحتمل: {insight.possible_cause}")
                st.write(f"الإجراء المقترح: {insight.recommended_action}")

    if output.proposed_actions:
        st.markdown("### الإجراءات المقترحة")
        for action in output.proposed_actions:
            with st.container(border=True):
                st.markdown(f"** نوع الإجراء:**  `{action.action_type}`")
                st.write(action.description)
                st.write(
                    "يحتاج موافقة بشرية:" 
                    + ("نعم" if action.requires_human_approval else "لا")

                )

    if output.draft_messages:
        st.markdown("### مسودات الرسائل")
        for draft in output.draft_messages:
            with st.container(border=True):
                st.markdown(f"** الجهة:** {draft.target}")
                st.markdown(f"**سبب المتابعة:** {draft.reason}")
                st.markdown("**نص الرسالة**")
                st.write(draft.message)
                st.write(
                    "تحتاج موافقة بشرية: "
                    + ("نعم" if draft.requires_human_approval else "لا")
                )


    if output.used_data_sources:
        with st.expander("مصادر البيانات المستخدمة:"):
            for source in output.used_data_sources:
                st.write(f"-{source}")




for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.write(message["content"])

        else:
            render_answer(message["content"])



question = st.chat_input("اكتب سؤالك هنا...")


if st.session_state.pending_question:
    question = st.session_state.pending_question
    st.session_state.pending_question = None

if question:
    st.session_state.messages.append({"role":"user","content":question})

    with st.chat_message("user"):
        st.write(question)


    deps = create_agent_deps()

    with st.chat_message("assistant"):
        with st.spinner("جاري تحليل البيانات والاتصال بال API..."):
            result = shipping_agent.run_sync(question, deps=deps)
            render_answer(result.output)


    st.session_state.messages.append({"role": "assistant", "content":result.output})


