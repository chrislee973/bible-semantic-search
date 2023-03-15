import streamlit as st
import re
from sentence_transformers import SentenceTransformer

from pinecone_index import PineconeIndex
from bible import Bible


def query_in_context(query, context):
    """
    Returns whether the query is contained in the context
    """
    query = query.lower().strip()
    return re.search(rf"\b{query}", context.lower())


@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def full_text_search(bibleObj: Bible, query):
    return bibleObj.get_verses(query)


@st.cache(allow_output_mutation=True)
def load_model():
    retriever_model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
    return retriever_model


@st.cache(allow_output_mutation=True)
def load_pinecone_index():
    index = PineconeIndex("qa-index-recovered")
    return index


@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def load_bible():
    # bible = Bible("Bible_KJV.txt")
    bible = Bible("Bible_KJV.txt")
    return bible


def display_results(query, query_results, num_to_display=5):
    """
    Displays the Pinecone search results
    """
    # iterate through the results
    i = 0
    for res in query_results:
        if i >= num_to_display:
            break
        book_title = res["metadata"]["book_title"]
        chapter_num = res["metadata"]["chapter_num"].lstrip("0")
        verse_num = res["metadata"]["verse_num"].lstrip("0")
        context = res["metadata"]["context"]
        similarity_score = res["score"]
        # if the query is contained in the result, skip it and return the next result, because it will already have been returned in the full-text search results
        if query_in_context(query, context):
            continue

        st.write(f"**{book_title} {chapter_num}:{verse_num}**  - {context}")
        i += 1
