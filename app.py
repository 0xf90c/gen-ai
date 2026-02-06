import streamlit as st
import pandas as pd
from agent import ask, SYSTEM
from db import stats,run_query

st.set_page_config(layout="wide")

if "chat" not in st.session_state:
    st.session_state.chat=[{"role":"system","content":"You are helpful"}]

rows,revenue=stats()

left,right=st.columns(2)

with left:
    st.title("Business Info")
    st.metric("Rows",rows)
    st.metric("Total Revenue",revenue)

    chart=run_query("""
      SELECT product,sum(amount) as revenue
      FROM sales GROUP BY product
    """)
    st.bar_chart(chart.set_index("product"))

    st.write("Sample queries:")
    if st.button("Top 5 customers"):
        st.session_state.q="Top 5 customers by revenue"
    if st.button("Sales by region"):
        st.session_state.q="Total sales by region"

with right:
    st.title("Chat")

    for m in st.session_state.chat:
        if m["role"]!="system":
            st.chat_message(m["role"]).write(m["content"])

    q=st.chat_input("Ask...")
    if "q" in st.session_state:
        q=st.session_state.q
        del st.session_state.q

    if q:
        st.session_state.chat.append({"role":"user","content":q})
        st.chat_message("user").write(q)

        st.session_state.chat=ask(st.session_state.chat)
        st.chat_message("assistant").write(
            st.session_state.chat[-1]["content"]
        )

    if st.sidebar.button("Reset chat"):
        st.session_state.chat = [{"role": "system", "content": SYSTEM}]
        st.rerun()

    if "chat" not in st.session_state:
        st.session_state.chat = [{"role": "system", "content": SYSTEM}]