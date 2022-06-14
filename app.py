import streamlit as st

from pinecone_index import PineconeIndex
from controller import Controller

# from bible import BIBLE_BOOK_MAPPING
from utils import *


bible = load_bible()
retriever_model = load_model()
# index = PineconeIndex("qa-index")
index = load_pinecone_index()
controller = Controller(retriever_model, index)

# init session state
if "num_suggested_results_to_display" not in st.session_state:
    st.session_state.num_suggested_results_to_display = 5

st.title("Bible Semantic Search")

query = st.text_input(label="Enter query")
submit = st.button("Search")


if (submit or query) and query != "":
    if "query" not in st.session_state:
        st.session_state.query = query
    # perform keyword search
    # results = full_text_search(bible, query)
    # st.subheader("Full text search results")
    # st.write(
    #     f"Found {len(results)} search {'result' if len(results) == 1 else 'results'} for **{query}**"
    # )
    # for loc, verse in results:
    #     # book_title, chapter_num, and verse_num are all strings
    #     book_title, chapter_num, verse_num = loc.split(":")
    #     st.write(
    #         f"**{BIBLE_BOOK_MAPPING[book_title]} {chapter_num.lstrip('0')}:{verse_num.lstrip('0')}**  - {verse}"
    #     )

    # perform semantic search
    if query != st.session_state.query:
        st.session_state.query = query
        st.session_state.num_suggested_results_to_display = 5
    st.subheader("Semantic search results")
    st.write(
        f"Showing top {st.session_state.num_suggested_results_to_display} most similar results to **{query}**"
    )
    query_results = controller.query(
        query, namespace="bible_KJV", top_k=100, verbose=True
    )

    display_results(
        query,
        query_results,
        num_to_display=st.session_state.num_suggested_results_to_display,
    )
    if st.button(label="More results"):
        # increase num_suggested_results_to_display by 5 (ie show 5 more results than were shown previously)
        st.session_state.num_suggested_results_to_display += 5
        st.experimental_rerun()

with st.expander("Wat this?"):
    st.write(
        "This is a Streamlit app I prototyped for performing semantic search on the King James Bible. It conducts full text search as well as semantic search, which is useful for surfacing passages that are similar in meaning to the query, even if the passages don't explicitly contain the query keyword(s). Suppose you wanted to bring up all verses that reference the infamous snake that tempted Eve. In a traditional keyword search system, searching for 'snake' wouldn't yield any results because the KJV uses the term 'serpent'. A semantic search system would take that 'snake' query and retrieve the relevant verses that contain 'serpent' as well as similar verses like ones about reptiles."
    )
    st.write(
        "Under the hood, I've generated vector embeddings of every verse in the Bible using [SBERT](https://www.sbert.net/), and stored those embeddings in a vector database called [Pinecone](https://www.pinecone.io/). Every time you submit a query, it's converted to its vector representation using SBERT. That query vector is then sent to Pinecone, which performs an [Approximate Nearest Neighbor](https://www.pinecone.io/learn/what-is-similarity-search/#:~:text=millions%20of%20vectors.-,Approximate%20Neighbor%20Search,-To%20reduce%20the) search, retrieving the top __n__ verses that are the most semantically similar to our query. The verses returned are ranked in order of most to least similar. "
    )
