import streamlit as st
from rag.retriever import get_relevant_chunks
from rag.qa import answer_question

def render_follow_up_qa(transcript: dict):
    st.markdown("### <span style='color: black;'>Follow-up Questions</span>", unsafe_allow_html=True)

    all_chunks = transcript["presentation"] + transcript["qa"]
    transcript_metadata = {
        "Company": transcript["Company"],
        "Year": transcript["Year"],
        "Quarter": transcript["Quarter"]
    }

    transcript_id = f"{transcript['Company']}_{transcript['Year']}_Q{transcript['Quarter']}"

    if st.session_state.get("current_transcript") != transcript_id:
        st.session_state.messages = []
        st.session_state.current_transcript = transcript_id

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if query := st.chat_input("Ask a question about this earnings call..."):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("Searching transcript..."):
                documents, metadatas = get_relevant_chunks(
                    transcript_metadata,
                    all_chunks,
                    query
                )
                answer = answer_question(query, documents, metadatas)
            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})