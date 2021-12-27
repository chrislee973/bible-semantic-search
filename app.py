import json
import streamlit as st
from Pinecone_index import PineconeIndex
from Controller import Controller
from TextFile import TextFile, BIBLE_BOOK_MAPPING

from sentence_transformers import SentenceTransformer


@st.cache(allow_output_mutation=True)
def load_model():
    retriever_model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
    return retriever_model


@st.cache(suppress_st_warning=True)
def load_bible():
    st.write("hello world")
    bible = TextFile("Bible_KJV.txt")
    return bible


bible = load_bible()
retriever_model = load_model()
index = PineconeIndex('qa-index')
controller = Controller(retriever_model, index)

st.title("Bible Semantic Search")
query = st.text_input(label="Enter query:")
submit = st.button("Search")

if submit or query:
    # perform full text search with get_sents() method
    results = bible.get_verses(query=query)
    st.write(f"Found {len(results)} search results")
    for loc, verse in results:
        # book_title, chapter_num, and verse_num are all strings
        book_title, chapter_num, verse_num = loc.split(":")
        st.write(
            f"**{BIBLE_BOOK_MAPPING[book_title]} {chapter_num.lstrip('0')}:{verse_num.lstrip('0')}**  - {verse}")

    # perform semantic searc
    st.write("Suggested results")
    query_results = controller.query(
        query, namespace="bible_KJV", verbose=True)
    st.write(query_results)
    for res in query_results:
        st.write(
            f"**{res['metadata']['book_title']} {res['metadata']['chapter_num'].lstrip('0')}:{res['metadata']['verse_num'].lstrip('0')}**  - {res['metadata']['context']}")
st.write(controller.list_namespaces())
