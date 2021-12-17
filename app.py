import streamlit as st
from Pinecone_index import PineconeIndex
from Controller import Controller

st.write("Hello WOrld!")
url = st.text_input(label="Enter url to Youtube video:")
