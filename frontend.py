import streamlit as st
import requests

SEARCH_API_URL = "http://127.0.0.1:8000/search/"
ASK_API_URL = "http://127.0.0.1:8000/ask/"

st.title("💬 COVID-19 FAQ Assistant")

# User Input for Initial Query
query = st.text_input("Ask a question:", "")

if st.button("Search"):
    with st.spinner("Searching..."):
        response = requests.get(SEARCH_API_URL, params={"query": query})
        
        if response.status_code == 200:
            data = response.json()
            st.subheader("🔎 Relevant FAQ:")
            for i, faq in enumerate(data["faqs"]):
                st.write(f"**{i+1}.** {faq}")
        else:
            st.error("Error retrieving FAQs. Please try again.")

# User Input for Follow-up Question
f_query = st.text_input("Ask a follow-up question:", "")

if st.button("Ask"):
    with st.spinner("Generating Answer..."):
        response = requests.get(ASK_API_URL, params={"query": query, "f_query": f_query})

        if response.status_code == 200:
            data = response.json()
            st.subheader("🤖 AI Answer:")
            st.write(data["answer"])
        else:
            st.error("Error generating answer. Please try again.")

