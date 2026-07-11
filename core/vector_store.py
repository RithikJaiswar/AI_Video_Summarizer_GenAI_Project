import os
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

CHROMA_DIR = 'vector_db'
COLLECTION_NAME = 'meeting_transcript' 
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

def get_embedding():
    return HuggingFaceEmbeddings(
        model_name= EMBEDDING_MODEL,
        model_kwargs = {'device':'cpu'}

    )

# Create Vector Store 
def build_vector_store(transcript:str)->Chroma:
    print('Building Vector Store')

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_text(transcript)

    docs = [
        Document(page_content=chunks,metadata= {'chunk_index': i })
        for i,chunk in enumerate(chunks) 
    ]

    embeddings = get_embedding()
    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR
    )

    return vector_store

# Load a vector store 
def load_vector_store()->Chroma:
    embeddings= get_embedding()
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR        
    )

    return vector_store

def get_retriever(vector_store:Chroma,k:int=4):
    return vector_store.as_retriever(
        search_type = 'similarity',
        search_kwargs = {
            'k' : k
        }
    )