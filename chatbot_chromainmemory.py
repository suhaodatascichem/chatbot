# -*- coding: utf-8 -*-
"""chatbot-ChromaInMemory.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1FuJZ856fzTikTwQLTmORJgxvWDubQNSd
"""

import streamlit as st
from langchain.document_loaders import Docx2txtLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline
import transformers
from transformers import pipeline
import tempfile
import os

# Initialize the embedding model
embedding = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Load TinyLLaMA pipeline
llm_pipeline = pipeline(
    "text-generation",
    model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    model_kwargs={"torch_dtype": "auto"},
    max_new_tokens=256,
    temperature=0.7,
    top_p=0.9,
    repetition_penalty=1.1
)

llm = HuggingFacePipeline(pipeline=llm_pipeline)

st.title("📄 Company Document Q&A Chatbot")

uploaded_file = st.file_uploader("Upload a .docx file", type=["docx"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    loader = Docx2txtLoader(tmp_file_path)
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)

    # Use Chroma in-memory
    vectorstore = Chroma.from_documents(docs, embedding, persist_directory=None)

    retriever = vectorstore.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

    query = st.text_input("Ask a question about the document:")

    if query:
        with st.spinner("Thinking..."):
            response = qa_chain.run(query)
        st.markdown(f"**Answer:** {response}")

    os.remove(tmp_file_path)