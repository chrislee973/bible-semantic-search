import json
import re
import streamlit as st
from Pinecone_index import PineconeIndex
from Controller import Controller
from TextFile import TextFile, BIBLE_BOOK_MAPPING

from sentence_transformers import SentenceTransformer


# UTILS

def query_in_context(query, context):
    """
    Returns whether the query is contained in the context
    """
    query = query.lower().strip()
    return re.search(fr'\b{query}', context.lower())


def callback():
    st.write("you pressed me")


@st.cache(allow_output_mutation=True)
def load_model():
    retriever_model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
    return retriever_model


@st.cache(suppress_st_warning=True)
def load_bible():
    bible = TextFile("Bible_KJV.txt")
    return bible


def display_results(query_results, num_to_display=5):
    """
    Displays the Pinecone search results to the screen
    """
    # iterate through the results
    i = 0
    for res in query_results:
        if i > num_to_display:
            break

        book_title = res['metadata']['book_title']
        chapter_num = res['metadata']['chapter_num'].lstrip('0')
        verse_num = res['metadata']['verse_num'].lstrip('0')
        context = res['metadata']['context']
        # if the query is contained in the result, skip it and return the next result, because it will already have been returned in the full-text search results
        if query_in_context(query, context):
            continue

        st.write(
            f"**{book_title} {chapter_num}:{verse_num}**  - {context}")
        i += 1


##### MAIN ##################
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
    st.write(
        f"Found {len(results)} search {'result' if len(results) == 1 else 'results'}")
    for loc, verse in results:
        # book_title, chapter_num, and verse_num are all strings
        book_title, chapter_num, verse_num = loc.split(":")
        st.write(
            f"**{BIBLE_BOOK_MAPPING[book_title]} {chapter_num.lstrip('0')}:{verse_num.lstrip('0')}**  - {verse}")

    # perform semantic searc
    st.write("Suggested results")
    query_results = controller.query(
        query, namespace="bible_KJV", top_k=100, verbose=True)

    display_results(query_results, num_to_display=5)

    # def display_results(query_results, num_to_display=5):
    #     """
    #     Displays the Pinecone search results to the screen
    #     """
    #     # iterate through the results
    #     i = 0
    #     for res in query_results:
    #         if i > num_to_display:
    #             break

    #         book_title = res['metadata']['book_title']
    #         chapter_num = res['metadata']['chapter_num'].lstrip('0')
    #         verse_num = res['metadata']['verse_num'].lstrip('0')
    #         verse_text = res['metadata']['context']
    #         # if the query is contained in the result, skip it and return the next result, because it will already have been returned in the full-text search results
    #         if query_in_context(query, verse_text):
    #             continue

    #         st.write(
    #             f"**{res['metadata']['book_title']} {res['metadata']['chapter_num'].lstrip('0')}:{res['metadata']['verse_num'].lstrip('0')}**  - {res['metadata']['context']}")
    #         i += 1

    if st.button(label="More results"):
        display_results(query_results, num_to_display=10)
