# Isso foi feito via IA

import streamlit as st
import requests

st.set_page_config(page_title="AI Personal Finance Planner", page_icon="💰")
st.title("💰 AI Personal Finance Planner")

income   = st.number_input("Monthly Income (USD)",   min_value=0, step=100, value=3000)
expenses = st.number_input("Fixed Expenses (USD)",   min_value=0, step=100, value=1500)
debt     = st.number_input("Total Debt (USD)",       min_value=0, step=500, value=5000)

if st.button("Generate My Finance Plan ✨"):
    payload = {"income": income, "expenses": expenses, "debt": debt}
    response = requests.post("http://localhost:8000/run", json=payload, timeout=120)
    if response.ok:
        data = response.json()
        st.subheader("📊 Budget")
        st.json(data["budget"])
        st.subheader("🏦 Savings")
        st.json(data["savings"])
        st.subheader("💳 Debt Strategy")
        st.json(data["debt"])
    else:
        st.error("Failed to fetch finance plan. Please try again.")
